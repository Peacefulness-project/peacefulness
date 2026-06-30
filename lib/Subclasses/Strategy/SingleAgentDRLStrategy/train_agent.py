# Imports
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.PeacefulnessEnv import PeacefulnessEnv, datetime
# from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import VecNormalize, VecCheckNan
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from CustomCallback import EpisodicMetricsCallback, NormalizedEvalCallback
from stable_baselines3 import PPO
# from Wrappers import PotentialBasedShapingWrapper
# from Reward_functions.delayed_reward_SRL import SRL_PBRS_final_Rt
import numpy as np


# Test my Gym Environement
my_path = "cases/Studies/first_paper_MultiEnergy/multiEnergyCaseStudy.py"
world_name = "MEG_single_DRL"
start_time = datetime(2020, 9, 22, 0, 0, 0)
simulation_length = 5304
export_path = "cases/Studies/first_paper_MultiEnergy/Results/Mono_agent"
obs_size = 46
action_info = {"total_size": 6, "exchanges": 3, "interior": {"electric_microgrid": 1, "district_heating_network": 2}}
agg_acts = {"electric_microgrid": ("Energy_Consumption", "Energy_Conversion_2", "Energy_Conversion_3"),
            "district_heating_network": ("Energy_Production", "Energy_Conversion_2", "Energy_Conversion_3")}
obj = {
       # "dummyReward": 1
       "conservation_penalty": 10,
       "aggregator_costs": 1,
       "social_cost": 1,
       "gas_cost": 1,
       "waste_cost": 1, "heatSink_cost": 1,
       "green_injection": 1
}
normalizing_parameters = {
                          "energy_minimum": -25000.0, "energy_maximum": 35000.0,
                          "price_minimum": 0.0, "price_maximum": 0.6,
                          }
performance_metrics = [
    "electric_microgrid.energy_bought_outside", "electric_microgrid.energy_sold_outside",  # external economic balance
    "electric_microgrid.money_spent_outside", "electric_microgrid.money_earned_outside",  # external economic balance
    "flexible_loads.LVE.energy_wanted", "flexible_loads.LVE.energy_accorded", "flexible_loads.LVE.money",  # social cost
    "combined_heat_power.LPG.energy_wanted", "combined_heat_power.LVE.energy_wanted", "combined_heat_power.LPG.money_spent",  # gas cost
    "electric_microgrid.LVE.energy_wanted", "combined_heat_power.LTH.energy_wanted", "district_heating_network.LVE.energy_wanted",
    "Waste_to_heat.heat_dissipated", "Waste_to_heat.LTH.energy_sold", "Waste_to_heat.LTH.money",  # cost of the wasted heat from the incinerator
    "combined_heat_power.heat_by_pass", "combined_heat_power.LTH.money",  # wasted heat from the CHP
    "PV_field_1.LVE.energy_sold", "PV_field_2.LVE.energy_sold", "WT_field_1.LVE.energy_sold", "WT_field_2.LVE.energy_sold",  # EnR
    "heat_pump.LVE.energy_bought", "heat_pump.LTH.energy_sold", "electric_microgrid.energy_bought_inside", "district_heating_network.energy_sold_inside", "heat_pump.LTH.energy_wanted"  # HP
]
act_red_dict = {
    "electric_microgrid": "Energy_Exchange_1",
    "district_heating_network": "Energy_Storage"
}
MEG_caseStudy_env = PeacefulnessEnv(my_path, world_name, start_time, simulation_length, export_path, obs_size, action_info, agg_acts, obj,
                              normalizing_parameters,
                              performance_metrics, red_dof_dict=act_red_dict
                              )
obs, info = MEG_caseStudy_env.reset()
for _ in range(5304):
    action = MEG_caseStudy_env.action_space.sample()
    next_obs, reward, terminated, truncated, info = MEG_caseStudy_env.step(action)
# check_env(MEG_caseStudy_env, warn=True)
# test_env = VecCheckNan(test_env, True)  # to check NaNs and Infs at the environment level

