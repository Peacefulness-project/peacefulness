# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t penalty for not totally serving loads.
    """
    def social_cost(iteration_result: Dict, metrics:List=None, agent_ID:str=None):  # todo patchwork solution
        """
        :param iteration_result: the dataloggers' signal for each iteration used to compute the immediate reward.
        :param metrics: the metrics needed to compute the defined immediate reward.
        :param agent_ID: the ID of the RL agent for which the reward is computed.
        """
        # First we identify the relevant keys from the metrics list
        key_list = []
        for metric in metrics:
            if "energy" in metric:
                key_list.append(metric)

        # We then retrieve the correct value from the iteration dict
        reward = 0.0
        for key in key_list:
            if "residential" in key and agent_ID == "agent_1":
                reward += - beta_0 * abs(iteration_result[key])
                break
            if "industrial" in key and agent_ID == "agent_2":
                reward += - beta_0 * abs(iteration_result[key])
                break

        return reward

    return social_cost
