# Imports
from pathlib import Path
import math

# PettingZoo environment creation imports
from PeacefulnessEnv import PeacefulnessEnv, datetime

# RLlib Ray imports for training
import ray
from ray import tune
from ray.tune.registry import register_env
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.rllib.algorithms.ppo import PPOConfig
# from ray.rllib.policy.policy import PolicySpec
# from ray.rllib.algorithms.callbacks import DefaultCallbacks
from CallBacks import EpisodicMetricsCallback

# For printing results
import uuid
from pprint import pprint

# #################################################################
# Creating an instance of the PettingZoo multi-agent RL environment
###################################################################

# Parameters
path_to_case = "cases/Studies/first_paper_MultiEnergy/multiEnergyCaseStudy.py"
world_name = "MEG"
start_time = datetime(2020, 9, 22, 0, 0, 0)
simulation_length = 5304
path_to_export = "cases/Studies/first_paper_MultiEnergy/Results/Three_Agents"
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

ENV_PARAMS = dict(
    path_to_case=path_to_case,
    world_name=world_name,
    start_time=start_time,
    hours_to_simulate=simulation_length,
    export_path=path_to_export,
    agent_dict=agents_dict,
    objective_dict=reward_dict,
    normalization_dict=normalization_dict,
    metrics=metrics,
    red_dof_dict=act_red_dict
)

# #############################
# Training with RLlib Ray
#########################
# First, the PettingZoo parallel environment is wrapped and registered as a multi-agent environment in RLlib
def build_env(env_config):
    required = ["path_to_case", "world_name", "start_time", "hours_to_simulate", "export_path",
                "agent_dict", "objective_dict", "normalization_dict", "metrics", "red_dof_dict"]
    for key in required:
        if key not in env_config:
            raise ValueError(f"Value missing for {key} in env_config !")

    std_dev = env_config.get("std_dev", None)
    if std_dev is None:
        std_dev = 0.25
    else:
        print(f"Evaluation with std = {std_dev}")

    env = PeacefulnessEnv(env_config["path_to_case"], env_config["world_name"],
                          env_config["start_time"], env_config["hours_to_simulate"],
                          env_config["export_path"], env_config["agent_dict"], env_config["objective_dict"],
                          env_config["normalization_dict"], env_config["metrics"], std_dev, False,
                          env_config["red_dof_dict"]
                          )

    return PettingZooEnv(env)

# Creating a CallBack to restore trained model if we want to resume training (curriculum learning e.g.)
# class RestoreCallback(DefaultCallbacks):
#     def __init__(self, checkpoint_path):
#         super().__init__()
#         self.checkpoint_path = checkpoint_path
#
#     def on_algorithm_init(self, *, algorithm, **kwargs):
#         algorithm.restore(self.checkpoint_path)

# The mapping of policy-agent function is defined for the case study
def policy_mapping_fn(agent_id, *args, **kwargs):
    return agent_id  # independent learners (each agent gets its own policy)

policies = set(agents_dict.keys())

if __name__ == "__main__":
    # Create a config instance for the PPO algorithm and build it.
    ray.init(ignore_reinit_error=True)

    # Resuming training from a previously trained model
    # checkpoint_path = "D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/first_paper_MultiEnergy/Models/run_0aeb6f27a52a4be8969d5f707e05d501/PPO_MEG_caseStudy_38894_00000_0_2026-05-07_10-46-21/checkpoint_000000"

    env_name = "MEG_caseStudy"
    register_env(env_name, build_env)

    config = (
        PPOConfig()
        .environment("MEG_caseStudy",
                     env_config=ENV_PARAMS)
        .multi_agent(policies=policies,
                     policy_mapping_fn=policy_mapping_fn,
                     count_steps_by="agent_steps")  # since it's an AEC environment
        .env_runners(num_env_runners=4,
                     num_cpus_per_env_runner=1,
                     rollout_fragment_length=15912,
                     batch_mode="complete_episodes",
                     sample_timeout_s=300)
        .learners(num_learners=0)
        .training(use_critic=True,
                  use_gae=True,
                  lambda_=0.97,
                  vf_loss_coeff=0.5,
                  vf_clip_param=math.inf,
                  entropy_coeff=0.01,
                  clip_param=0.2,
                  gamma=0.99,
                  lr=3e-4,
                  train_batch_size=63648,
                  # train_batch_size_per_learner=5304,
                  num_epochs=5,
                  minibatch_size=624,
                  shuffle_batch_per_epoch=True,
                  use_kl_loss=True,
                  kl_target=0.01,
                  kl_coeff=0.2)
        .evaluation(evaluation_interval=25,
                    evaluation_num_env_runners=1,
                    evaluation_duration=1,
                    evaluation_duration_unit="episodes",
                    evaluation_config={"env_config": {"std_dev": 0}, "explore": False})
        .framework('torch')
        .callbacks(EpisodicMetricsCallback)
        .debugging(log_level='ERROR')
    )

    tuner = tune.Tuner(
        config.algo_class,
        param_space=config.to_dict(),
        run_config=tune.RunConfig(
            name=f"run_{uuid.uuid4().hex}",
            storage_path=Path("cases/Studies/first_paper_MultiEnergy/Results/Three_Agents/Models").resolve(),
            stop={"training_iteration": 100},
            checkpoint_config=tune.CheckpointConfig(
                checkpoint_score_attribute="evaluation/env_runners/episode_return_mean",
                checkpoint_score_order="max",)
        )
    )

    results = tuner.fit()
    best_results = results.get_best_result()
    pprint(best_results)