# MEG_caseStudy_env = make_vec_env(PeacefulnessEnv, n_envs=1, env_kwargs={"path_to_case": my_path, "world_name": world_name,
#                                                      "start_time": start_time, "hours_to_simulate": simulation_length,
#                                                      "export_path": export_path, "observation_size": obs_size,
#                                                      "action_dict": action_info, "aggregators_actions": agg_acts, "objective_dict": obj,
#                                                      "normalization_dict": normalizing_parameters, "metrics": performance_metrics,
#                                                      "red_dof_dict": act_red_dict},
# #                                  # wrapper_class=lambda env: PotentialBasedShapingWrapper(
# #                                  #     env, gamma=0.95, base=2, worst_imbalance={"electric_microgrid": {"surplus": -37778.4, "deficit": 37566.55},
# #                                  #                                     "district_heating_network": {"surplus": -35731.4633, "deficit": 37375.7225}},
# #                                  #     delayed_reward=SRL_PBRS_final_Rt, scale=4596273.03
# #                                  # )
#                                  )
# MEG_caseStudy_env = VecNormalize(MEG_caseStudy_env, norm_obs=False, norm_reward=True)
# # # TODO resume training from a loaded model
# # # MEG_caseStudy_env = VecNormalize.load("cases/Studies/first_paper_MultiEnergy/Results/Mono_agent/Models/vecnormalize.pkl", MEG_caseStudy_env)
# # # MEG_caseStudy_env.training = True
# #
# # # TODO evaluation environment
# MEG_eval_env = make_vec_env(PeacefulnessEnv, env_kwargs={"path_to_case": my_path, "world_name": world_name,
#                                                      "start_time": start_time, "hours_to_simulate": simulation_length,
#                                                      "export_path": export_path, "observation_size": obs_size,
#                                                      "action_dict": action_info, "aggregators_actions": agg_acts, "objective_dict": obj,
#                                                      "normalization_dict": normalizing_parameters, "metrics": performance_metrics,
#                                                      "red_dof_dict": act_red_dict, "std_dev": 0})
# MEG_eval_env = VecNormalize(MEG_eval_env, training=False, norm_obs=False, norm_reward=True)
# # # MEG_eval_env.obs_rms = MEG_caseStudy_env.obs_rms
# #
# checkpoint_callback = CheckpointCallback(
#     save_freq=53040,  # we save a checkpoint every 10 episodes
#     save_path=export_path+"/checkpoints/",
#     name_prefix="ppo_model"
# )
#
# eval_callback = NormalizedEvalCallback(
#     MEG_eval_env,
#     best_model_save_path=export_path+"/Models/best_model/",
#     log_path=export_path+"/evaluations/",
#     eval_freq=132600,  # each 25 episodes, we evaluate the model
#     deterministic=True
# )
# export_callback = EpisodicMetricsCallback()
# #
# # # TODO training from scratch
# model = PPO("MlpPolicy", policy_kwargs=dict(net_arch=dict(pi=[256, 256], vf=[256, 256])), env=MEG_caseStudy_env,
#             learning_rate=3e-4, n_steps=5304,
#             batch_size=52, n_epochs=5, gamma=0.99, gae_lambda=0.97, clip_range=0.2, normalize_advantage=True,
#             ent_coef=0.01, vf_coef=0.5,
#             clip_range_vf=1,
#             stats_window_size=10,
#             tensorboard_log=export_path+"/tb_logs/", verbose=1)
# #
# # # TODO resume training from a loaded model
# # # model = PPO.load("cases/Studies/first_paper_MultiEnergy/Results/Mono_agent/Models/final_model.zip", env=MEG_caseStudy_env)
# #
# model.learn(total_timesteps=530400, callback=[checkpoint_callback, eval_callback, export_callback], progress_bar=True,
#             # reset_num_timesteps=False
#             )
# model.save(export_path+"/Models/final_model")
# MEG_caseStudy_env.save(export_path+"/Models/vecnormalize.pkl")

