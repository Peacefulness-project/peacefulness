# In this file, the trained model are run for inference
# Imports
import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPO
from lib.Subclasses.Strategy.MultiAgentDRLStrategy.train_agents import ENV_PARAMS, build_env
import torch
import numpy as np


# helper function
def get_action(module, observation):
    """
    Runs a single inference step.
    """
    # Converting the numpy obs to torch tensor with batch dimension
    obs_tensor = torch.from_numpy(observation).float()
    input_batch = {"obs": obs_tensor.unsqueeze(0)}  # wrapping it in a dict
    with torch.no_grad():  # inference
        inference_output = module.forward_inference(input_batch)
    # Extracting the action
    if "action" in inference_output:
        action_tensor = inference_output["action"]
    else:
        logits = inference_output["action_dist_inputs"]
        dist_class = module.get_inference_action_dist_cls()
        dist = dist_class.from_logits(logits)
        action_tensor = dist.to_deterministic().sample()  # for deterministic action otherwise .sample() for exploration

    return action_tensor.numpy()[0]  # Removing batch dimension and convert back to Numpy


# I - Re-creating the environment & registering it in RLlib Ray
ENV_PARAMS["std_dev"] = 0  # making sure the environment is de-noised
ENV_PARAMS["export_path"] ="cases/Studies/MultiAgent_RL/Results/Inference"
path_to_trained_model = "D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/MultiAgent_RL/Models/run_c8404791cbac4b6f9589168db11c079d/PPO_mini_case_2ab71_00000_0_2026-02-03_17-34-10/checkpoint_000000"

if __name__ == "__main__":
    ray.init()
    register_env("mini_case", build_env)

# II - The trained model is retrieved via checkpoint
    algo = PPO.from_checkpoint(path_to_trained_model, num_env_runners=0, evaluation_num_env_runners=0)

# III - The inference loop is run
    my_env = build_env(ENV_PARAMS)
    obs, infos = my_env.reset()  # the environment is reset
    pmf = algo.config.multi_agent()["policy_mapping_fn"]  # policy mapping

    done = {"__all__": False}
    while not done["__all__"]:
        actions = {}
        for agent_id, agent_obs in obs.items():
            policy_id = pmf(agent_id)  # first we map each agent to its policy
            module = algo.get_module(policy_id)  # getting the corresponding RLModule
            action = get_action(module, agent_obs)
            actions[agent_id] = np.clip(action, -1.0, 1.0)  # TODO from action space of the environment

        obs, rewards, done, truncated, infos = my_env.step(actions)  # the actions of the agents are acted in the env
    obs, infos = my_env.reset()  # for datalogger export

