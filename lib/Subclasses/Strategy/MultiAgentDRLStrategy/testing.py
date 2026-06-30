from PeacefulnessEnv import PeacefulnessEnv, datetime
# from pettingzoo.test import parallel_api_test, parallel_seed_test
# from Wrappers import PotentialBasedShapingWrapper
# from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Reward_functions.delayed_reward_test import MARL_MECS_Rt
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv

# Parameters for the base Env.
path_to_case = "cases/Studies/first_paper_MultiEnergy/multiEnergyCaseStudy.py"
world_name = "MEG"
start_time = datetime(2021, 9, 22, 0, 0, 0)
simulation_length = 5304
path_to_export = "cases/Studies/first_paper_MultiEnergy/Results/Two_Agents/testing"
agents_dict = {
    "EMG": {"electric_microgrid": (49, 2), "exchanges": 3},
    "DHN": {"district_heating_network": (49, 3), "exchanges": 2}
}
agg_acts = {
    "electric_microgrid": ('Energy_Consumption', 'Energy_Conversion_2', 'Energy_Conversion_3'),
    "district_heating_network": ('Energy_Consumption', "Energy_Production", "Energy_Conversion_2", "Energy_Conversion_3"),
}
reward_dict = {
    "EMG": [
        ("conservation_penalty", 10),
        ("green_injection", 1.5), ("social_cost", 0.5),
        ("aggregator_costs", 0.7), ("gas_cost", 0.3)
                ],
    "DHN": [
        ("conservation_penalty", 10),
        ("green_injection", 1.5),
        ("waste_cost", 0.7),
        ("gas_cost", 0.3), ("heatSink_cost", 0.7)
                ]
}
normalization_dict = {
    "energy_minimum": -25000.0, "energy_maximum": 35000.0, "price_minimum": 0.0, "price_maximum": 0.6,
    # "efficiency_minimum": 2.44496538514395, "efficiency_maximum": 4.60688775510204
    # "agent_1": {"energy_minimum": -4000.0, "energy_maximum": 2600.0, "price_minimum": 0.05, "price_maximum": 0.25},
    # "agent_2": {"energy_minimum": -12000.0, "energy_maximum": 8100.0, "price_minimum": 0.05, "price_maximum": 0.25}
}
act_red_dict = {
    "EMG": {"electric_microgrid": "Energy_Exchange_1"},
    "DHN": {"district_heating_network": "Energy_Storage"}
}

metrics = [
    "electric_microgrid.energy_bought_outside", "electric_microgrid.energy_sold_outside",  # external economic balance
    "electric_microgrid.money_spent_outside", "electric_microgrid.money_earned_outside",  # external economic balance
    "flexible_loads.LVE.energy_wanted", "flexible_loads.LVE.energy_accorded", "flexible_loads.LVE.money",  # social cost
    "combined_heat_power.LPG.energy_wanted", "combined_heat_power.LVE.energy_wanted", "combined_heat_power.LPG.money_spent",  # gas cost
    "electric_microgrid.LVE.energy_wanted", "combined_heat_power.LTH.energy_wanted", "district_heating_network.LVE.energy_wanted",
    "Waste_to_heat.heat_dissipated", "Waste_to_heat.LTH.energy_sold", "Waste_to_heat.LTH.money",  # cost of the wasted heat from the incinerator
    "combined_heat_power.heat_by_pass", "combined_heat_power.LTH.money",  # wasted heat from the CHP
    "PV_field_1.LVE.energy_sold", "PV_field_2.LVE.energy_sold", "WT_field_1.LVE.energy_sold", "WT_field_2.LVE.energy_sold",  # EnR
    "artificial_DHN.flexibility_offset",
    "heat_pump.LVE.energy_bought", "heat_pump.LTH.energy_sold", "electric_microgrid.energy_bought_inside", "district_heating_network.energy_sold_inside", "heat_pump.LTH.energy_wanted"  # HP
]

# Parameters for the PBRS wrapper.
# gamma = 0.95
# expn = True
# exp_base = 32
# pot_shift = - 0.2
# bias_reset = False
# bias_reset_val = 0
# worst_pot = {"agent_1": 15000, "agent_2": 25000}
# ref_rt = {"agent_1": 1e6, "agent_2": 1e6}
# needed_for_goal = metrics + ['flexible_loads.LVE.money', 'combined_heat_power.LPG.money', 'combined_heat_power.LTH.money',
#                              'rigid_electricity_consumption.LVE.energy', 'artificial_DHN.LTH.energy', 'artificial_DHN.LTH.money',
#                              'PV_field_1.LVE.energy', 'PV_field_2.LVE.energy',
#                              'WT_field_1.LVE.energy', 'WT_field_2.LVE.energy',
#                              'heat_pump.LVE.money', 'heat_pump.LTH.money']

# Instantiating the PettingZoo environment
myEnv = PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, agg_acts,
                        reward_dict, normalization_dict, metrics, 0, False, act_red_dict
                        )

# myEnv = PotentialBasedShapingWrapper(myEnv, gamma, expn, exp_base, pot_shift, bias_reset, bias_reset_val, worst_pot, ref_rt, needed_for_goal, MARL_MECS_Rt)

# API Test
# parallel_api_test(myEnv, num_cycles=8760)

# Seed Test
# def create_my_env():
#     return PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, reward_dict, normalization_dict, metrics)
# parallel_seed_test(create_my_env, num_cycles=8760)

# done = False
# state_dict = {}
# obs, info = myEnv.reset(seed=694267)
# while not done:
#     actions = {agent: myEnv.action_space(agent).sample() for agent in myEnv.agents}
#     obs, rewards, terminations, truncations, info = myEnv.step(actions)
#     for v in terminations.values():
#         if v == True:
#             done = True
#     for v in truncations.values():
#         if v == True:
#             done = True
# obs, info = myEnv.reset(seed=694267)
# myEnv.close()

# Testing the environment for RLlib
libEnv = ParallelPettingZooEnv(myEnv)
obs, info = libEnv.reset()
for _ in range(5304):
    actions = {agent_id: libEnv.action_space[agent_id].sample() for agent_id in obs}
    obs, rewards, terminated, truncated, infos = libEnv.step(actions)
obs, info = libEnv.reset()

