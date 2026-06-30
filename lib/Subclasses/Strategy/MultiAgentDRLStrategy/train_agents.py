# Imports
from pathlib import Path
import math

# PettingZoo environment creation imports
from PeacefulnessEnv import PeacefulnessEnv, datetime
# from pettingzoo.test import parallel_api_test, parallel_seed_test  # TODO for testing the PettingZoo environment
# from Wrappers import ScaleRewardsWrapper  # TODO Rt normalization
# from supersuit import normalize_obs_v0  # todo for St normalization

# RLlib ray imports for training
from ray import tune
import ray
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import register_env
from ray.rllib.algorithms.ppo import PPOConfig
# from ray.tune.schedulers import PopulationBasedTraining  # TODO for hyper-parameters tuning
from ray.rllib.algorithms.callbacks import DefaultCallbacks

# todo Imports for action mapping
# from ray.rllib.models import ModelCatalog
# from ray.rllib.models.torch.torch_action_dist import TorchSquashedGaussian
# from Wrappers import ActionMappingWrapper
# from feasibility_policy import FeasibilityPolicy, feasibility_relevant_state

# todo for Potential-based Rewards Shaping
# from Wrappers import PotentialBasedShapingWrapper
# from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Reward_functions.delayed_reward_MARL import MARL_MECS_Rt

# For printing results
import uuid
from pprint import pprint

from lib.Subclasses.Strategy.HierarchicalMADRLStrategy.CallBacks import make_episodic_metrics_callback


# #################################################################
# Creating an instance of the PettingZoo multi-agent RL environment
###################################################################

# Parameters
path_to_case = "cases/Studies/first_paper_MultiEnergy/multiEnergyCaseStudy.py"
world_name = "MEG"
start_time = datetime(2020, 9, 22, 0, 0, 0)
simulation_length = 5304
path_to_export = "cases/Studies/first_paper_MultiEnergy/Results/Two_Agents"
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
        ("green_injection", 1), ("social_cost", 1),
        ("aggregator_costs", 1), ("gas_cost", 1)
                ],
    "DHN": [
        ("conservation_penalty", 1),
        ("green_injection", 1),
        ("waste_cost", 1),
        ("gas_cost", 1), ("heatSink_cost", 1)
                ]
}
normalization_dict = {
    "energy_minimum": -25000.0, "energy_maximum": 35000.0, "price_minimum": 0.0, "price_maximum": 0.6
    # "agent_1": {"energy_minimum": -4000.0, "energy_maximum": 2600.0, "price_minimum": 0.05, "price_maximum": 0.25},
    # "agent_2": {"energy_minimum": -12000.0, "energy_maximum": 8100.0, "price_minimum": 0.05, "price_maximum": 0.25}
}
metrics = [
    "electric_microgrid.energy_bought_outside", "electric_microgrid.energy_sold_outside",  # external economic balance
    "electric_microgrid.money_spent_outside", "electric_microgrid.money_earned_outside",  # external economic balance
    "flexible_loads.LVE.energy_wanted", "flexible_loads.LVE.energy_accorded",  "flexible_loads.LVE.money",  # social cost
    "combined_heat_power.LPG.energy_wanted", "combined_heat_power.LVE.energy_wanted", "combined_heat_power.LPG.money_spent",  # gas cost
    "electric_microgrid.LVE.energy_wanted", "combined_heat_power.LTH.energy_wanted", "district_heating_network.LVE.energy_wanted",
    "Waste_to_heat.heat_dissipated", "Waste_to_heat.LTH.energy_sold", "Waste_to_heat.LTH.money",  # cost of the wasted heat from the incinerator
    "combined_heat_power.heat_by_pass", "combined_heat_power.LTH.money",  # wasted heat from the CHP
    "PV_field_1.LVE.energy_sold", "PV_field_2.LVE.energy_sold", "WT_field_1.LVE.energy_sold", "WT_field_2.LVE.energy_sold",  # EnR
    "heat_pump.LVE.energy_bought", "heat_pump.LTH.energy_sold", "electric_microgrid.energy_bought_inside", "district_heating_network.energy_sold_inside", "heat_pump.LTH.energy_wanted",  # HP
    "artificial_DHN.flexibility_offset"  # artificial DHN energy flexibility offset
]
act_red_dict = {
    "EMG": {"electric_microgrid": "Energy_Exchange_1"},
    "DHN": {"district_heating_network": "Energy_Storage"}
}

# todo Specific to action mapping
# my_pi_f = FeasibilityPolicy(state_dim=22, latent_dim=11)
# path_to_weights = "cases/Studies/MultiAgent_RL/Results/action_mapper/feasibility_policy.pt"
# state_sampler = feasibility_relevant_state

