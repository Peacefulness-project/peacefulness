# Imports
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from importlib import import_module
from random import setstate
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import *
from datetime import datetime
import uuid


class PeacefulnessEnv(gym.Env):

    def __init__(self, path_to_case: str, world_name: str, start_time: datetime, hours_to_simulate: int, export_path: str, observation_size: int, action_dict: Dict, objective_dict: Dict, normalization_dict: Dict={}, metrics: List=[], std_dev:float=0.25, verbose=False):
        """
        path_to_case: the path to the case study
        hours_to_simulate: defines the length of each episode of training
        export_path: where to find the logs of the dataloggers
        observation_size: size of the observation vector
        action_dict: dict composed of : "total_size" ; "nb_exchanges" ; "nb_interior_actions_per_aggregator"
        normalization_dict: used to normalize states
        objective_dict: used to identify which reward function to apply (and for which agent)
        metrics: list of metrics used to compute the reward
        std_dev: by default it is set to 25% of noise to validation data
        verbose:
        """
        # Observation space - TODO on peut aussi avoir -inf et +inf comme low/high pour Box en normalisant avec NormalizeEnv de SB3 (à tester plus tard)
        # high_obs = np.ones(observation_size)
        # low_obs = np.zeros_like(high_obs)
        # self.observation_space = spaces.Box(low=low_obs, high=high_obs, dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(observation_size, ), dtype=np.float32)

        # Action space - TODO the SB3 models use tanh by default
        # self.action_space = spaces.Box(low=0.0, high=1.0, shape=(action_size, ), dtype=np.float32)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(action_dict["total_size"], ), dtype=np.float32)

        # Defining the reward function to use
        self._identify_reward(objective_dict)

        # Normalization parameters
        self.normalization_parameters = normalization_dict  # can be None if normalization at agent-level (in SB3)

        # Needed for the observation and for the step method
        self.independent_aggregators_list = []
        self.independent_agents_list = []

        # Needed for the step method
        self.action_info = deepcopy(action_dict)
        self.action_info.pop("total_size")  # contains only nb_exchanges, nb_internal_typologies_per_agg

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


    def _identify_reward(self, objective_dict: Dict):
        """
        objective_dict: has the format {"reward_function_name": [*args corresponding], ...}.
                        maybe in the multi-agent format, it will have {"reward_function_name": [(agent_ID, *args corresponding)], ...}.
        """
        reward_func_list = []
        path_to_rewards = "lib/Subclasses/Strategy/SingleAgentDRLStrategy/Reward_functions"
        path_to_rewards = correct_path(path_to_rewards)
        for name in objective_dict:
            rt_path = path_to_rewards + "." + name
            rt_file = import_module(rt_path)
            reward_func_list.append(rt_file.define_my_Rt(objective_dict[name]))

        self.reward_function_list = reward_func_list


    def initial_grid_operation(self):
        self.grid._check()  # check if everything is fine in world definition

        if self.verbose:
            print(f"Start of the run named {self.grid.name}.\n")

        self.independent_aggregators_list = self.grid._identify_independent_aggregators()

        self.independent_agents_list = self.grid._identify_independent_agents()

        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger.initial_operations()

        # Identifying which aggregators are managed by the RL agent through the gym strategy
        gym_scope = find_my_aggregators(self.independent_aggregators_list)
        if f"gym_Strategy.strategy_scope" not in self.grid._catalog.keys:
            self.grid._catalog.add(f"gym_Strategy.strategy_scope", gym_scope)
        else:
            self.grid._catalog.set(f"gym_Strategy.strategy_scope", gym_scope)


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
        state_dict = dict(zip(obs_keys, group_components(self.grid._catalog)))
        if f"gym_Strategy.raw_state" not in self.grid._catalog.keys:
            self.grid._catalog.add(f"gym_Strategy.raw_state", state_dict)
        else:
            self.grid._catalog.set(f"gym_Strategy.raw_state", state_dict)
        norm_obs = construct_state(state_dict, self.normalization_parameters)

        return np.asarray(norm_obs, dtype=np.float32)


    def _get_info(self):
        info = {}
        # if self.ended_episode:
        #     info["is_success"] = True

        return info  # TODO voir de quoi remplir


    def reset(self, *, seed=None, options=None):
        """
        We re-initialize the environment with this method.
        """
        super().reset(seed=seed)
        sim_seed = seed
        if sim_seed is None:
            sim_seed = int(self.np_random.integers(0, 2 ** 32 - 1))

        if self.ended_episode:
            self.final_grid_operation()
            self.ended_episode = False

        self.dataloggers_path += "/" + f"run_{self.env_id}_seed_{sim_seed}"
        self.grid = self.case_study.create_simulation(self.world_name, self.world_start, self.episode_length, self.dataloggers_path, self.metrics, sim_seed, self.std_dev)  # the Peacefulness World
        self.initial_grid_operation()

        observation = self._get_obs()
        info = self._get_info()

        return observation, info


    def step(self, action):
        """
        We perform the instructions the same way in original Peacefulness "World.start" method, except we don't loop.
        """
        distribute_my_action(action.tolist(), self.grid._catalog, self.action_info)  # writes in the catalog the dicts of actions/aggregator

        # descendant phase: balances with remote energy
        for aggregator in self.independent_aggregators_list:  # aggregators are called according to the predefined order
            aggregator.distribute()  # aggregators make local balances and then publish their needs (both in demand and in offer)
            # the method is recursive
        # multi-energy devices management
        # as multi-energy devices state depends on different aggreators, a second round of distribution is performed in case of an incompability
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

        # Truncated
        if self.grid._catalog.get('simulation_time') == self.grid._catalog.get("time_limit"):
            truncated = True
            self.ended_episode = True
        else:
            truncated = False

        # Terminated
        terminated = False  # TODO maybe add later the multi-energy check phase in the corresponding strategy

        # Computing the immediate reward
        # Getting the scaled-up decision made by the RL agent as understood by the environment
        results = recapitulate_decision(self.grid._catalog)
        # Getting the list of the dataloggers defined for the study_case with respect of operational objectives.
        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger_keys = datalogger.get_keys  # retrieving the keys to be exported by the datalogger
            results = {**results, **datalogger.request_keys(datalogger_keys)}  # getting the values of these keys
        # Calculating each reward function - and then we sum them to get the overall immediate reward
        reward = 0.0
        for reward_function in self.reward_function_list:  # todo maybe a distinct penalty term for P3O ?
            reward += reward_function(results, self.metrics)

        info = self._get_info()

        next_obs = self._get_obs()

        return next_obs, reward, terminated, truncated, info


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
