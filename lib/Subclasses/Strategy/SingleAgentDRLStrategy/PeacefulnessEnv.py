# Imports
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from importlib import import_module
from random import setstate
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import *
from datetime import datetime
import uuid
from Reward_functions.delayed_reward_SRL import SRL_PBRS_final_Rt


class PeacefulnessEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, path_to_case: str, world_name: str, start_time: datetime, hours_to_simulate: int, export_path: str, observation_size: int, action_dict: Dict, objective_dict: Dict, normalization_dict: Dict={}, metrics: List=[], std_dev:float=0.25, verbose=False, red_dof_dict=None):
        """
        :param path_to_case: the path to the case study
        :param hours_to_simulate: defines the length of each episode of training
        :param export_path: where to find the logs of the dataloggers
        :param observation_size: size of the observation vector
        :param action_dict: dict composed of : "total_size" ; "nb_exchanges" ; "nb_interior_actions_per_aggregator"
        :param normalization_dict: used to normalize states
        :param objective_dict: used to identify which reward function to apply (and for which agent)
        :param metrics: list of metrics used to compute the reward
        :param std_dev: by default it is set to 25% of noise to validation data
        :param verbose:
        :param red_dof_dict: if we apply 1-degree less of freedom per agent, a dict should be defined.
        """
        # Observation space - TODO on peut aussi avoir -inf et +inf comme low/high pour Box en normalisant avec NormalizeEnv de SB3 (à tester plus tard)
        # high_obs = np.ones(observation_size)
        # low_obs = np.zeros_like(high_obs)
        # self.observation_space = spaces.Box(low=low_obs, high=high_obs, dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(observation_size, ), dtype=np.float32)

        # Action space
        # self.action_space = spaces.Box(low=0.0, high=1.0, shape=(action_size, ), dtype=np.float32)
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(self.get_my_action_size(action_dict, red_dof_dict), ), dtype=np.float32)

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

        self.stats = {}


    def get_my_action_size(self, action_info: Dict, red_dof_dict=None):
        """
        This method is used to retrieve the size of actions for the RL agent in the environment.
        :param action_info: A dict as follows {"total_size": , "exchanges": , "interior": {"aggregator_1": , "aggregator_2":...}}.
        :param red_dof_dict: A dict as follows {"aggregator": "demand"/"supply"/"storage"/"exchange"/"conversion", ...}.
        """
        if not red_dof_dict:
            action_size = action_info["total_size"]
        else:
            action_size = action_info["total_size"] - len(red_dof_dict)
        return action_size


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
            if not f"{aggregator.name}.incompatibility" in self.grid._catalog.keys:  # the flag indicating if a second round of decision is needed due to multi-energy devices
                self.grid._catalog.add(f"{aggregator.name}.incompatibility", False)
            else:
                self.grid._catalog.set(f"{aggregator.name}.incompatibility", False)

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

        if f"gym_Strategy.observation" not in self.grid._catalog.keys:  # useful for the PBRS wrapper
            self.grid._catalog.add(f"gym_Strategy.observation", np.asarray(norm_obs, dtype=np.float32))
        else:
            self.grid._catalog.set(f"gym_Strategy.observation", np.asarray(norm_obs, dtype=np.float32))

        return np.asarray(norm_obs, dtype=np.float32)


    def _get_info(self):
        info = {}
        # if self.ended_episode:
        #     info["is_success"] = True

        return info


    def reset(self, *, seed=None, options=None):
        """
        We re-initialize the environment with this method.
        """
        super().reset(seed=seed)

        if self.ended_episode:
            self.final_grid_operation()
            self.ended_episode = False

        self.dataloggers_path += "/" + f"run_{self.env_id}_seed_{self.np_random_seed}"
        self.grid = self.case_study.create_simulation(self.world_name, self.world_start, self.episode_length, self.dataloggers_path, self.metrics, [self.np_random_seed, self.np_random], self.std_dev, self.red_dof_dict)  # the Peacefulness World
        self.initial_grid_operation()

        if self.red_dof_dict is not None:
            for agg in self.red_dof_dict:
                if f"Action removed for {agg}" not in self.grid._catalog.keys:  # Energy_Consumption, Energy_Production, Energy_Storage, Energy_Exchange, Energy_Conversion
                    self.grid._catalog.add(f"Action removed for {agg}", self.red_dof_dict[agg])
                else:
                    self.grid._catalog.set(f"Action removed for {agg}", self.red_dof_dict[agg])

        observation = self._get_obs()
        info = self._get_info()
        # Needed for logging metrics
        self.initialize_cumulative_dict()

        return observation, info


    def step(self, action):
        """
        We perform the instructions the same way in original Peacefulness "World.start" method, except we don't loop.
        """
        distribute_my_action(action.tolist(), self.grid._catalog, self.action_info, red_dof_dict=self.red_dof_dict)  # writes in the catalog the dicts of actions/aggregator

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

        incompatible_aggregators = self.find_incompatibility_aggregators()
        for aggregator in incompatible_aggregators:  # aggregators are called according to the predefined order
            second_ask(aggregator)  # aggregators make local balances and then publish their needs (both in demand and in offer)
        for aggregator in incompatible_aggregators:  # aggregators are called according to the predefined order
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

        # Truncated
        if self.grid._catalog.get('simulation_time') == self.grid._catalog.get("time_limit"):
            truncated = True
            self.ended_episode = True
            self._cum_dict["HP_money"] = self.grid._catalog.get('heat_pump.LTH.money')
            self._cum_dict["W2h_money"] = self.grid._catalog.get('Waste_to_heat.LTH.money')
        else:
            truncated = False

        # Terminated
        terminated = False  # TODO maybe add later the multi-energy check phase in the corresponding strategy

        # Computing the immediate reward
        # Getting the scaled-up decision made by the RL agent as understood by the environment
        results = {}
        results.update(recapitulate_state(self.grid._catalog))
        results.update(recapitulate_decision(self.grid._catalog))
        results.update(converters_recap(self.grid._catalog))
        # Getting the list of the dataloggers defined for the study_case with respect of operational objectives.
        for datalogger in self.grid._catalog.dataloggers.values():
            datalogger_keys = datalogger.get_keys  # retrieving the keys to be exported by the datalogger
            results = {**results, **datalogger.request_keys(datalogger_keys)}  # getting the values of these keys
        # Calculating each reward function - and then we sum them to get the overall immediate reward
        reward = 0.0
        for reward_function in self.reward_function_list:  # todo maybe a distinct penalty term for P3O ?
            func_reward = 0.0
            func_reward += reward_function(results, self.metrics, action_reduction_dict=self.red_dof_dict)

            if str(reward_function) in self.stats.keys():
                self.stats[str(reward_function)].append(func_reward)
            else:
                self.stats[str(reward_function)] = [func_reward]

            reward += func_reward

        info = self._get_info()
        info.update(group_metrics(results, self._cum_dict, self.episode_length))  # for the (episodic) metrics callback
        if terminated or truncated:
            info.update(recapitulate_decision(self.grid._catalog))  # for the last iteration during inference

            dict_to_csv(self.stats, "D:/dossier_y23hallo/Thèse/multi-energy/final_results/rt_components.csv")


        # if truncated:
        #     reward = SRL_PBRS_final_Rt(reward, self._cum_dict)  # todo patchwork solution delayed reward (PBRS)

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


    def find_incompatibility_aggregators(self):
        concerned_aggregators = []
        managed_aggregators = self.grid._catalog.get(f"gym_Strategy.strategy_scope")
        all_aggregators = self.grid._catalog.aggregators.values()
        for agg in all_aggregators:
            if self.grid._catalog.get(f"{agg.name}.incompatibility"):
                concerned_aggregators.append(agg)
            if not agg in managed_aggregators and self.grid._catalog.get("incompatibility"):
                device_list = agg.devices
                for device in device_list:
                    if device == "combined_heat_power":  # TODO patchwork solution for the MEG case study
                        concerned_aggregators.append(agg)

        return concerned_aggregators


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


def dict_to_csv(data: dict, filename="output.csv"):
    # Get column names
    columns = list(data.keys())

    # Determine the maximum number of rows
    max_len = max(len(values) for values in data.values())

    # Open CSV file for writing
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow(columns)

        # Write rows
        for i in range(max_len):
            row = []
            for col in columns:
                # Get value if exists, else empty string
                values = data[col]
                row.append(values[i] if i < len(values) else "")
            writer.writerow(row)

