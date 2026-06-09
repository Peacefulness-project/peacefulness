# In this file, the trained model are run for inference
# Imports
import ray
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPO
from lib.Subclasses.Strategy.HierarchicalMADRLStrategy.train_agents import ENV_PARAMS, build_env
from lib.Subclasses.Strategy.HierarchicalMADRLStrategy.PeacefulnessEnv import *
import torch
import numpy as np



# helper function
def get_action(module, observation):
    """
    Policy network predicts an action.
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
        action_tensor = dist.to_deterministic().sample()

    return action_tensor.numpy()[0]

# Re-creating the Peacefulness AEC environment
ENV_PARAMS['std_dev'] = 0  # de-noising consumption data
ENV_PARAMS['export_path'] = "cases/Studies/first_paper_MultiEnergy/Results/Three_Agents/Inference"

# Trained model path
path_to_trained_model = "D:/dossier_y23hallo/Thèse/multi-energy/final_results/3-agents/without-1dol/C-10/model_4/PPO_MEG_caseStudy_4cbbb_00000_0_2026-06-08_08-43-03/checkpoint_000000"

# Global dicts for export
max_nb_exchanges = 1
max_nb_conversions = 2
state_dict = {}
decision_dict = {}


if __name__ == "__main__":
    ray.init()
    register_env("MEG_caseStudy", build_env)

    # Loading the trained model
    algo = PPO.from_checkpoint(path_to_trained_model, num_env_runners=0, evaluation_num_env_runners=0)

    # Inference loop
    my_env = PeacefulnessEnv(**ENV_PARAMS)
    my_env.reset()
    pmf = algo.config.multi_agent()["policy_mapping_fn"]  # policy mapping

    # AEC loop — agents act one at a time
    while my_env.agents:
        agent_id = my_env.agent_selection  # agent whose turn

        # skipping dead agents (at the end of the run)
        if my_env.terminations[agent_id] or my_env.truncations[agent_id]:
            my_env.step(None)
            continue

        obs = my_env.observe(agent_id)  # getting the observation

        # Saving the state for export
        for k, v in recapitulate_state(my_env.grid._catalog, agent_id).items():
            for key, value in v.items():
                state_dict.setdefault(k, {}).setdefault(key, []).append(value)

        # mapping the agent_id to its corresponding policy network
        policy_id = pmf(agent_id)
        module = algo.get_module(policy_id)

        # getting the action
        action = get_action(module, obs)
        action = np.clip(action, -1.0, 1.0)

        # the environment advances
        my_env.step(action)

        # Saving the action for export
        if agent_id == "DHN":
            for agent in my_env.agents:
                for k, v in recapitulate_decision(my_env.grid._catalog, agent).items():
                    if "scope" not in k:
                        decision_dict.setdefault(k, []).append(v)

    my_env.reset()  # for datalogger export

    # exporting results in CSV files
    export_my_state_file(state_dict, ENV_PARAMS["export_path"] + "_energy_intervals", max_nb_exchanges, max_nb_conversions)
    export_my_decision_file(decision_dict, ENV_PARAMS["export_path"] + "_RL_decisions", max_nb_exchanges, max_nb_conversions)

    # plotting results & saving plots
    plot_my_results(state_dict, decision_dict, ENV_PARAMS["export_path"])
