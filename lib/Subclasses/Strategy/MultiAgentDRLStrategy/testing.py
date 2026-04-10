from PeacefulnessEnv import PeacefulnessEnv, datetime
from pettingzoo.test import parallel_api_test, parallel_seed_test
from Wrappers import PotentialBasedShapingWrapper
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Reward_functions.delayed_reward_test import MARL_MECS_Rt
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv

# Parameters for the base Env.
path_to_case = "cases/Studies/first_paper_MultiEnergy/multiEnergyCaseStudy.py"
world_name = "MEG"
start_time = datetime(2020, 1, 1, 0, 0, 0)
simulation_length = 8760
path_to_export = "cases/Studies/first_paper_MultiEnergy/Results"
agents_dict = {
    "agent_1": {"electric_microgrid": (22, 2), "exchanges": 3},
    "agent_2": {"district_heating_network": (25, 3), "exchanges": 2}
}
reward_dict = {
    "agent_1": [
        ("conservation_penalty", 1)
                ],
    "agent_2": [
        ("conservation_penalty", 1),
                ]
}
normalization_dict = {
    "energy_minimum": -19000.0, "energy_maximum": 31000.0, "price_minimum": 0.0, "price_maximum": 0.26
    # "agent_1": {"energy_minimum": -4000.0, "energy_maximum": 2600.0, "price_minimum": 0.05, "price_maximum": 0.25},
    # "agent_2": {"energy_minimum": -12000.0, "energy_maximum": 8100.0, "price_minimum": 0.05, "price_maximum": 0.25}
}
metrics = [
    "electric_microgrid.money_spent_outside", "electric_microgrid.money_earned_outside",
    "flexible_loads.LVE.energy_erased",
    # "Waste_to_heat.LTH.energy_sold",
    "combined_heat_power.LPG.energy_bought",
    # "combined_heat_power.LVE.energy_sold", "combined_heat_power.LTH.energy_sold",
    "heat_pump.LVE.energy_bought", "heat_pump.LTH.energy_sold"
]
act_red_dict = {
    "agent_1": {"electric_microgrid": "Energy_Exchange_1"},
    "agent_2": {"district_heating_network": "Energy_Storage"}
}


# Parameters for the PBRS wrapper.
gamma = 0.99
expn = True
exp_base = 32
pot_shift = - 0.1
bias_reset = False
bias_reset_val = 0
worst_pot = {"agent_1": 33566.5519, "agent_2": 35465.3909}
ref_rt = {"agent_1": 20352833.315, "agent_2": 6953289.515}
needed_for_goal = metrics + ['flexible_loads.LVE.money', 'combined_heat_power.LPG.money',
                             'rigid_electricity_consumption.LVE.energy',
                             'PV_field_1.LVE.energy', 'PV_field_2.LVE.energy',
                             'WT_field_1.LVE.energy', 'WT_field_2.LVE.energy',
                             'heat_pump.LVE.money', 'heat_pump.LTH.money']

# Instantiating the PettingZoo environment
myEnv = PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, reward_dict, normalization_dict, metrics, 0.25, False
                        # , act_red_dict
                        )

myEnv = PotentialBasedShapingWrapper(myEnv, gamma, expn, exp_base, pot_shift, bias_reset, bias_reset_val, worst_pot, ref_rt, needed_for_goal, MARL_MECS_Rt)

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
for _ in range(8760):
    actions = {agent_id: libEnv.action_space[agent_id].sample() for agent_id in obs}
    obs, rewards, terminated, truncated, infos = libEnv.step(actions)

