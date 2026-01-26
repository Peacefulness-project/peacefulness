# Imports
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.PeacefulnessEnv import PeacefulnessEnv, datetime
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import VecNormalize, VecCheckNan
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3 import PPO

# Test my Gym Environement
my_path = "cases/Studies/ClusteringAndStrategy/CasesStudied/LimitedResourceManagement/GymScriptTest.py"
world_name = "single_RL_case"
start_time = datetime(2023, 1, 1, 0, 0, 0)
simulation_length = 8759
export_path = "Results"
obs_size = 23  # cyclical time otherwise, it is 22
action_info = {"total_size": 4, "exchanges": 1, "interior": {"local_network": 3}}
obj = {"skeleton": 0.2}
normalizing_parameters = {"energy_minimum": -175.0, "energy_maximum": 1000.0, "price_minimum": 0.05, "price_maximum": 0.2}
performance_metrics = [
    "local_network.energy_bought_outside",
    "industrial_process.LVE.energy_bought",
]
my_test_env = PeacefulnessEnv(my_path, world_name, start_time, simulation_length, export_path, obs_size, action_info, obj,
                              normalizing_parameters,
                              performance_metrics,
                              # False
                              )
check_env(my_test_env, warn=True)
# test_env = VecNormalize(DummyVecEnv([lambda: Monitor(my_test_env)]), norm_obs=True, norm_reward=True)
test_env = make_vec_env(PeacefulnessEnv, env_kwargs={"path_to_case": my_path, "world_name": world_name,
                                                     "start_time": start_time, "hours_to_simulate": simulation_length,
                                                     "export_path": export_path, "observation_size": obs_size,
                                                     "action_dict": action_info, "objective_dict": obj})
test_env = VecCheckNan(test_env, True)  # to check NaNs and Infs at the environment level
# test_env = VecNormalize(test_env, norm_obs=True, norm_reward=True)  # to normalize St and Rt (at agent-level)


model = PPO("MlpPolicy", test_env, tensorboard_log="./tb_logs/", verbose=1)
model.learn(total_timesteps=12000)

