# Imports
from pathlib import Path

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
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.torch_action_dist import TorchSquashedGaussian
from Wrappers import ActionMappingWrapper
from feasibility_policy import FeasibilityPolicy, feasibility_relevant_state

# For printing results
import uuid
from pprint import pprint

# #################################################################
# Creating an instance of the PettingZoo multi-agent RL environment
###################################################################

# Parameters
path_to_case = "cases/Studies/first_paper_MultiEnergy/multiEnergyCaseStudy.py"
world_name = "MEG"
start_time = datetime(2021, 1, 1,0, 0, 0)
simulation_length = 8759
path_to_export = "cases/Studies/first_paper_MultiEnergy/Results"
agents_dict = {
    "agent_1": {"electric_microgrid": (22, 2), "exchanges": 3},
    "agent_2": {"district_heating_network": (25, 3), "exchanges": 2}
}
reward_dict = {
    "agent_1": [
        ("conservation_penalty", 2.5), ("social_cost", 1), ("green_injection", 1),
        ("aggregator_costs", 0.5), ("gas_cost", 0.5)
                ],
    "agent_2": [
        ("conservation_penalty", 2.5), ("green_injection", 1),
        ("gas_cost", 0.5), ("waste_cost", 0.5)
                ]
}
normalization_dict = {
    "energy_minimum": -19000.0, "energy_maximum": 31000.0, "price_minimum": 0.0, "price_maximum": 0.26
    # "agent_1": {"energy_minimum": -4000.0, "energy_maximum": 2600.0, "price_minimum": 0.05, "price_maximum": 0.25},
    # "agent_2": {"energy_minimum": -12000.0, "energy_maximum": 8100.0, "price_minimum": 0.05, "price_maximum": 0.25}
}
metrics = [
    "electric_microgrid.energy_bought_outside", "electric_microgrid.energy_sold_outside",
    "flexible_loads.LVE.energy_erased", "Waste_to_heat.LTH.energy_sold",
    "combined_heat_power.LPG.energy_bought", "combined_heat_power.LVE.energy_sold", "combined_heat_power.LTH.energy_sold",
    "heat_pump.LVE.energy_bought", "heat_pump.LTH.energy_sold"
]
act_red_dict = {
    "agent_1": {"electric_microgrid": "Energy_Exchange_1"},
    "agent_2": {"district_heating_network": "Energy_Storage"}
}

# Specific to action mapping
# my_pi_f = FeasibilityPolicy(state_dim=22, latent_dim=11)
# path_to_weights = "cases/Studies/MultiAgent_RL/Results/action_mapper/feasibility_policy.pt"
# state_sampler = feasibility_relevant_state

ENV_PARAMS = dict(
    path_to_case = path_to_case,
    world_name = world_name,
    start_time = start_time,
    hours_to_simulate = simulation_length,
    export_path = path_to_export,
    agent_dict = agents_dict,
    objective_dict = reward_dict,
    normalization_dict = normalization_dict,
    metrics = metrics,
    red_dof_dict = act_red_dict,
    # feasibility_policy = my_pi_f,
    # pi_f_path = path_to_weights,
    # relevant_state = state_sampler
)

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

# Testing the environment for RLlib
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
#     obs, rewards, terminateds, truncateds, infos = libEnv.step(actions)

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
                          env_config["export_path"], env_config["agent_dict"], env_config["objective_dict"],
                          env_config["normalization_dict"], env_config["metrics"], std_dev, False,
                          env_config["red_dof_dict"]
                          )  # for reducing one degree of freedom per aggregator
    # env = normalize_obs_v0(env)  # todo state normalization wrapper
    # wrapped_env = ScaleRewardsWrapper(env, gamma=0.99)  # todo Reward normalization wrapper
    # env = ActionMappingWrapper(env, env_config['feasibility_policy'], env_config['pi_f_path'], env_config['relevant_state'])  # todo Action Mapping wrapper

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
    ray.init()

    # Resuming training from a previously trained model
    # checkpoint_path = "D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/MultiAgent_RL/Models/run_0be381d40f6f42fbb0ae5a57a26d78b9/PPO_mini_case_93f69_00000_0_2026-03-01_20-41-01/checkpoint_000000"

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
                  entropy_coeff=0.01,
                  clip_param=0.2,
                  gamma=0.99,
                  lr=3e-4,
                  train_batch_size=8760,
                  train_batch_size_per_learner=8760,
                  num_epochs=5,
                  minibatch_size=73,
                  shuffle_batch_per_epoch=True,
                  # model={
                  #     "custom_action_dist": "squashed_gaussian",  # todo for action mapping
                  # }
                  )
        .evaluation(evaluation_interval=50,
                    evaluation_num_env_runners=1,
                    evaluation_duration_unit="episodes",
                    evaluation_duration=1,
                    evaluation_config={"env_config": {"std_dev": 0}})
        .env_runners(num_env_runners=4,
                     num_cpus_per_env_runner=1,
                     rollout_fragment_length="auto",
                     batch_mode="complete_episodes")
        .learners(num_learners=0,
                  # num_cpus_per_learner=1,
                  # num_aggregator_actors_per_learner=1
                  )
        .multi_agent(policies=policies,
                     policy_mapping_fn=policy_mapping_fn,
                     policy_states_are_swappable=False  # todo set this to true if agents share the same obs/act sizes
                     )
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
            storage_path=Path("cases/Studies/MultiAgent_RL/Models").resolve(),
            stop={"training_iteration": 100
                # , "episode_return_mean": 0.0
                  },  # number of training episodes (stopping criteria)
            checkpoint_config=tune.CheckpointConfig(  # to save the model which has the best rewards during training
                checkpoint_score_attribute="episode_return_mean",
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
