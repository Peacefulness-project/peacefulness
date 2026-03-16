# In this file, some utilities are defined

# Imports
from pettingzoo.utils.wrappers import BaseParallelWrapper
import numpy as np
import torch
# from feasibility_policy import FeasibilityPolicy
from gymnasium import spaces
from typing import Callable
# from AmUtilities import feasibility_relevant_state

class ScaleRewardsWrapper(BaseParallelWrapper):
    """
    Normalization of the rewards for the PettingZoo parallel environment.
    Using running mean/std method for returns.
    """
    def __init__(self, env, gamma=0.99):
        super().__init__(env)
        self.gamma = gamma

        # tracking stats per agent
        self.return_rms = {}
        self.returns = {}
        self.agents = env.possible_agents

    def reset(self, seed=None, options=None):
        obs, infos = self.env.reset(seed=None, options=None)

        self.returns = {agent: 0.0 for agent in self.agents}
        self.return_rms = {agent: {"mean": 0.0, "var": 1.0, "count": 1e-4} for agent in self.agents}

        return obs, infos

    def step(self, actions):
        obs, rewards, terminations, truncations, infos = self.env.step(actions)

        for agent, reward in rewards.items():
            self.returns[agent] = self.returns[agent] * self.gamma + reward  # mimicking the value function

            # Updating the running mean/std
            rms = self.return_rms[agent]
            rms["count"] += 1
            batch_mean = self.returns[agent]
            delta = batch_mean - rms["mean"]
            new_mean = rms["mean"] + delta / rms["count"]
            rms["var"] = rms["var"] + delta * (batch_mean - new_mean)
            rms["mean"] = new_mean

            # Normalizing the immediate reward using the variance
            var = rms["var"] / (rms["count"] - 1) if rms["count"] > 1 else 1.0
            stdev = np.sqrt(var) + 1e-8
            norm_reward = reward / stdev

            rewards[agent] = norm_reward

            # Reset return accumulator if agent is done
            if terminations[agent] or truncations[agent]:
                self.returns[agent] = 0.0

        return obs, rewards, terminations, truncations, infos


class ActionMappingWrapper(BaseParallelWrapper):
    """
    Wraps the pettingZoo environment, such that it intercepts the latent vector Z from the agent and maps it to A in the step method.
    """
    def __init__(self, env, pi_f: "FeasibilityPolicy", mapper_weight_path: str, state_sampler: Callable, device:str='cpu'):
        super().__init__(env)

        # Loading the pre-trained feasibility policy (mapper)
        self.mapper = pi_f.to(device)
        self.mapper.load_state_dict(torch.load(mapper_weight_path))
        self.mapper.eval()  # setting it to evaluation mode
        for parameter in self.mapper.parameters():  # freezing its weights
            parameter.requires_grad = False

        # Redefining the observation and action spaces
        for agent in self.possible_agents:   # action space stays the same shape (Z = A in cardinality) - but relabeled as latent space Z
            self.observation_spaces = {agent: self.env.observation_space(agent)}
            self.action_spaces = {agent: spaces.Box(low=-1.0, high=1.0, shape=self.env.action_space(agent).shape, dtype=np.float32)}

        self._last_obs = {}  # stored for feasibility relevant state information
        self.state_sampler = state_sampler  # function used to create the relevant state from the observation
        self.device = device

    def reset(self, seed=None, options=None):
        obs, infos = self.env.reset(seed=seed, options=options)
        self._last_obs = {agent: self.state_sampler(self.env.grid._catalog, self.env.normalization_parameters, agent) for agent in self.env.agents}

        return obs, infos

    def step(self, actions):
        """
        We get the latent actions from the RL agents.
        """
        mapped_actions = {}

        # The feasibility policy maps latent actions to real ones - Case 1 : independent action mappers !
        # with torch.no_grad(): # No gradients needed during RL rollout
        #     for agent_id, z in actions.items():
        #         # Converting s and z as input tensors for pi_f
        #         obs_tensor = torch.tensor(
        #             self._last_obs[agent_id], dtype=torch.float32, device=self.device
        #         ).unsqueeze(0)
        #
        #         z_tensor = torch.tensor(
        #             z, dtype=torch.float32, device=self.device
        #         ).unsqueeze(0)  # (1, Latent_Dim)
        #
        #         # Forward pass to get mapping to real action space
        #         a_t = self.mapper(obs_tensor, z_tensor)
        #
        #         # Converting back to correct format
        #         mapped_actions[agent_id] = a_t.squeeze(0).cpu().numpy()

        # Case 2 : one action mapper for all the agents (presence of energy conversion systems) !
        with torch.no_grad():
            concatenated_st = []
            concatenated_z = []

            for agent_id, z in actions.items():
                concatenated_st.extend(self._last_obs[agent_id].tolist())
                concatenated_z.extend(z.tolist())

            obs_tensor = torch.tensor(
                concatenated_st, dtype=torch.float32, device=self.device
            ).unsqueeze(0)

            z_tensor = torch.tensor(
                concatenated_z, dtype=torch.float32, device=self.device
            ).unsqueeze(0)

            # Forward pass to get mapping to real action space
            a_t = self.mapper(obs_tensor, z_tensor)
            outpu_t = a_t.squeeze(0).cpu().numpy()

            # Converting back to correct format
            for agent_id, z in actions.items():
                mapped_actions[agent_id] = outpu_t[:len(z)]
                outpu_t = outpu_t[len(z):]

        # Step the base environment with the safe physical actions
        obs, rewards, terminations, truncations, infos = self.env.step(mapped_actions)

        # Update current obs for the next step
        self._last_obs = {agent: self.state_sampler(self.env.grid._catalog, self.env.normalization_parameters, agent) for agent in self.env.agents}

        return obs, rewards, terminations, truncations, infos
