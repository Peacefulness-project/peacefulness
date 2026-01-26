# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the penalty w.r.t energy conservation.
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: penalty coefficient w.r.t energy conservation constraint.
    """
    def energy_conservation(iteration_result: Dict, metrics:List=None, agent_ID:str=None):
        """
        :param iteration_result: the dataloggers' signal for each iteration used to compute the immediate reward.
        :param metrics: the metrics needed to compute the defined immediate reward.
        :param agent_ID: the ID of the RL agent for which the reward is computed.
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

        # We get then the sum of the scaled up actions corresponding to each aggregator
        scaled_actions = {}
        for agg in managed_aggregators:
            key = agg + f".{ref_name}.scaled_up_actions"
            if key in iteration_result:
                scaled_actions[agg] = - beta_0 * abs(sum(iteration_result[key]))

        # We can also retrieve energy flow values for each aggregator from the datalogger
        from_datalogger = {}
        for agg in managed_aggregators:
            sold_inside = 0.0
            sold_outside = 0.0
            bought_inside = 0.0
            bought_outside = 0.0
            if agg + f".energy_sold_inside" in iteration_result:
                sold_inside = iteration_result[agg + f".energy_sold_inside"]
            if agg + f".energy_sold_outside" in iteration_result:
                sold_outside = iteration_result[agg + f".energy_sold_inside"]
            if agg + f".energy_bought_inside" in iteration_result:
                bought_inside = iteration_result[agg + f".energy_sold_inside"]
            if agg + f".energy_bought_outside" in iteration_result:
                bought_outside = iteration_result[agg + f".energy_sold_inside"]
            from_datalogger[agg] = - beta_0 * abs((bought_inside + bought_outside) - (sold_inside + sold_outside))

        # Finally the reward is calculated and returned
        reward = 0.0
        for agg in managed_aggregators:
            reward += min(scaled_actions[agg], from_datalogger[agg])

        return reward

    return energy_conservation
