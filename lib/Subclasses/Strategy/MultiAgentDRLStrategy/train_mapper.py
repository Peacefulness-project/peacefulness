from lib.Subclasses.Strategy.MultiAgentDRLStrategy.feasibility_policy import *

normalization_dict = {"energy_minimum": -12000.0, "energy_maximum": 8100.0}
error_tolerance = 75.0  # kWh
path_to_data = "cases/Studies/MultiAgent_RL/Results/pi_f_data_pre-training.csv"
tensorboard_path = "cases/Studies/MultiAgent_RL/Results/action_mapper"
agent_1_pif = FeasibilityPolicy(state_dim=22, latent_dim=11)
agent_1_trainer = FeasibilityPolicyTrainer(agent_1_pif, relevant_state_sample, connected_constraint_oracle,
                                           at_dim=11, latent_samples_per_state=4096, states_per_batch=16,
                                           sigma=0.15, sigma_p=0.3, lr=3e-5, norm_param=normalization_dict,
                                           offset_threshold=error_tolerance, path_to_data=path_to_data,
                                           agent_to_train=("agent_1", "agent_2"), tensorboard_path=tensorboard_path,
                                           device="cpu", state_1_dim=12, action_1_dim=6, nb_converters=2)
agent_1_trainer.train(2738, 100)
agent_1_trainer.save("cases/Studies/MultiAgent_RL/Results/action_mapper/feasibility_policy.pt")
