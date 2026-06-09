# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t penalty for not totally serving loads.
    """
    def heatSink_cost(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):  # todo patchwork solution
        """
        :param iteration_result: the dataloggers' signal for each iteration used to compute the immediate reward.
        :param metrics: the metrics needed to compute the defined immediate reward.
        :param agent_ID: the ID of the RL agent for which the reward is computed.
        :param action_reduction_dict: the dict in case of action reduction (1 action less per aggregator).
        """
        # First we identify the relevant keys from the metrics list
        key_list = []
        for metric in metrics:
            # if "energy" in metric:
            if "combined_heat_power" in metric:
                key_list.append(metric)

        # We then retrieve the correct value from the iteration dict
        reward = 0.0
        heatByPass_price = 0.0
        heatByPass_energy = 0.0
        for key in key_list:
            if "LTH.money" in key:
                heatByPass_price = iteration_result[key]
            elif "by_pass" in key:
                heatByPass_energy = iteration_result[key]

        # Finally we compute the reward
        # if heatByPass_price != 0.0:
        #     reward += - beta_0 * abs((heatByPass_price * heatByPass_energy) / (heatByPass_price * 9900.8))
        #     # reward += - beta_0 * abs(heatByPass_price * heatByPass_energy)
        reward += - beta_0 * abs(heatByPass_energy) / 9900.8

        return reward

    return heatSink_cost