# todo Parameters for the PBRS wrapper.
# gamma = 0.95
# expn = True
# exp_base = 32
# pot_shift = - 0.2
# bias_reset = False
# bias_reset_val = 0
# worst_pot = {"agent_1": 25000, "agent_2": 30000}
# ref_rt = {"agent_1": 1e5, "agent_2": 1e5}
# needed_for_goal = metrics + ['flexible_loads.LVE.money', 'combined_heat_power.LPG.money', 'combined_heat_power.LTH.money',
#                              'rigid_electricity_consumption.LVE.energy', 'artificial_DHN.LTH.energy', 'artificial_DHN.LTH.money',
#                              'PV_field_1.LVE.energy', 'PV_field_2.LVE.energy',
#                              'WT_field_1.LVE.energy', 'WT_field_2.LVE.energy',
#                              'heat_pump.LVE.money', 'heat_pump.LTH.money']


ENV_PARAMS = dict(
    path_to_case = path_to_case,
    world_name = world_name,
    start_time = start_time,
    hours_to_simulate = simulation_length,
    export_path = path_to_export,
    agent_dict = agents_dict,
    aggregators_actions=agg_acts,
    objective_dict = reward_dict,
    normalization_dict = normalization_dict,
    metrics = metrics,
    red_dof_dict = act_red_dict,

    # todo Specific to action mapping
    # feasibility_policy = my_pi_f,
    # pi_f_path = path_to_weights,
    # relevant_state = state_sampler

    # todo Specific to PBRS wrapper
    # gamma = gamma,
    # expn = expn,
    # exp_base = exp_base,
    # pot_shift = pot_shift,
    # bias_reset = bias_reset,
    # bias_reset_val = bias_reset_val,
    # worst_pot = worst_pot,
    # ref_rt = ref_rt,
    # needed_mets = needed_for_goal,
    # goal_func = MARL_MECS_Rt
)

# todo Testing the PettingZoo envrionment
# Env creation
# myEnv = PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, reward_dict, normalization_dict, metrics)


# Interaction loop
# observations, infos = myEnv.reset(seed=42)
# while myEnv.agents:
#     actions = {agent: myEnv.action_space(agent).sample() for agent in myEnv.agents}
#     observations, rewards, terminations, truncations, infos = myEnv.step(actions)

# API Test
# parallel_api_test(myEnv, num_cycles=8760)

# Seed Test
# def create_my_env():
#     return PeacefulnessEnv(path_to_case, world_name, start_time, simulation_length, path_to_export, agents_dict, reward_dict, normalization_dict, metrics)
# parallel_seed_test(create_my_env, num_cycles=8760)

# todo Testing the environment for RL_lib
# libEnv = ParallelPettingZooEnv(myEnv)
# obs, info = libEnv.reset()
# print("Reset OK:", obs.keys())
# obs, rew, term, trunc, info = libEnv.step({agent: libEnv.action_space[agent].sample() for agent in obs})
# print("Step OK:", rew)
# for agent in obs:
#     print(obs[agent].shape)
# for iter in range(8760):
#     actions = {agent_id: libEnv.action_space[agent_id].sample() for agent_id in obs}
#     print(iter)
#     for agent in obs:
#         print(obs[agent].shape)
#     obs, rewards, terminated, truncated, infos = libEnv.step(actions)

# #############################
# Training with RLlib Ray
#########################

# First, the PettingZoo parallel environment is wrapped and registered as a multi-agent environment in RLlib
def build_env(env_config):
    required = ["path_to_case", "world_name", "start_time", "hours_to_simulate", "export_path", "agent_dict", "objective_dict"]
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
                          env_config["export_path"], env_config["agent_dict"], env_config["aggregators_actions"], env_config["objective_dict"],
                          env_config["normalization_dict"], env_config["metrics"], std_dev, False,
                          env_config["red_dof_dict"]
                          )  # for reducing one degree of freedom per aggregator
    # env = normalize_obs_v0(env)  # todo state normalization wrapper
    # wrapped_env = ScaleRewardsWrapper(env, gamma=0.99)  # todo Reward normalization wrapper
    # env = ActionMappingWrapper(env, env_config['feasibility_policy'], env_config['pi_f_path'], env_config['relevant_state'])  # todo Action Mapping wrapper
    # todo PBRS wrapper
    # env = PotentialBasedShapingWrapper(env, env_config["gamma"], env_config["expn"], env_config["exp_base"],
    #                                    env_config["pot_shift"], env_config["bias_reset"], env_config["bias_reset_val"],
    #                                    env_config["worst_pot"], env_config["ref_rt"], env_config["needed_mets"], env_config["goal_func"])

    return ParallelPettingZooEnv(env)

# Creating a CallBack to restore trained model if we want to resume training (curriculum learning e.g.)
class RestoreCallback(DefaultCallbacks):
    def __init__(self, checkpoint_path):
        super().__init__()
        self.checkpoint_path = checkpoint_path

    def on_algorithm_init(self, *, algorithm, **kwargs):
        algorithm.restore(self.checkpoint_path)


