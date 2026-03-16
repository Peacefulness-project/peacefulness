# In this file utility functions for action mapping implementation are defined
# Imports
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import recapitulate_state
import numpy as np
from typing import Dict, List
import torch
import pandas as pd


def feasibility_relevant_state(catalog: "Catalog", norm_parameters: Dict, agent_ID=None):
    """
    This function is used to compute the used state for the feasibility policy.
    It is used inside the RL loop when action mapping is used.
    """
    return_list = []
    agent_state = recapitulate_state(catalog, agent_ID)
    for key, value in agent_state.items():
        for flow in value:
            return_list.extend(agent_state[key][flow])
    for idx in range(len(return_list)):
        return_list[idx] = 2 * ((return_list[idx] - norm_parameters['energy_minimum']) / (norm_parameters['energy_maximum'] - norm_parameters['energy_minimum'])) - 1

    return np.array(return_list, dtype=np.float32)


def load_states(path_to_data: str, concerned_agent):
    """
    This method is used to load states from the csv file.
    It is used during the pre-training of the action mapping model.
    """
    df = pd.read_csv(path_to_data, header=None, skiprows=1)  # reading the CSV file
    # Separate the DataFrame based on the ID
    id_1 = 'local_community_1.energy_flow_values_intervals'
    id_2 = 'local_community_2.energy_flow_values_intervals'
    df_1 = df[df[0] == id_1].copy()
    df_2 = df[df[0] == id_2].copy()
    # Dropping the string ID column
    df_1 = df_1.drop(columns=[0])
    df_2 = df_2.drop(columns=[0])
    # Cleaning up df_2 from the NaN
    df_2 = df_2.dropna(axis=1, how='all')
    # Converting to NumPy arrays
    array_1 = df_1.to_numpy(dtype=float)
    array_2 = df_2.to_numpy(dtype=float)

    if not isinstance(concerned_agent, tuple):  # if we train an action mapping model for each RL agent
        if concerned_agent == "agent_1":
            np.random.shuffle(array_1)
            to_return = list(array_1)
        else:
            np.random.shuffle(array_2)
            to_return = list(array_2)
    else:  # if we have one model for all the RL agents
        full_array = np.concatenate((array_1, array_2), axis=1)  # stacking horizontally the arrays
        np.random.shuffle(full_array)
        to_return = list(full_array)

    return to_return


def relevant_state_sample(data_list: List, norm_param: Dict):
    """
    This function is used to sample relevant states for the feasibility policy.
    """
    scaled_up_state = np.array(data_list.pop())

    return 2 * (scaled_up_state - norm_param["energy_minimum"]) / (norm_param["energy_maximum"] - norm_param["energy_minimum"]) - 1


def constraint_oracle(sampled_state: np.ndarray, action_vector: np.ndarray, normalization_parameters: Dict, error_threshold: float, st_dim=None, at_dim=None, nb_converters=None):
    """
    This function plays the role of feasibility model.
    For the case when the agents are independent.
    """
    # First we scale-up back the state vector
    sampled_state = ((sampled_state + 1) * (normalization_parameters['energy_maximum'] - normalization_parameters['energy_minimum'])) / 2 + normalization_parameters['energy_minimum']

    # Then we scale-up the action vector
    state_pairs = sampled_state.reshape(-1, 2)
    diff = state_pairs[:,1] - state_pairs[:,0]
    scale_up_at = (action_vector + 1) * (diff / 2)[None,:] + state_pairs[:,0][None,:]

    # Finally we compare the sum to a treshold
    row_sums = abs(scale_up_at.sum(axis=1))
    mask = row_sums < error_threshold

    return mask.astype(int)


