# Imports
#########
import functools
from pettingzoo import AECEnv
from pettingzoo.utils import AgentSelector
from gymnasium.spaces import Box
from gymnasium.utils import seeding
from importlib import import_module

from pettingzoo.utils.env import AgentID, ObsType, ActionType

from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import *
from typing import Dict
from datetime import datetime
from random import setstate
import uuid

from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Reward_functions.delayed_reward_SRL import SRL_PBRS_final_Rt


class PeacefulnessEnv(AECEnv):
    metadata = {"name": "hierarchical_env_v0", }

    def __init__(self, path_to_case: str, world_name: str, start_time: datetime, hours_to_simulate: int, export_path: str, agent_dict: Dict, objective_dict: Dict, normalization_dict: Dict={}, metrics: List=[], std_dev:float=0.25, verbose=False, red_dof_dict=None):
        super().__init__()
        # Defining the possible agents
        self.possible_agents = list(agent_dict.keys())
        self.obs_size, self.action_size = self.get_my_dicts(agent_dict, red_dof_dict)  # getting the size of observation and action for each RL agent

        # Agents selection for cyclic stepping through agent list
        self._agent_selector = AgentSelector(self.possible_agents)

        # Defining the reward function to use
        self._identify_reward(objective_dict)

        # Normalization parameters
        self.normalization_parameters = normalization_dict  # can be given per RL agent or global
        self.independent_aggregators_list = []
        self.independent_agents_list = []
        self._cum_dict = {}

        # Needed for the top_down phase to distribute the decisions
        self.action_dict_per_agent = get_correct_action_dict(agent_dict)
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


    def reset(self, seed: int | None = None, options: dict | None = None) -> None:
        """
        Initialize the environment and RL agents at the start of each episode of training.
        """
        # Seeding
        if seed is not None:
            seed = int(seed) % (2 ** 32)
        self.np_random, self.np_random_seed = seeding.np_random(seed)  # instead of passing the seed to the env, the generator is now passed
        self.np_random_seed = int(self.np_random_seed) % (2 ** 32)

        # The final operation of the Peacefulness world at the end of each episode (exporting dataloggers)
        if self.ended_episode:
            self.final_grid_operation()
            self.ended_episode = False

        # Cycling order through RL agents
        self.agents = self.possible_agents[:]  # Defining the RL agents present
        # self._agent_selector = self._agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()

        # Mandatory dicts
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}


        # Retrieving the Peacefulness world
        myPath = deepcopy(self.dataloggers_path)
        myPath += "/" + f"run_{self.env_id}_seed_{self.np_random_seed}"
        self.grid = self.case_study.create_simulation(self.world_name, self.world_start, self.episode_length, myPath, self.metrics, [self.np_random_seed, self.np_random], self.std_dev, self.red_dof_dict)  # the Peacefulness World
        self.initial_grid_operation()  # Initial operation at the start of each episode

        # In case we remove 1-degree of freedom per aggregator
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


    def observe(self, agent: AgentID) -> ObsType | None:

        if self.terminations.get(agent, False) or self.truncations.get(agent, False):
            obs = np.zeros(self.observation_space(agent).shape, dtype=np.float32)
            # print(f"{agent} terminal observation -> {obs} at env step {self.grid._catalog.get("simulation_time")}")
        else:
            if agent == "Intermediary":  # the intermediary agent fixes the energy flowing in the CHP & HP
                self._define_state()
                self._return_state()
                obs = self.grid._catalog.get(f"{agent}.observation")

            else:  # the other agents observe the intermediary's decision and adapt to it
                converters_decision = self.grid._catalog.get("Intermediary.norm_action")  # todo patchwork solution
                original_obs = self.grid._catalog.get(f"{agent}.observation")
                obs = np.concatenate([original_obs, converters_decision])

        return obs


    def _define_state(self):
        """
        This method is used to get world's state (bottom_up_phase)
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

        for P_agent in self.grid._catalog.agents.values():
            P_agent.reinitialize()

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
        obs_keys = ["iteration", "interior", "forecast", "prices", "interconnection", "conversion"]
        observations = {}
        for R_agent in self.agents:
            state_dict = dict(zip(obs_keys, group_components(self.grid._catalog, R_agent)))
            if f"{R_agent}.raw_state" not in self.grid._catalog.keys:
                self.grid._catalog.add(f"{R_agent}.raw_state", state_dict)
            else:
                self.grid._catalog.set(f"{R_agent}.raw_state", state_dict)
            norm_obs = construct_state(state_dict, return_correct_dict(self.normalization_parameters, R_agent))

            observations[R_agent] = np.asarray(norm_obs, dtype=np.float32)
            if f"{R_agent}.observation" not in self.grid._catalog.keys:
                self.grid._catalog.add(f"{R_agent}.observation", observations[R_agent])
            else:
                self.grid._catalog.set(f"{R_agent}.observation", observations[R_agent])


    def _return_state(self):  # TODO patchwork solution
        """
        This utility function is used to modify the observation for the agents.
        """
        for agent in self.agents:
            old_obs = self.grid._catalog.get(f"{agent}.observation")
            new_obs = []
            if agent == "Intermediary":  # The intermediary agent
                new_obs.append(old_obs[0])  # time
                new_obs.append(old_obs[16])  # HP (upstream LVE)
                new_obs.append(old_obs[17])
                new_obs.append(old_obs[18])
                old_EMG = self.grid._catalog.get("EMG.observation")
                old_DHN = self.grid._catalog.get("DHN.observation")
                new_obs.append(old_DHN[19])  # HP (downstream LTH)
                new_obs.append(old_DHN[20])
                new_obs.append(old_DHN[21])
                new_obs.append(old_obs[34])  # CHP (upstream LPG)
                new_obs.append(old_obs[35])
                new_obs.append(old_obs[36])
                new_obs.append(old_EMG[16])  # CHP (upstream LVE)
                new_obs.append(old_EMG[17])
                new_obs.append(old_EMG[18])
                new_obs.append(old_DHN[22])  # CHP (upstream LTH)
                new_obs.append(old_DHN[23])
                new_obs.append(old_DHN[24])
                # Prices info
                new_obs.append(old_obs[29])  # gas price
                new_obs.append(old_EMG[11])  # electricity buying price
                new_obs.append(old_EMG[12])  # electricity selling price
                new_obs.append(old_DHN[17])  # heat price
                # Supply/load info
                new_obs.append(old_EMG[1])  # LVE demand
                new_obs.append(old_EMG[2])
                new_obs.append(old_EMG[6])  # LVE supply
                new_obs.append(old_EMG[7])
                new_obs.append(old_DHN[1])  # LTH demand
                new_obs.append(old_DHN[2])
                new_obs.append(old_DHN[6])  # LTH supply
                new_obs.append(old_DHN[7])
                new_obs.append(old_DHN[11])  # LTH TES
                new_obs.append(old_DHN[12])
                new_obs = np.array(new_obs)
            else:
                new_obs = old_obs[:-6]  # we remove features relative to energy conversion systems
            self.grid._catalog.set(f"{agent}.observation", new_obs)


    def step(self, action: ActionType) -> None:
        # Clearing this agent's cumulative reward at the start of its turn
        agent = self.agent_selection

        # Dead step guard
        if self.terminations[agent] or self.truncations[agent]:  # guard: if this agent is already done, skip it
            # print(f"DEAD STEP for {agent}")
            self._clear_rewards()
            self._was_dead_step(action)
            return

        # Clearing current's agent cumulative reward
        self._cumulative_rewards[agent] = 0.0

        # Storing the agent's action
        if f"{agent}.norm_action" not in self.grid._catalog.keys:
            self.grid._catalog.add(f"{agent}.norm_action", action)
        else:
            self.grid._catalog.set(f"{agent}.norm_action", action)

        # If last agent, advance world and accumulate rewards
        if self._agent_selector.is_last():
            self._advance_world()
        else:
            self._clear_rewards()

        # Advance agent selector
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()

    def _advance_world(self):
        """
        This method is used to implement the decisions/actions of the RL agents (top_down_phase)
        """
        # Writing in the catalog the dicts of actions/aggregator
        for RL_agent in self.agents:
            RL_agent_action = self.grid._catalog.get(f"{RL_agent}.norm_action")
            RL_agent_action_dict = deepcopy(self.action_dict_per_agent[RL_agent])
            if RL_agent != "Intermediary":  # retrieving the converters decision
                converters = deepcopy(self.grid._catalog.get("Intermediary.norm_action"))
                if RL_agent == "EMG":  # todo patchwork solution (for HP)
                    converters[0] = - converters[0]
                RL_agent_action = np.concatenate([RL_agent_action, converters])
                RL_agent_action_dict['exchanges'] += len(converters)

            if self.red_dof_dict is not None and RL_agent in self.red_dof_dict:
                distribute_my_action(RL_agent_action.tolist(), self.grid._catalog, RL_agent_action_dict, RL_agent, self.red_dof_dict[RL_agent])
            else:
                distribute_my_action(RL_agent_action.tolist(), self.grid._catalog, RL_agent_action_dict, RL_agent)

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
        for P_agent in self.independent_agents_list:
            P_agent.report()

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
        self._clear_rewards()
        for agent in self.agents:
            for reward_function in self.reward_function_list[agent]:
                if self.red_dof_dict is not None and agent in self.red_dof_dict:
                    self.rewards[agent] += reward_function(results, self.metrics, agent, self.red_dof_dict[agent])
                else:
                    self.rewards[agent] += reward_function(results, self.metrics, agent)
        # print(self.rewards)
        self.group_metrics(results, self.grid._catalog.get("time_limit"))

        # Infos
        self.infos = {a: {} for a in self.agents}

        # Termination condition
        self.terminations = {agent: False for agent in self.agents}

        # Truncation condition
        if self.grid._catalog.get('simulation_time') >= self.grid._catalog.get("time_limit"):
            self.infos['Intermediary'].update({'episode_metrics': self._cum_dict})
            for agent in self.agents:
                self.rewards[agent] = SRL_PBRS_final_Rt(self.rewards[agent], self._cum_dict)
            self.truncations = {agent: True for agent in self.agents}
            self.ended_episode = True
        else:
            self.truncations = {agent: False for agent in self.agents}

        # Resetting per-step buffers
        # for agent in self.agents:
        #     self.grid._catalog.set(f"{agent}.norm_action", None)


    def find_incompatibility_aggregators(self):
        concerned_aggregators = []
        for RL_agent in self.agents:
            managed_aggregators = self.grid._catalog.get(f"{RL_agent}.strategy_scope")
            for agg in managed_aggregators:
                if self.grid._catalog.get(f"{agg.name}.incompatibility"):
                    concerned_aggregators.append(agg)

        return concerned_aggregators


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
            print(f"Initial operation : Start of the run named {self.grid.name}.\n")

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
            print("Final grid operation, writing results")

        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger.final_process()
            datalogger.final_export()

        for daemon in self.grid._catalog.daemons.values():
            daemon.final_process()

        if self.verbose:
            print("Final grid operation, Done")

        self.grid._clean_up()

        # reinitialize random state
        setstate(self.grid._random_state)


    def render(self) -> None | np.ndarray | str | list:
        pass

    def close(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Box(low=-1.0, high=10.0, shape=(self.obs_size[agent], ), dtype=np.float32)

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
        manager_decisions = agent_dict["Intermediary"]['exchanges']
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
            if agent != "Intermediary":  # the EMG & DHN get to observe the decision of Energy Conversion Systems manager
                obs_dict[agent] += manager_decisions
            act_dict[agent] = nb_actions
            if red_dof_dict is not None and agent in red_dof_dict:
                act_dict[agent] -= len(red_dof_dict[agent])

        # TODO patchwork solution for the multi energy case
        obs_dict["Intermediary"] = 30
        obs_dict["EMG"] = 15
        obs_dict["DHN"] = 21

        return obs_dict, act_dict

    def initialize_cumulative_dict(self):  # todo patchwork solution for the MEG case study
        self._cum_dict = {
            "sum_error_EMG": 0,
            "max_error_EMG": 0,
            "avg_error_EMG": 0,
            "sum_error_DHN": 0,
            "max_error_DHN": 0,
            "avg_error_DHN": 0,
            "total_electricity_consumption": 0,
            "total_heat_consumption": 0,
            "relative_electricity_error": 0,
            "relative_heat_error": 0,
            "exchange_cost": 0,
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

    def group_metrics(self, iteration_results: Dict, time_limit: int):
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

        # Objectives related metrics
        ############################
        # Score / Operational costs
        earned_out = iteration_results["electric_microgrid.money_earned_outside"]
        spent_out = iteration_results["electric_microgrid.money_spent_outside"]
        balance_cost = earned_out - spent_out  # cost of electricity exchange with the main grid
        self._cum_dict["exchange_cost"] += balance_cost

        electricity_erased = iteration_results["flexible_loads.LVE.energy_erased"]
        flexible_money = iteration_results["flexible_loads.LVE.money"]
        social_cost = electricity_erased * flexible_money  # cost of not serving flexible loads
        self._cum_dict["social_cost"] += social_cost

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

        if iteration_results['simulation_time'] == time_limit:
            self._cum_dict["HP_green_ratio"] = self._cum_dict["green_HP_elec"] / self._cum_dict["total_HP_elec"]
            self._cum_dict["total_HP_green_injection"] = self._cum_dict["HP_green_ratio"] * self._cum_dict["total_HP_heat"]
            self._cum_dict["total_green_supply"] = (self._cum_dict["total_HP_green_injection"] + self._cum_dict["incinerator_heat"]) / self._cum_dict["total_heat_supply"]
            self._cum_dict["OPEX"] = self._cum_dict["exchange_cost"] - self._cum_dict["social_cost"] - self._cum_dict["gas_cost"] - self._cum_dict["W2h_dissipated_heat"] - self._cum_dict["CHP_heat_by_pass"]
            self._cum_dict["relative_electricity_error"] = self._cum_dict["sum_error_EMG"] / self._cum_dict["total_electricity_consumption"]
            self._cum_dict["relative_heat_error"] = self._cum_dict["sum_error_DHN"] / self._cum_dict["total_heat_consumption"]
