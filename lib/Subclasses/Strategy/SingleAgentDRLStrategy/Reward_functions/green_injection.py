# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t penalty for not totally serving loads.
    """
    def green_injection(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):  # todo patchwork solution
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
            if "heat_pump" in metric:
                key_list.append(metric)

        # We then retrieve the correct value from the iteration dict
        reward = 0.0
        HP_value = 0.0
        for key in key_list:
            if "bought" in key:
                HP_value += iteration_result[key] / 1500.0
            else:
                HP_value += iteration_result[key] / 6910.33163265306

        # Checking the condition for green injection
        elec_conso = abs(iteration_result["rigid_electricity_consumption.LVE.energy"])
        elec_conso += abs(iteration_result["flexible_loads.LVE.energy"])
        elec_supply = abs(iteration_result["PV_field_1.LVE.energy"])
        elec_supply += abs(iteration_result["PV_field_2.LVE.energy"])
        elec_supply += abs(iteration_result["WT_field_1.LVE.energy"])
        elec_supply += abs(iteration_result["WT_field_2.LVE.energy"])

        # Finally we compute the reward
        if elec_conso > elec_supply:
            reward += - beta_0 * abs(HP_value)
        else:
            reward += beta_0 * abs(HP_value)

        return reward

    return green_injection
