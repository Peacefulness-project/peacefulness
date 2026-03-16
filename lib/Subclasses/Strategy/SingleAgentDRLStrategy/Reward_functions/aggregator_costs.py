# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t costs for aggregators.
    """
    def outside_cost(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):
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

        # First we identify the aggregators managed by the RL agent
        managed_aggregators = []
        for key in iteration_result:
            if ref_name in key and "scope" in key:
                managed_aggregators = iteration_result[key]

        # We get then the list of keys corresponding to these aggregators from the metrics
        list_of_keys = []
        for agg in managed_aggregators:
            for metric in metrics:
                if agg in metric and "energy" in metric:
                # if agg in metric and "money" in metric:
                    list_of_keys.append(metric)

        # Finally we can calculate the reward from the values in the iteration dict corresponding to keys
        reward = 0.0
        for metric in list_of_keys:
            if metric in iteration_result:
                reward += (
                    beta_0 * iteration_result[metric]
                    if "sold" in metric
                    else -beta_0 * iteration_result[metric]
                )
                # reward += (
                #     beta_0 * iteration_result[metric]
                #     if "earned" in metric
                #     else -beta_0 * iteration_result[metric]
                # )

        return reward

    return outside_cost
