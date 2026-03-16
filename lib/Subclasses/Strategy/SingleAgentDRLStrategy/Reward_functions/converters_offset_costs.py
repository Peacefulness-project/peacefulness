# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List
import numpy as np

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t costs for aggregators.
    """
    def converter_cost(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):
        """
        :param iteration_result: the dataloggers' signal for each iteration used to compute the immediate reward.
        :param metrics: the metrics needed to compute the defined immediate reward.
        :param agent_ID: the ID of the RL agent for which the reward is computed.
        :param action_reduction_dict: the dict in case of action reduction (1 action less per aggregator).
        """
        # Distinction between single agent RL and multi-agent configuration
        if not agent_ID:
            ref_name = "gym_Strategy"
        else:
            ref_name = agent_ID

        # We get then the list of keys corresponding to these aggregators from the metrics
        reward = 0.0
        for key in iteration_result:
            if ref_name in key and "converters_offset" in key:
                # reward += - beta_0 * (sum(abs(np.array(list(iteration_result[key][0].values())))) ** 2)
                reward += - beta_0 * sum(abs(np.array(list(iteration_result[key][0].values()))))
                break

        return reward

    return converter_cost
