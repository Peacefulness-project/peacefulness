# In this file, some utilities are defined

# Imports
from pettingzoo.utils.wrappers import BaseParallelWrapper
import numpy as np


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
