# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t penalty for not totally serving loads.
    """
    def social_cost(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):  # todo patchwork solution
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
            if "erased" in metric or "money" in metric or "bought" in metric:
                key_list.append(metric)

        # We then retrieve the correct value from the iteration dict
        reward = 0.0
        # for key in key_list:
        #     if "residential" in key and agent_ID == "agent_1":
        #         reward += - beta_0 * abs(iteration_result[key])
        #         break
        #     if "industrial" in key and agent_ID == "agent_2":
        #         reward += - beta_0 * abs(iteration_result[key])
        #         break
        for key in key_list:
            if agent_ID == "agent_1":
                if "flexible_loads" in key and "erased" in key:
                    energy_erased = iteration_result[key]
                # elif "residential" in key and "money" in key:
                #     money_spent = iteration_result[key]
                # elif "residential" in key and "energy" in key:
                #     energy_bought = iteration_result[key]
            elif agent_ID == "agent_2":
                if "industrial" in key and "erased" in key:
                    energy_erased = iteration_result[key]
                # elif "industrial" in key and "money" in key:
                #     money_spent = iteration_result[key]
                # elif "industrial" in key and "energy" in key:
                #     energy_bought = iteration_result[key]

        # Finally we compute the reward
        # energy_price = money_spent / energy_bought if energy_bought != 0 else 0.0
        # erased_price = energy_price * energy_erased
        # reward += - beta_0 * abs(erased_price)
        reward += - beta_0 * abs(energy_erased)

        return reward

    return social_cost
