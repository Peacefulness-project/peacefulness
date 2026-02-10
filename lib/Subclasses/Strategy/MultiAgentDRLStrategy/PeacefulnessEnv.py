# Imports
import functools
from pettingzoo import ParallelEnv
from gymnasium.spaces import Box
from gymnasium.utils import seeding
import numpy as np
from importlib import import_module
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import *
from random import setstate
from datetime import datetime
import uuid


class PeacefulnessEnv(ParallelEnv):
    metadata = {"name": "custom_env_v0", }

    def __init__(self, path_to_case: str, world_name: str, start_time: datetime, hours_to_simulate: int, export_path: str, agent_dict: Dict, objective_dict: Dict, normalization_dict: Dict={}, metrics: List=[], std_dev:float=0.25, verbose=False, red_dof_dict=None):
        """
        :param path_to_case: the path to the case study
        :param hours_to_simulate: defines the length of each episode of training
        :param export_path: where to find the logs of the dataloggers
        :param agent_dict: dict with keys "RL_agent_ID" with values as dict of "aggregator_name" and values ("obs_size", "action") and "nb_exchanges"
        :param normalization_dict: used to normalize states
        :param objective_dict: used to identify which reward function to apply (and for which agent)
        :param metrics: list of metrics used to compute the reward
        :param std_dev: by default it is set to 25% of noise to validation data
        :param verbose:
        :param red_dof_dict: if we apply 1-degree less of freedom per agent, a dict should be defined.
        """
        # Defining the possible agents
        self.possible_agents = list(agent_dict.keys())
        self.obs_size, self.action_size = self.get_my_dicts(agent_dict, red_dof_dict)  # getting the size of observation and action for each RL agent

        # Defining the reward function to use
        self._identify_reward(objective_dict)

        # Normalization parameters
        self.normalization_parameters = normalization_dict  # can be given per RL agent or global

        # Needed for the observation and for the step method
        self.independent_aggregators_list = []
        self.independent_agents_list = []
        self.action_dict_per_agent = get_correct_action_dict(agent_dict)  # useful to correctly distribute the actions to their corresponding RL agent (original length without reduction)
        self.red_dof_dict = red_dof_dict  # None if no degree of freedom is reduced

        # Used to retrieve the correct case study
        path_to_case = correct_path(path_to_case)
        self.case_study = import_module(path_to_case)  # we import the case study
        self.world_name = world_name
        self.world_start = start_time
        self.episode_length = hours_to_simulate
        self.dataloggers_path = export_path
        self.metrics = metrics
        self.std_dev = std_dev
        self.verbose = verbose
        self.grid = None
        self.ended_episode = False
        self.env_id = uuid.uuid4().hex


    def reset(self, seed=None, options=None):
        """
        Initialize the environment and RL agents at the start of each episode of training.
        """
        # Seeding
        if seed is not None:
            seed = int(seed) % (2 ** 32)
        self.np_random, self.np_random_seed = seeding.np_random(seed)
        self.np_random_seed = int(self.np_random_seed) % (2 ** 32)

        # Defining the RL agents present
        self.agents = self.possible_agents[:]

        # The final operation of the Peacefulness world at the end of each episode
        if self.ended_episode:
            self.final_grid_operation()
            self.ended_episode = False

        # Retrieving the Peacefulness world
        red_dof_flag = False if self.red_dof_dict is None else True
        self.dataloggers_path += "/" + f"run_{self.env_id}_seed_{self.np_random_seed}"
        self.grid = self.case_study.create_simulation(self.world_name, self.world_start, self.episode_length, self.dataloggers_path, self.metrics, self.np_random_seed, self.std_dev, red_dof_flag)  # the Peacefulness World
        self.initial_grid_operation()  # Initial operation at the start of each episode

        # In case we remove 1-degree of freedom per aggregator
        if self.red_dof_dict is not None:
            for agent in self.red_dof_dict:
                for agg in self.red_dof_dict[agent]:
                    if f"Action removed for {agg}" not in self.grid._catalog.keys:  # Energy_Consumption, Energy_Production, Energy_Storage, Energy_Exchange, Energy_Conversion
                        self.grid._catalog.add(f"Action removed for {agg}", self.red_dof_dict[agent][agg])
                    else:
                        self.grid._catalog.set(f"Action removed for {agg}", self.red_dof_dict[agent][agg])

        observations = self._get_obs()  # The observation of each RL agent
        infos = self._get_infos()

        return observations, infos

    def _get_infos(self):
        info = {agent: {} for agent in self.agents}
        return info

    def _get_obs(self):
        """
        We perform the instructions the same way in original Peacefulness "World.start" method, except we don't loop.
        """
        # Resolution
        # ###########################
        # Beginning of the turn
        # ###########################
        if self.verbose:
            print(f"Start of the iteration {self.grid._catalog.get('simulation_time')}")

        # reinitialization of values in the catalog
        # these values are, globally, the money and energy balances
        for nature in self.grid._catalog.natures.values():
            nature.reinitialize()

        for strategy in self.grid._catalog.strategies.values():
            strategy.reinitialize()

        for agent in self.grid._catalog.agents.values():
            agent.reinitialize()

        for contract in self.grid._catalog.contracts.values():
            contract.reinitialize()

        for aggregator in self.grid._catalog.aggregators.values():
            aggregator.reinitialize()

        for device in self.grid._catalog.devices.values():
            device.reinitialize()
            device.update()  # devices publish the quantities they are interested in (both in demand and in offer)

        self.grid._catalog.set("incompatibility", False)  # the flag indicating if a second round of decision is needed due to multi-energy devices

        # ###########################
        # Calculus phase
        # ###########################

        # ascendant phase: balances with local energy and formulation of needs (both in demand and in offer)
        for aggregator in self.independent_aggregators_list:  # aggregators are called according to the predefined order
            aggregator.ask()  # aggregators make local balances and then publish their needs (both in demand and in offer)
            # the method is recursive

        # Constructing the observation (St vector)
        obs_keys = ["iteration", "interior", "forecast", "prices", "interconnection", "conversion"]
        observations = {}
        for agent in self.agents:
            state_dict = dict(zip(obs_keys, group_components(self.grid._catalog, agent)))
            if f"{agent}.raw_state" not in self.grid._catalog.keys:
                self.grid._catalog.add(f"{agent}.raw_state", state_dict)
            else:
                self.grid._catalog.set(f"{agent}.raw_state", state_dict)
            norm_obs = construct_state(state_dict, return_correct_dict(self.normalization_parameters, agent))
            observations[agent] = np.asarray(norm_obs, dtype=np.float32)

        return observations

    def step(self, actions):
        """
        We perform the instructions the same way in original Peacefulness "World.start" method, except we don't loop.
        """
        # Writing in the catalog the dicts of actions/aggregator
        for RL_agent in self.agents:
            if self.red_dof_dict is not None:
                distribute_my_action(actions[RL_agent].tolist(), self.grid._catalog, self.action_dict_per_agent[RL_agent], RL_agent, self.red_dof_dict[RL_agent])
            else:
                distribute_my_action(actions[RL_agent].tolist(), self.grid._catalog, self.action_dict_per_agent[RL_agent], RL_agent)

        # descendant phase: balances with remote energy
        for aggregator in self.independent_aggregators_list:  # aggregators are called according to the predefined order
            aggregator.distribute()  # aggregators make local balances and then publish their needs (both in demand and in offer)
            # the method is recursive
        # multi-energy devices management
        # as multi-energy devices state depends on different aggregators, a second round of distribution is performed in case of an incompability
        # multi-energy devices update their balances first and correct potential incompatibilities
        for device in self.grid._catalog.devices.values():
            device.second_update()

        # aggregators then check if everything is fine and correct potential problems
        for aggregator in self.independent_aggregators_list:
            aggregator.check()
            # the method is recursive

        if self.grid._catalog.get("incompatibility"):  # if a second round is needed
           for aggregator in self.independent_aggregators_list:  # aggregators are called according to the predefined order
               aggregator.ask()  # aggregators make local balances and then publish their needs (both in demand and in offer)
           for aggregator in self.independent_aggregators_list:  # aggregators are called according to the predefined order
               aggregator.distribute()  # aggregators make local balances and then publish their needs (both in demand and in offer)

        # ###########################
        # End of the turn
        # ###########################

        # devices update their state according to the quantity of energy received/given
        for device in self.grid._catalog.devices.values():
            device.react()
            device.make_balances()

        # balance phase at the aggregator level
        for aggregator in self.independent_aggregators_list:  # aggregators are called according to the predefined order
            aggregator.make_balances()  # aggregators make their final balances of money anf energy
            # the method is recursive

        # agent report what happened to their potential owner (i.e to another agent)
        for agent in self.independent_agents_list:
            agent.report()

        # data exporting
        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger.launch()

        # time update
        self.grid._update_time()

        # daemons activation
        for daemon in self.grid._catalog.daemons.values():
            daemon.launch()

        if self.verbose:
           print(f"End of the iteration {self.grid._catalog.get('simulation_time')}")

        # Termination condition
        terminations = {agent: False for agent in self.agents}  # TODO maybe add later the multi-energy check phase in the corresponding strategy

        # Truncation condition
        if self.grid._catalog.get('simulation_time') == self.grid._catalog.get("time_limit"):
            truncations = {agent: True for agent in self.agents}
            self.ended_episode = True
        else:
            truncations = {agent: False for agent in self.agents}

        # Computing immediate rewards
        # Getting the scaled-up decision made by the RL agent as understood by the environment
        results = {}
        for RL_agent in self.agents:
            results.update(recapitulate_state(self.grid._catalog, RL_agent))
            results.update(recapitulate_decision(self.grid._catalog, RL_agent))
        # Getting the list of the dataloggers defined for the study_case with respect of operational objectives.
        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger_keys = datalogger.get_keys  # retrieving the keys to be exported by the datalogger
            results = {**results, **datalogger.request_keys(datalogger_keys)}  # getting the values of these keys
        # Calculating each reward function - and then we sum them to get the overall immediate reward
        rewards = {agent: 0.0 for agent in self.agents}  # todo maybe a distinct penalty term for P3O ?
        for agent in self.agents:
            for reward_function in self.reward_function_list[agent]:
                if self.red_dof_dict is not None:
                    rewards[agent] += reward_function(results, self.metrics, agent, self.red_dof_dict[agent])
                else:
                    rewards[agent] += reward_function(results, self.metrics, agent)
            # Normalizing the immediate rewards with Emin and Emax - did not achieve better learning
            # rewards[agent] = normalize_my_rewards(rewards[agent], return_correct_dict(self.normalization_parameters, agent))

        # Getting the next observation dict
        observations = self._get_obs()

        # Getting the informations dict
        infos = self._get_infos()

        if any(terminations.values()) or all(truncations.values()):
            self.agents = []

        return observations, rewards, terminations, truncations, infos

    def render(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Box(low=-np.inf, high=np.inf, shape=(self.obs_size[agent], ), dtype=np.float32)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Box(low=-1.0, high=1.0, shape=(self.action_size[agent], ), dtype=np.float32)

    def get_my_dicts(self, agent_dict: Dict, red_dof_dict=None):
        """
        This method is used to retrieve the size of observation and action for each RL agent in the environment.
        :param agent_dict: A dict as follows {"RLagent_ID": {"aggregator": (obs_size, action_size), ..., "nb_exchanges": }, ...}.
        :param red_dof_dict: A dict as follows {"RLagent_ID": {"aggregator": "demand"/"supply"/"storage"/"exchange"/"conversion", ...}, ...}.
        """
        obs_dict = {}
        act_dict = {}
        for agent in agent_dict:
            obs_size = 0
            nb_actions = 0
            for key in agent_dict[agent]:
                if key != "exchanges":
                    obs_size += agent_dict[agent][key][0]
                    nb_actions += agent_dict[agent][key][1]
                else:
                    nb_actions += agent_dict[agent][key]
            obs_dict[agent] = obs_size
            act_dict[agent] = nb_actions
            if red_dof_dict is not None:
                act_dict[agent] -= len(red_dof_dict[agent])

        return obs_dict, act_dict

    def _identify_reward(self, objective_dict: Dict):
        """
        This method is used to retrieve the reward function(s) corresponding to each RL agent in the environment.
        :param objective_dict: The format {"RLagent_ID": [("reward_function_name", *args corresponding), ...], ...}.
        """
        self.reward_function_list = {}
        path_to_rewards = "lib/Subclasses/Strategy/SingleAgentDRLStrategy/Reward_functions"
        path_to_rewards = correct_path(path_to_rewards)

        for agent in objective_dict:
            reward_func_list = []
            for tup in objective_dict[agent]:
                rt_path = path_to_rewards + "." + tup[0]
                rt_file = import_module(rt_path)
                reward_func_list.append(rt_file.define_my_Rt(tup[1]))
            self.reward_function_list[agent] = reward_func_list  # Dict defining for each RL agent its reward functions

    def initial_grid_operation(self):
        self.grid._check()  # check if everything is fine in world definition

        if self.verbose:
            print(f"Start of the run named {self.grid.name}.\n")

        self.independent_aggregators_list = self.grid._identify_independent_aggregators()

        self.independent_agents_list = self.grid._identify_independent_agents()

        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger.initial_operations()

        # Identifying the scope of each RL agent (the aggregators it manages in the environment)
        for RL_agent in self.agents:
            RL_agent_scope = find_my_aggregators(self.independent_aggregators_list, RL_agent)
            if f"{RL_agent}.strategy_scope" not in self.grid._catalog.keys:
                self.grid._catalog.add(f"{RL_agent}.strategy_scope", RL_agent_scope)
            else:
                self.grid._catalog.set(f"{RL_agent}.strategy_scope", RL_agent_scope)

    def final_grid_operation(self):
        # end of the run
        if self.verbose:
            print("writing results")

        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger.final_process()
            datalogger.final_export()

        for daemon in self.grid._catalog.daemons.values():
            daemon.final_process()

        if self.verbose:
            print("Done")

        self.grid._clean_up()

        # reinitialize random state
        setstate(self.grid._random_state)