def connected_constraint_oracle(sampled_state: np.ndarray, action_vector: np.ndarray, normalization_parameters: Dict, error_threshold: float, st1_dim: int, at1_dim: int, nb_converters: int):
    """
    This function plays the role of feasibility model.
    For the case when one model is trained for all the RL agents.
    Useful when energy conversion systems are present in the case study.
    """
    # First we scale-up back the state vector
    sampled_state = ((sampled_state + 1) * (normalization_parameters['energy_maximum'] - normalization_parameters['energy_minimum'])) / 2 + normalization_parameters['energy_minimum']
    agent_1_state = sampled_state[:st1_dim]
    agent_2_state = sampled_state[st1_dim:]

    # Then we scale-up the action vector
    agent_1_state_pairs = agent_1_state.reshape(-1, 2)
    agent_1_diff = agent_1_state_pairs[:, 1] - agent_1_state_pairs[:, 0]
    agent_2_state_pairs = agent_2_state.reshape(-1, 2)
    agent_2_diff = agent_2_state_pairs[:, 1] - agent_2_state_pairs[:, 0]
    # if only upstream aggregator decides for the energy conversion systems
    # Ecv_2 = action_vector[:, 4]  # decision for energy conversion 2
    # Ecv_1 = action_vector[:,-1]  # decision for energy conversion 1
    # agent_1_actions = np.hstack([action_vector[:, :4], Ecv_1[:, None], Ecv_2[:, None]])
    # agent_2_actions = np.hstack([action_vector[:, 5:8], Ecv_1[:, None], Ecv_2[:, None]])
    # if energy conversion system decision is made by both upstream and downstream aggregators
    agent_1_actions = action_vector[:, :at1_dim]
    agent_2_actions = action_vector[:, at1_dim:]

    scaled_up_at1 = (agent_1_actions + 1) * (agent_1_diff / 2)[None,:] + agent_1_state_pairs[:,0][None,:]
    scaled_up_at2 = (agent_2_actions + 1) * (agent_2_diff / 2)[None,:] + agent_2_state_pairs[:,0][None,:]

    converters_1_decision = scaled_up_at1[:, -nb_converters:]
    converters_2_decision = scaled_up_at2[:, -nb_converters:]
    # converters_1_decision, converters_2_decision = compute_converters_flow(converters_1_decision + converters_2_decision, True)  # taking the mean
    converters_1_decision, converters_2_decision = compute_converters_flow(converters_1_decision, converters_2_decision)  # taking the min
    scaled_up_at1 = np.hstack([scaled_up_at1[:, :-nb_converters], converters_1_decision])
    scaled_up_at2 = np.hstack([scaled_up_at2[:, :-nb_converters], converters_2_decision])

    # Finally we compare the sum to a treshold
    row_sums_at1 = abs(scaled_up_at1.sum(axis=1))
    mask_at1 = row_sums_at1 < error_threshold
    row_sums_at2 = abs(scaled_up_at2.sum(axis=1))
    mask_at2 = row_sums_at2 < error_threshold

    to_return = mask_at1 + mask_at2  # stricter than + where g=1 if only one aggregator satisfies energy conservation

    return to_return.astype(int)


def gaussian_kernel(diff: torch.Tensor, sigma:float, a_dim: int):
    return torch.exp(-0.5 * (diff / sigma).pow(2).sum(-1)) / ((2 * np.pi) ** (a_dim / 2) * sigma ** a_dim)


def kde(query: torch.Tensor, support: torch.Tensor, sigma: float, action_dim: int):
    """
    This function (Kernel Density Estimation) is used to estimate the current probability distribution of the feasibility policy q_theta.
    """
    diff = query.unsqueeze(1) - support.unsqueeze(0)  # [N, N, d_a]
    k = gaussian_kernel(diff, sigma, action_dim)  # [N, N]
    return k.mean(dim=1)  # [N]


def compute_converters_flow(arr1: np.ndarray, arr2: np.ndarray, mean_signal=False):
    """
    This helper function is used to compute the tru energy flow for energy conversion systems.
    """
    if not mean_signal:
        abs_val = np.minimum(np.abs(arr1), np.abs(arr2))
    else:
        abs_val = (np.abs(arr1) + np.abs(arr2)) / 2

    new_arr1 = np.sign(arr1) * abs_val
    new_arr2 = np.sign(arr2) * abs_val

    return new_arr1, new_arr2
