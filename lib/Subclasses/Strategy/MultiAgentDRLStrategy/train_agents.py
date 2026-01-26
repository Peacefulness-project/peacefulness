# Imports
from lib.Subclasses.Strategy.MultiAgentDRLStrategy.PeacefulnessEnv import PeacefulnessEnv, datetime
from pettingzoo.test import parallel_api_test, parallel_seed_test

# #################################################################
# Creating an instance of the PettingZoo multi-agent RL environment
###################################################################

# Parameters
path_to_case = "cases/Studies/MultiAgent_RL/small_scale.py"
world_name = "mini_case"
start_time = datetime(2023, 1, 1,0, 0, 0)
simulation_length = 8759
path_to_export = "cases/Studies/MultiAgent_RL/Results"
agents_dict = {
    "agent_1": {"local_community_1": (23, 3), "exchanges": 1},
    "agent_2": {"local_community_2": (17, 2), "exchanges": 1}
}
reward_dict = {
    "agent_1": [("conservation_penalty", 10), ("aggregator_costs", 1), ("social_cost", 1)],
    "agent_2": [("conservation_penalty", 10), ("aggregator_costs", 1), ("social_cost", 1)]
}
normalization_dict = {
    "agent_1": {"energy_minimum": -2600.0, "energy_maximum": 4000.0, "price_minimum": 0.05, "price_maximum": 0.25},
    "agent_2": {"energy_minimum": -12000.0, "energy_maximum": 8100.0, "price_minimum": 0.05, "price_maximum": 0.25}
}
metrics = [
    "residential_dwellings.LVE.energy_erased", "industrial_process.LVE.energy_erased",
    "local_community_1.money_spent_outside", "local_community_2.money_spent_outside",
    "local_community_1.money_earned_outside", "local_community_2.money_earned_outside"
]

# Env creation
myEnv = PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, reward_dict, normalization_dict, metrics)
# observations, infos = myEnv.reset(seed=42)
# while myEnv.agents:
#     actions = {agent: myEnv.action_space(agent).sample() for agent in myEnv.agents}
#     observations, rewards, terminations, truncations, infos = myEnv.step(actions)

# API Test
parallel_api_test(myEnv, num_cycles=8760)

# Seed Test
def create_my_env():
    return PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, reward_dict, normalization_dict, metrics)

parallel_seed_test(create_my_env, num_cycles=8760)


