# Imports
from PeacefulnessEnv import PeacefulnessEnv, datetime
from pettingzoo.test import seed_test, api_test
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv


path_to_case = "cases/Studies/first_paper_MultiEnergy/multiEnergyCaseStudy.py"
world_name = "MEG"
start_time = datetime(2020, 9, 22, 0, 0, 0)
simulation_length = 5304
path_to_export = "cases/Studies/first_paper_MultiEnergy/Results/Three_Agents/testing"
agents_dict = {
    "Intermediary": {"Intermediary_HP": (9, 0), "Intermediary_CHP": (9, 0), "exchanges": 2},
    "EMG": {"electric_microgrid": (18, 2), "exchanges": 1},
    "DHN": {"district_heating_network": (21, 3), "exchanges": 0}
}
reward_dict = {
    "Intermediary": [
        ("green_injection", 1),
        ("gas_cost", 1)
    ],
    "EMG": [
        ("conservation_penalty", 10),
        ("social_cost", 1),
        ("aggregator_costs", 1)
                ],
    "DHN": [
        ("conservation_penalty", 10),
        ("waste_cost", 1),
        ("heatSink_cost", 1)
                ]
}
normalization_dict = {
    "energy_minimum": -25000.0, "energy_maximum": 35000.0,
                          "price_minimum": 0.0, "price_maximum": 0.57,
                      }
metrics = [
    "electric_microgrid.energy_bought_outside", "electric_microgrid.energy_sold_outside",  # external economic balance
    "electric_microgrid.money_spent_outside", "electric_microgrid.money_earned_outside",  # external economic balance
    "flexible_loads.LVE.energy_erased", "flexible_loads.LVE.money",  # social cost
    "combined_heat_power.LPG.energy_wanted", "combined_heat_power.LVE.energy_wanted", "combined_heat_power.LPG.money_spent",  # gas cost
    "electric_microgrid.LVE.energy_wanted", "combined_heat_power.LTH.energy_wanted", "district_heating_network.LVE.energy_wanted",
    "Waste_to_heat.heat_dissipated", "Waste_to_heat.LTH.energy_sold", "Waste_to_heat.LTH.money",  # cost of the wasted heat from the incinerator
    "combined_heat_power.heat_by_pass", "combined_heat_power.LTH.money",  # wasted heat from the CHP
    "PV_field_1.LVE.energy_sold", "PV_field_2.LVE.energy_sold", "WT_field_1.LVE.energy_sold", "WT_field_2.LVE.energy_sold",  # EnR
    "heat_pump.LVE.energy_bought", "heat_pump.LTH.energy_sold", "electric_microgrid.energy_bought_inside", "district_heating_network.energy_sold_inside"  # HP
]
act_red_dict = {
    # "EMG": {"electric_microgrid": "Energy_Exchange_1"},
    # "DHN": {"district_heating_network": "Energy_Storage"}
}


env = PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, reward_dict,
                      normalization_dict, metrics, red_dof_dict=act_red_dict)
# env.reset()
# step = 0
# while env.agents:
#     agent = env.agent_selection
#     obs = env.observe(agent)
#     action = env.action_space(agent).sample()
#     print(f"  step={step:3d} | agent={agent:10s} | obs_shape={obs.shape} | action={action}")
#     env.step(action)
#     # only count full world steps
#     if env._agent_selector.is_last():
#         step += 1
# print('Episode Finished')

# API test
# api_test(env, 5304)

# Seed test
# def create_my_env():
#     return PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, reward_dict, normalization_dict, metrics, red_dof_dict=act_red_dict)
#
# seed_test(create_my_env, num_cycles=10608)


# Testing the environment for RL_lib
libEnv = PettingZooEnv(env)
obs, info = libEnv.reset()
print("Reset OK. First agent to act:", obs.keys())
for step_iter in range(5304):
    # Only sample actions for the agents currently present in the `obs` dictionary
    actions = {
        agent_id: libEnv.action_space[agent_id].sample()
        for agent_id in obs
    }
    # Step the environment
    obs, rewards, terminated, truncated, infos = libEnv.step(actions)
    # Optional print to see what is happening step-by-step
    current_agents = list(obs.keys())
    # print(f"Step {step_iter} | Acting: {current_agents} | Rewards: {rewards}")
    # RLlib signifies the end of the episode by setting the "__all__" key to True
    is_terminated = terminated.get("__all__", False)
    is_truncated = truncated.get("__all__", False)
    if is_terminated or is_truncated:
        # print(f"Episode ended at step {step_iter}. Resetting environment...")
        obs, info = libEnv.reset()
print("Test complete!")