# The mapping of policy-agent function is defined for the case study
def policy_mapping_fn(agent_id, *args, **kwargs):  # todo gets more complex with parameters sharing etc...
    return agent_id  # independent learners (each agent gets its own policy)

policies = set(agents_dict.keys())

if __name__ == "__main__":
    # Create a config instance for the PPO algorithm and build it.
    ray.init(ignore_reinit_error=True)

    # Resuming training from a previously trained model
    # checkpoint_path = "D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/first_paper_MultiEnergy/Models/run_0aeb6f27a52a4be8969d5f707e05d501/PPO_MEG_caseStudy_38894_00000_0_2026-05-07_10-46-21/checkpoint_000000"

    env_name = "MEG_caseStudy"
    register_env(env_name, build_env)

    # Action mapping
    # ModelCatalog.register_custom_action_dist("squashed_gaussian", TorchSquashedGaussian)

    config = (
        PPOConfig()
        .environment("MEG_caseStudy",
                     env_config=ENV_PARAMS,
                     # normalize_actions=False
                     # disable_env_checking=True,
                     # is_atari=False
                     )
        .training(use_critic=True,
                  use_gae=True,
                  lambda_=0.97,
                  vf_loss_coeff=0.5,
                  vf_clip_param=math.inf,
                  entropy_coeff=0.01,
                  clip_param=0.2,
                  gamma=0.99,
                  lr=3e-4,
                  train_batch_size=21216,
                  # train_batch_size_per_learner=5304,
                  num_epochs=5,
                  minibatch_size=208,
                  shuffle_batch_per_epoch=True,
                  use_kl_loss=True,
                  kl_target=0.01,
                  kl_coeff=0.2
                  # model={
                  #     "custom_action_dist": "squashed_gaussian",  # todo for action mapping
                  # }
                  )
        .evaluation(evaluation_interval=25,
                    evaluation_num_env_runners=1,
                    evaluation_duration=1,
                    evaluation_duration_unit="episodes",
                    evaluation_config={"env_config": {"std_dev": 0, "explore": False}})
        .env_runners(num_env_runners=4,
                     num_cpus_per_env_runner=1,
                     rollout_fragment_length=5304,
                     batch_mode="complete_episodes",
                     sample_timeout_s=300)
        .learners(num_learners=0,
                  # num_cpus_per_learner=1,
                  # num_aggregator_actors_per_learner=1
                  )
        .multi_agent(policies=policies,
                     policy_mapping_fn=policy_mapping_fn,
                     policy_states_are_swappable=False,  # todo set this to true if agents share the same obs/act sizes
                     count_steps_by="env_steps"
                     )
        .callbacks(make_episodic_metrics_callback(agent_id="EMG"))
        # .callbacks(lambda: RestoreCallback(checkpoint_path))  # TODO this for resuming training from a trained model
        .framework("torch")
        .debugging(log_level="ERROR")
    )


    # Training without using Ray Tune
    # myPPO = config.build_algo()
    #
    # for _ in range(10):
    #     pprint(myPPO.train())

    # With Ray Tune - for more control over experiments, hyperparameters tuning, etc.
    # hyperparam_mutations = {      TODO if hyper-parameters tuning
    #     "clip_param": tune.grid_search([0.05, 0.1, 0.15, 0.2]),
    #     "lr": tune.grid_search([1e-3, 5e-4, 1e-4, 5e-5, 1e-5]),
    #     "num_epoch": tune.choice([3, 5, 8, 10, 12]),
    # }
    # pbt_scheduler = PopulationBasedTraining(
    #     time_attr="training_iteration",
    #     perturbation_interval=120,
    #     resample_probability=0.25,
    #     hyperparam_mutations=hyperparam_mutations,
    # )

    tuner = tune.Tuner(
        config.algo_class,
        param_space=config.to_dict(),
        run_config=tune.RunConfig(
            name=f"run_{uuid.uuid4().hex}",
            storage_path=Path("cases/Studies/first_paper_MultiEnergy/Results/Two_Agents/Models").resolve(),
            stop={"training_iteration": 100
                # , "episode_return_mean": 0.0
                  },  # number of training episodes (stopping criteria)
            checkpoint_config=tune.CheckpointConfig(  # to save the model which has the best rewards during training
                checkpoint_score_attribute="evaluation/env_runners/episode_return_mean",
                checkpoint_score_order="max",
            )
        ),
        # tune_config=tune.TuneConfig(      TODO if hyper-parameters tuning
        #     scheduler=pbt_scheduler,
        #     num_samples=10,
        #     metric="env_runners/episode_reward_mean",
        #     mode="max"
        # )
    )

    results = tuner.fit()
    best_results = results.get_best_result()
    pprint(best_results)
