# Imports
import functools
from pettingzoo import ParallelEnv
from gymnasium.spaces import Box
from gymnasium.utils import seeding
import numpy as np
from importlib import import_module

from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Reward_functions.delayed_reward_SRL import SRL_PBRS_final_Rt
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import *
from random import setstate
from datetime import datetime
import uuid


class PeacefulnessEnv(ParallelEnv):
    metadata = {"name": "custom_env_v0", }

    def __init__(self, path_to_case: str, world_name: str, start_time: datetime, hours_to_simulate: int, export_path: str, agent_dict: Dict, aggregators_actions: Dict, objective_dict: Dict, normalization_dict: Dict={}, metrics: List=[], std_dev:float=0.25, verbose=False, red_dof_dict=None):
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
        self.agg_actions = deepcopy(aggregators_actions)
        self.red_dof_dict = red_dof_dict  # None if no degree of freedom is reduced
        self._cum_dict = {}  # for callback

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
        self.np_random, self.np_random_seed = seeding.np_random(seed)  # instead of passing the seed to the env, the generator is now passed
        self.np_random_seed = int(self.np_random_seed) % (2 ** 32)

        # Defining the RL agents present
        self.agents = self.possible_agents[:]

        # The final operation of the Peacefulness world at the end of each episode
        if self.ended_episode:
            self.final_grid_operation()
            self.ended_episode = False

        # Retrieving the Peacefulness world
        red_dof_flag = False if self.red_dof_dict is None else True
        myPath = deepcopy(self.dataloggers_path)
        myPath += "/" + f"run_{self.env_id}_seed_{self.np_random_seed}"
        self.grid = self.case_study.create_simulation(self.world_name, self.world_start, self.episode_length, myPath, self.metrics, [self.np_random_seed, self.np_random], self.std_dev, red_dof_flag)  # the Peacefulness World
        self.initial_grid_operation()  # Initial operation at the start of each episode

        # In case we remove 1-degree of freedom per aggregator
        if self.red_dof_dict is not None:
            for agent in self.red_dof_dict:
                for agg in self.red_dof_dict[agent]:
                    if f"Action removed for {agg}" not in self.grid._catalog.keys:  # Energy_Consumption, Energy_Production, Energy_Storage, Energy_Exchange, Energy_Conversion
                        self.grid._catalog.add(f"Action removed for {agg}", self.red_dof_dict[agent][agg])
                    else:
                        self.grid._catalog.set(f"Action removed for {agg}", self.red_dof_dict[agent][agg])

        # adding the existing RL agents to the grid catalog (useful for managing energy conversion systems)
        if f"existing_RL_agents" not in self.grid._catalog.keys:
            self.grid._catalog.add(f"existing_RL_agents", self.agents)
        else:
            self.grid._catalog.set(f"existing_RL_agents", self.agents)

        # Needed for logging metrics
        self.initialize_cumulative_dict()

        observations = self._get_obs()  # The observation of each RL agent
        infos = self._get_infos()

        return observations, infos

    def _get_infos(self, **kwargs):
        if not kwargs:
            info = {agent: {} for agent in self.agents}
        else:
            info = {agent: deepcopy(kwargs["info"]) for agent in self.agents}
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
            if not f"{aggregator.name}.incompatibility" in self.grid._catalog.keys:  # the flag indicating if a second round of decision is needed due to multi-energy devices
                self.grid._catalog.add(f"{aggregator.name}.incompatibility", False)
            else:
                self.grid._catalog.set(f"{aggregator.name}.incompatibility", False)

        for device in self.grid._catalog.devices.values():
            device.reinitialize()
            device.update()  # devices publish the quantities they are interested in (both in demand and in offer)


        # ###########################
        # Calculus phase
        # ###########################

        # ascendant phase: balances with local energy and formulation of needs (both in demand and in offer)
        for aggregator in self.independent_aggregators_list:  # aggregators are called according to the predefined order
            aggregator.ask()  # aggregators make local balances and then publish their needs (both in demand and in offer)
            # the method is recursive

        # Constructing the observation (St vector)
        obs_keys = ["iteration", "interior", "forecast", "prices", "interconnection", "conversion", "priority"]
        observations = {}
        centralized_critic = []  # todo specific idea of sharing the full observation between the two agents
        for agent in self.agents:
            state_dict = dict(zip(obs_keys, group_components(self.grid._catalog, agent)))
            if f"{agent}.raw_state" not in self.grid._catalog.keys:
                self.grid._catalog.add(f"{agent}.raw_state", state_dict)
            else:
                self.grid._catalog.set(f"{agent}.raw_state", state_dict)
            norm_obs = construct_state(state_dict, return_correct_dict(self.normalization_parameters, agent))

            # observations[agent] = np.asarray(norm_obs, dtype=np.float32)
            # # print(f"{agent} obs shape -> {observations[agent].shape}")
            # if f"{agent}.observation" not in self.grid._catalog.keys:
            #     self.grid._catalog.add(f"{agent}.observation", observations[agent])
            # else:
            #     self.grid._catalog.set(f"{agent}.observation", observations[agent])

            # todo specific idea of sharing the full observation between the two agents
            centralized_critic.extend(norm_obs)
            if f"{agent}.observation" not in self.grid._catalog.keys:
                self.grid._catalog.add(f"{agent}.observation", np.asarray(norm_obs, dtype=np.float32))
            else:
                self.grid._catalog.set(f"{agent}.observation", np.asarray(norm_obs, dtype=np.float32))
        for agent in self.agents:
            observations[agent] = np.asarray(centralized_critic, dtype=np.float32)


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

        # todo patchwork solution - for now superior absorbs the excess/deficit thus if incompatible aggregator its superior should also become incompatible ?
        incompatibility_aggregators = self.find_incompatibility_aggregators()  # if a second round is needed
        for aggregator in incompatibility_aggregators:  # aggregators are called according to the predefined order
            second_ask(aggregator)  # aggregators make local balances and then publish their needs (both in demand and in offer)
        for aggregator in incompatibility_aggregators:  # aggregators are called according to the predefined order
            second_distribute(aggregator)  # aggregators make local balances and then publish their needs (both in demand and in offer)

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

        # Computing immediate rewards
        # Getting the scaled-up decision made by the RL agent as understood by the environment
        results = {}
        for RL_agent in self.agents:
            results.update(recapitulate_state(self.grid._catalog, RL_agent))
            results.update(recapitulate_decision(self.grid._catalog, RL_agent))
            results.update(converters_recap(self.grid._catalog, RL_agent))
        # Getting the list of the dataloggers defined for the study_case with respect of operational objectives.
        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger_keys = datalogger.get_keys  # retrieving the keys to be exported by the datalogger
            results = {**results, **datalogger.request_keys(datalogger_keys)}  # getting the values of these keys
        # Calculating each reward function - and then we sum them to get the overall immediate reward
        # print(f"{self.grid._catalog.get("artificial_DHN.LTH.energy_wanted")}")
        # print(f"{self.grid._catalog.get("artificial_DHN.LTH.energy_accorded")}")
        rewards = {agent: 0.0 for agent in self.agents}  # todo maybe a distinct penalty term for P3O ?
        penalty = {agent: 0.0 for agent in self.agents}
        for agent in self.agents:
            for reward_function in self.reward_function_list[agent]:
                if self.red_dof_dict is not None:
                    val = reward_function(results, self.metrics, agent, self._cum_dict, self.red_dof_dict[agent])
                    rewards[agent] += val
                else:
                    val = reward_function(results, self.metrics, agent, self._cum_dict)
                    rewards[agent] += val
                if reward_function.__name__ == "energy_conservation":
                    penalty[agent] = deepcopy(val)

        for agent in self.agents:
            if results['converters_priority'] == agent:
                penalty.pop(agent)
                rewards[agent] += sum(penalty.values()) * 0.5
                break

            # Normalizing the immediate rewards with Emin and Emax - did not achieve better learning
            # rewards[agent] = normalize_my_rewards(rewards[agent], return_correct_dict(self.normalization_parameters, agent))

        # stats for callback
        self.group_metrics(results)

        # Getting the information dict - todo special for potential based rewards shaping
        # infos = self._get_infos(info=results)
        infos = self._get_infos()

        # Termination condition
        terminations = {agent: False for agent in self.agents}

        # Truncation condition
        if self.grid._catalog.get('simulation_time') >= self.grid._catalog.get("time_limit"):
            infos['EMG'].update({'episode_metrics': self._cum_dict})
            rewards = SRL_PBRS_final_Rt(rewards, self._cum_dict)
            truncations = {agent: True for agent in self.agents}
            self.ended_episode = True
        else:
            truncations = {agent: False for agent in self.agents}

        # Getting the next observation dict
        observations = self._get_obs()

        if any(terminations.values()) or all(truncations.values()):
            self.agents = []

        return observations, rewards, terminations, truncations, infos

    def render(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Box(low=-1.0, high=1.0, shape=(self.obs_size[agent], ), dtype=np.float32)

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

        # TODO patchwork solution for the multi-energy case study
        act_dict["EMG"] = 3
        act_dict["DHN"] = 4

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

            for agg in RL_agent_scope:
                if f"{agg.name}.expected_RL_actions" not in self.grid._catalog.keys:
                    self.grid._catalog.add(f"{agg.name}.expected_RL_actions", self.agg_actions[agg.name])
                else:
                    self.grid._catalog.set(f"{agg.name}.expected_RL_actions", self.agg_actions[agg.name])

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

    def find_incompatibility_aggregators(self):
        concerned_aggregators = []
        for RL_agent in self.agents:
            managed_aggregators = self.grid._catalog.get(f"{RL_agent}.strategy_scope")
            for agg in managed_aggregators:
                if self.grid._catalog.get(f"{agg.name}.incompatibility"):
                    concerned_aggregators.append(agg)

        return concerned_aggregators

    def initialize_cumulative_dict(self):  # todo patchwork solution for the MEG case study (CallBack)
        self._cum_dict = {
            "time_limit": self.grid._catalog.get('time_limit'),
            "sum_error_EMG": 0,
            "max_error_EMG": 0,
            "avg_error_EMG": 0,
            "sum_error_DHN": 0,
            "max_error_DHN": 0,
            "avg_error_DHN": 0,
            "priority_hours": {"EMG": 0, "DHN": 0},  # todo patchwork solution
            "total_electricity_consumption": 0,
            "total_heat_consumption": 0,
            "relative_electricity_error": 0,
            "relative_heat_error": 0,
            "exchange_cost": 0,
            "flex_given": 0,
            "flex_max": 0,
            "social_cost": 0,
            "gas_cost": 0,
            "W2h_dissipated_heat": 0,
            "CHP_heat_by_pass": 0,
            "green_HP_elec": 0,
            "total_HP_elec": 0,
            "total_HP_heat": 0,
            "incinerator_heat": 0,
            "total_heat_supply": 0,
            "HP_green_ratio": 0,
            "total_HP_green_injection": 0,
            "total_green_supply": 0,
            "OPEX": 0
        }

    def group_metrics(self, iteration_results: Dict):
        # Constraints related metrics
        #############################
        # energy conservation error for the Electric Microgrid.
        # TODO With removing 1-dol
        # Exch_value = iteration_results["electric_microgrid.EMG.scaled_up_actions"][3]
        # EMG_error = (
        # Exch_value - 22000 if Exch_value > 22000
        # else abs(Exch_value + 7200) if Exch_value < -7200
        # else 0
        # )
        # TODO Without removing 1-dol
        Exch_value = iteration_results["electric_microgrid.EMG.scaled_up_actions"]
        EMG_error = abs(sum(Exch_value))
        self._cum_dict["sum_error_EMG"] += EMG_error
        self._cum_dict["max_error_EMG"] = max(EMG_error, self._cum_dict["max_error_EMG"])
        # energy conservation error for the District Heating Network
        # TODO Without removing 1-dol
        e_conservation_error = abs(sum(iteration_results["district_heating_network.DHN.scaled_up_actions"]))
        # TODO With removing 1-dol
        # Esto_value = iteration_results["district_heating_network.DHN.scaled_up_actions"][2]
        # Esto_intervals = iteration_results["district_heating_network.energy_flow_values_intervals"]["Energy_Storage"]
        # e_conservation_error = (
        # Esto_value - Esto_intervals[1] if Esto_value > Esto_intervals[1]
        # else abs(Esto_value - Esto_intervals[0]) if Esto_value < Esto_intervals[1]
        # else 0
        # )
        self._cum_dict["sum_error_DHN"] += e_conservation_error
        self._cum_dict["max_error_DHN"] = max(e_conservation_error, self._cum_dict["max_error_DHN"])
        if iteration_results["simulation_time"] > 0:
            self._cum_dict["avg_error_EMG"] = self._cum_dict["sum_error_EMG"] / iteration_results["simulation_time"]
            self._cum_dict["avg_error_DHN"] = self._cum_dict["sum_error_DHN"] / iteration_results["simulation_time"]
        else:
            self._cum_dict["avg_error_EMG"] = self._cum_dict["sum_error_EMG"]
            self._cum_dict["avg_error_DHN"] = self._cum_dict["sum_error_DHN"]

        self._cum_dict["total_electricity_consumption"] += iteration_results["electric_microgrid.energy_sold_inside"] + iteration_results["electric_microgrid.energy_sold_outside"]
        self._cum_dict["total_heat_consumption"] += iteration_results["district_heating_network.energy_sold_inside"] + iteration_results["district_heating_network.energy_sold_outside"]

        # Coordination mechanism related
        ################################
        for agent in self._cum_dict["priority_hours"]:
            if agent == iteration_results['converters_priority']:
                self._cum_dict["priority_hours"][agent] += 1
                break
        # print(f"priority hours -> {self._cum_dict["priority_hours"]}")

        # Objectives related metrics
        ############################
        # Score / Operational costs
        earned_out = iteration_results["electric_microgrid.money_earned_outside"]
        spent_out = iteration_results["electric_microgrid.money_spent_outside"]
        balance_cost = earned_out - spent_out  # cost of electricity exchange with the main grid
        self._cum_dict["exchange_cost"] += balance_cost

        electricity_erased = iteration_results["flexible_loads.LVE.energy_wanted"]['energy_maximum'] - iteration_results["flexible_loads.LVE.energy_accorded"]['quantity']
        flexible_money = iteration_results["flexible_loads.LVE.money"]
        social_cost = electricity_erased * flexible_money  # cost of not serving flexible loads
        self._cum_dict["social_cost"] += social_cost
        self._cum_dict["flex_given"] += iteration_results["flexible_loads.LVE.energy_accorded"]['quantity']
        self._cum_dict["flex_max"] += iteration_results["flexible_loads.LVE.energy_wanted"]['energy_maximum']

        gas_cost = iteration_results["combined_heat_power.LPG.money_spent"]  # cost of gas used by the CHP
        self._cum_dict["gas_cost"] += gas_cost

        heat_ununsed = iteration_results["Waste_to_heat.heat_dissipated"]
        W2h_money = iteration_results["Waste_to_heat.LTH.money"]
        W2h_unused_heat = heat_ununsed * W2h_money  # cost of not using free heat from the incinerator
        self._cum_dict["W2h_dissipated_heat"] += W2h_unused_heat

        heat_by_pass = iteration_results["combined_heat_power.heat_by_pass"]
        CHP_heat_money = iteration_results["combined_heat_power.LTH.money"]
        CHP_heat_by_pass_cost = heat_by_pass * CHP_heat_money  # cost of heat surplus from the CHP
        self._cum_dict["CHP_heat_by_pass"] += CHP_heat_by_pass_cost

        # Green heat supply
        EnR_electricity = iteration_results["PV_field_1.LVE.energy_sold"] + iteration_results["PV_field_2.LVE.energy_sold"] + iteration_results["WT_field_1.LVE.energy_sold"] + iteration_results["WT_field_2.LVE.energy_sold"]
        electricity_total_supply = iteration_results["electric_microgrid.energy_bought_inside"] + iteration_results["electric_microgrid.energy_bought_outside"]
        if electricity_total_supply == 0:
            EnR_ratio = 0.0
        else:
            EnR_ratio = EnR_electricity / electricity_total_supply
        self._cum_dict["green_HP_elec"] += EnR_ratio * iteration_results["heat_pump.LVE.energy_bought"]
        self._cum_dict["total_HP_elec"] += iteration_results["heat_pump.LVE.energy_bought"]
        self._cum_dict["total_HP_heat"] += iteration_results["heat_pump.LTH.energy_sold"]
        self._cum_dict["incinerator_heat"] += iteration_results["Waste_to_heat.LTH.energy_sold"]
        self._cum_dict["total_heat_supply"] += iteration_results["district_heating_network.energy_bought_inside"]

        if iteration_results['simulation_time'] == self._cum_dict["time_limit"]:
            self._cum_dict["HP_green_ratio"] = self._cum_dict["green_HP_elec"] / self._cum_dict["total_HP_elec"]
            self._cum_dict["total_HP_green_injection"] = self._cum_dict["HP_green_ratio"] * self._cum_dict["total_HP_heat"]
            self._cum_dict["total_green_supply"] = (self._cum_dict["total_HP_green_injection"] + self._cum_dict["incinerator_heat"]) / self._cum_dict["total_heat_supply"]
            self._cum_dict["OPEX"] = self._cum_dict["exchange_cost"] - self._cum_dict["social_cost"] - self._cum_dict["gas_cost"] - self._cum_dict["W2h_dissipated_heat"] - self._cum_dict["CHP_heat_by_pass"]
            self._cum_dict["relative_electricity_error"] = self._cum_dict["sum_error_EMG"] / self._cum_dict["total_electricity_consumption"]
            self._cum_dict["relative_heat_error"] = self._cum_dict["sum_error_DHN"] / self._cum_dict["total_heat_consumption"]

