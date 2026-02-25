# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the penalty w.r.t energy conservation.
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: penalty coefficient w.r.t energy conservation constraint.
    """
    def energy_conservation(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):
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

        # In case, we don't reduce the degree of freedom per aggregator
        if action_reduction_dict is None:
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
        else:
            # We get the scaled-up actions/decisions & energy flow values intervals per aggregator
            reward = 0.0
            for agg in managed_aggregators:
                key1 = agg + f".{ref_name}.scaled_up_actions"
                key2 = agg + ".energy_flow_values_intervals"
                if key1 in iteration_result:
                    scaled_actions = iteration_result[key1]
                if key2 in iteration_result:
                    dynamic_intervals = iteration_result[key2]
                # We identify the masked action
                if agg in action_reduction_dict:
                    masked_action = action_reduction_dict[agg]

                # We then compute the offset per aggregator
                if masked_action == "Energy_Consumption":
                    if scaled_actions[0] > dynamic_intervals["Energy_Consumption"][1]:
                        offset = abs(scaled_actions[0] - dynamic_intervals["Energy_Consumption"][1])
                    elif scaled_actions[0] < dynamic_intervals["Energy_Consumption"][0]:
                        offset = abs(dynamic_intervals["Energy_Consumption"][0] - scaled_actions[0])
                    else:
                        offset = 0.0
                elif masked_action == "Energy_Production":
                    if scaled_actions[1] > dynamic_intervals["Energy_Production"][1]:
                        offset = abs(scaled_actions[1] - dynamic_intervals["Energy_Production"][1])
                    elif scaled_actions[1] < dynamic_intervals["Energy_Production"][0]:
                        offset = abs(dynamic_intervals["Energy_Production"][0] - scaled_actions[1])
                    else:
                        offset = 0.0
                elif masked_action == "Energy_Storage":
                    if scaled_actions[2] > dynamic_intervals["Energy_Storage"][1]:
                        offset = abs(scaled_actions[2] - dynamic_intervals["Energy_Storage"][1])
                    elif scaled_actions[2] < dynamic_intervals["Energy_Storage"][0]:
                        offset = abs(dynamic_intervals["Energy_Storage"][0] - scaled_actions[2])
                    else:
                        offset = 0.0
                else:
                    for idx in range(1, len(scaled_actions) - 2):
                        if str(idx) in masked_action:
                            for key in dynamic_intervals:
                                if str(idx) in key:
                                    interval_key = dynamic_intervals[key]
                            if scaled_actions[idx + 2] > interval_key[1]:
                                offset = abs(scaled_actions[idx + 2] - interval_key[1])
                            elif scaled_actions[idx + 2] < interval_key[0]:
                                offset = abs(interval_key[0] - scaled_actions[idx + 2])
                            else:
                                offset = 0.0
                # Finally the reward is computed based on the offset
                reward -= beta_0 * offset
                reward = ((reward + 12000) / 20100) * 2 - 1

        return reward

    return energy_conservation
