# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t penalty for not totally serving loads.
    """
    def social_cost(iteration_result: Dict, metrics:List=None, agent_ID:str=None, cumul_dict:Dict=None, action_reduction_dict:Dict=None):  # todo patchwork solution
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
            if "flexible" in metric:
                key_list.append(metric)

        # We then retrieve the correct value from the iteration dict
        reward = 0.0
        energy_price = 0.0
        energy_erased = 0.0
        for key in key_list:
            # if agent_ID == "agent_1":
            if "flexible_loads" in key and "wanted" in key:
                energy_wanted = iteration_result[key]
            elif "flexible_loads" in key and "accorded" in key:
                energy_accorded = iteration_result[key]
            elif "flexible_loads" in key and "money" in key:
                energy_price = iteration_result[key]

        # Finally we compute the reward
        if iteration_result['simulation_time'] != cumul_dict['time_limit']:  # end of simulation haven't been reached yet
            if energy_wanted['energy_maximum'] != 0:
                energy_erased = energy_accorded['quantity'] / energy_wanted['energy_maximum']
            else:
                energy_erased = 0.0
        else:
            energy_erased = (cumul_dict['flex_given'] - cumul_dict['flex_max'])/ cumul_dict['flex_max']

        reward += beta_0 * energy_erased

        return reward

    return social_cost
