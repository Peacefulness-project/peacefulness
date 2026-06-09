# PBRS wrapper for single agent RL
# step
# super().step()
# recapitulate_state(catalog) => energy flow interval values => compute potential of the current state & next state
# potential = max(abs(max_neg), max_pos)
# info => cum_dict => when done, compute the delayed reward/objective
# base = 2
# delayed_reward_metrics (PBRS for MARL) is not needed, all the necessary information are found in "info"
# metrics are the same as for the original environment
# wort_imbalance = {"electric_microgrid": {"surplus": -37778.4, "deficit": 37566.55},
#                   "district_heating_network": {"surplus": -35731.4633, "deficit": 37375.7225}}

# Imports
import gymnasium as gym
from typing import Callable, Dict
from Utilities import recapitulate_decision


class PotentialBasedShapingWrapper(gym.Wrapper):
    """
    Using Potential-Based Reward Shaping (PBRS) to guide the training.
    The potential function would represent the energy conservation constraint.
    The delayed reward plays the role of operational objectives.
    """
    def __init__(self, env, gamma, base, worst_imbalance: Dict, delayed_reward: Callable, reset_to_bias=False, reset_value=None, scale=None):
        super().__init__(env)
        self.goal = delayed_reward
        self.gamma = gamma
        self.base = base
        self.reset_to_bias = reset_to_bias
        self.reset_value = reset_value
        self.max_potential = worst_imbalance
        self.goal = delayed_reward  # the delayed reward function that computes the objective signal
        self.scale = scale

    def potential(self, state, reward):
        # VecNormalize is used to normalize the states, the obs here is already scaled_up.
        # We don't normalize the rewards when using potential based reward shaping.
        C_elec_min, C_elec_max = state[1], state[2]
        P_elec_min, P_elec_max = state[6], state[7]
        Eexch_min, Eexch_max = state[13], state[14]
        HP_elec_min, HP_elec_max = state[16], state[17]
        CHP_elec_min, CHP_elec_max = state[19], state[20]
        elec_surplus = C_elec_min + P_elec_max + Eexch_min + HP_elec_min + CHP_elec_max
        elec_deficit = C_elec_max + P_elec_min + Eexch_max + HP_elec_max + CHP_elec_min
        C_heat_min, C_heat_max = state[22], state[23]
        P_heat_min, P_heat_max = state[27], state[28]
        Sdis, Sch = state[32], state[33]
        HP_heat_min, HP_heat_max = state[40], state[41]
        CHP_heat_min, CHP_heat_max = state[43], state[44]
        heat_surplus = C_heat_min + P_heat_max + Sdis + HP_heat_max + CHP_heat_max
        heat_deficit = C_heat_max + P_heat_min + Sch + HP_heat_min + CHP_heat_min

        # 1- either for each state, the potential function is the maximum possible error for both EMG & DHN (Pot = F(st))
        # potential = (4 - abs(elec_surplus) / abs(self.max_potential["electric_microgrid"]['surplus'])
        #                - abs(elec_deficit) / abs(self.max_potential["electric_microgrid"]['deficit'])
        #                - abs(heat_surplus) / abs(self.max_potential["district_heating_network"]['surplus'])
        #                - abs(heat_deficit) / abs(self.max_potential["district_heating_network"]['deficit'])
        #              )

        # 2- or we compute the error w.r.t to the action taken (Pot = F(st, at))
        # decision_dict = recapitulate_decision(self.env.unwrapped.grid._catalog)
        # EMG_error = sum(decision_dict["electric_microgrid.gym_Strategy.scaled_up_actions"])
        # if EMG_error < 0:  # surplus
        #     EMG_pot = abs(EMG_error / elec_surplus)
        # else:
        #     EMG_pot = abs(EMG_error / elec_deficit)
        #
        # DHN_error = sum(decision_dict["district_heating_network.gym_Strategy.scaled_up_actions"])
        # if DHN_error < 0:  # surplus
        #     DHN_pot = abs(DHN_error / heat_surplus)
        # else:
        #     DHN_pot = abs(DHN_error / heat_deficit)
        #
        # potential = 2 - EMG_pot - DHN_pot

        # 3- potential + reward (constraint violation)
        Emax = (max(abs(elec_surplus), elec_deficit) + max(abs(heat_surplus), heat_deficit)) * 10
        potential = abs(reward) / Emax

        return potential

    def rescale_potential(self, potential):
        # 1- if Pot = F(st)
        # max_pot = 4
        # potential /= max_pot
        # 2- if Pot = F(st, at)
        # max_pot = 2
        # potential /= max_pot
        # 3- potential + reward (constraint violation)
        potential = 1 - potential

        return potential

    def exponential_potential(self, potential):
        # return self.base ** (potential - 1)
        return self.scale * (self.base ** (potential - 1))

    def is_terminal(self, potential, done):
        if done:
            if not self.reset_to_bias:
                return 0
            else:
                return self.reset_value
        else:
            return potential

    def complete_info(self):
        if self.env.unwrapped.grid._catalog.get('simulation_time') == 1:
            self.env.unwrapped._cum_dict["HP_money"] = self.env.unwrapped.grid._catalog.get('heat_pump.LTH.money')
            self.env.unwrapped._cum_dict["W2h_money"] = self.env.unwrapped.grid._catalog.get('Waste_to_heat.LTH.money')

    def step(self, action):
        done = False
        current_obs = self.env.unwrapped.grid._catalog.get("gym_Strategy.observation")
        next_obs, reward, terminated, truncated, info = self.env.step(action)

        if terminated or truncated:
            done = True

        current_pot, next_pot = self.potential(current_obs, reward), self.potential(next_obs, reward)
        current_pot, next_pot = self.rescale_potential(current_pot), self.rescale_potential(next_pot)
        current_pot, next_pot = self.exponential_potential(current_pot), self.exponential_potential(next_pot)

        self.complete_info()
        if done:
            reward = self.goal(reward, self.env.unwrapped._cum_dict)

        reward = reward + self.gamma * self.is_terminal(next_pot, done) - self.is_terminal(current_pot, False)

        return next_obs, reward, terminated, truncated, info


