# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t penalty for not totally serving loads.
    """
    def green_injection(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):  # todo patchwork solution
        """
        :param iteration_result: the dataloggers signal for each iteration used to compute the immediate reward.
        :param metrics: the metrics needed to compute the defined immediate reward.
        :param agent_ID: the ID of the RL agent for which the reward is computed.
        :param action_reduction_dict: the dict in case of action reduction (1 action less per aggregator).
        """
        # First we identify the relevant keys from the metrics list
        # key_list = []
        # for metric in metrics:
        #     # if "energy" in metric:
        #     if "heat_pump" in metric or "priority" in metric:
        #         key_list.append(metric)

        # We then retrieve the correct value from the iteration dict
        reward = 0.0
        # HP_elec_value = 0.0
        # HP_elec_price = 0.0
        # HP_heat_value = 0.0
        # HP_heat_price = 0.0
        # for key in key_list:
        #     if "bought" in key:
        #         HP_elec_value += iteration_result[key]
        #     elif "LVE.money" in key:
        #         HP_elec_price += iteration_result[key]
        #     elif "LTH.money" in key:
        #         HP_heat_price += iteration_result[key]
        #     elif "sold" in key:
        #         HP_heat_value += iteration_result[key]
        #     elif "priority" in key:
        #         to_assign = (
        #                     "agent_1" if iteration_result[key] > 0
        #                     else "agent_2" if iteration_result[key] < 0
        #                     else "any"
        #                     )
        #
        # if HP_elec_price != 0.0:
        #     HP_value = (HP_elec_value * HP_elec_price) / (1500.0 * HP_elec_price) + (HP_heat_value * HP_heat_price) / (6910.33163265306 * HP_heat_price)
        # else:
        #     HP_value = 0.0

        # Checking the condition for green injection
        # elec_conso = abs(iteration_result["rigid_electricity_consumption.LVE.energy"])
        # elec_conso += abs(iteration_result["flexible_loads.LVE.energy"])
        elec_supply = abs(iteration_result["PV_field_1.LVE.energy_sold"])
        elec_supply += abs(iteration_result["PV_field_2.LVE.energy_sold"])
        elec_supply += abs(iteration_result["WT_field_1.LVE.energy_sold"])
        elec_supply += abs(iteration_result["WT_field_2.LVE.energy_sold"])
        tot_elec_supply = iteration_result["electric_microgrid.energy_bought_inside"] + iteration_result["electric_microgrid.energy_bought_outside"]
        tot_heat_demand = iteration_result["district_heating_network.energy_sold_inside"]
        if tot_elec_supply != 0:
            EnR_ratio = elec_supply / tot_elec_supply
        else:
            EnR_ratio = 0.0
        if tot_heat_demand == 0:
            green_HP_heat_injected = 0.0
        elif iteration_result["heat_pump.LTH.energy_sold"] <= tot_heat_demand:  # todo patchwork solution to not reward the use of HP when TES is full
            green_HP_heat_injected = EnR_ratio * abs(iteration_result["heat_pump.LTH.energy_sold"]) / tot_heat_demand
            # green_HP_heat_injected = EnR_ratio * abs(iteration_result["heat_pump.LTH.energy_sold"])
        else:  # todo patchwork solution to not reward the use of HP when TES is full
            ref = 6910.33163265306
            green_HP_heat_injected = - abs(iteration_result["heat_pump.LTH.energy_sold"]) / ref
            # green_HP_heat_injected = - abs(iteration_result["heat_pump.LTH.energy_sold"])

        if EnR_ratio == 0 and abs(iteration_result["heat_pump.LTH.energy_sold"]) > 0:
            # ref = (1500 + 6910.33163265306) / 2
            ref = 6910.33163265306
            green_HP_heat_injected = - abs(iteration_result["heat_pump.LTH.energy_sold"]) / ref
            # green_HP_heat_injected = - abs(iteration_result["heat_pump.LTH.energy_sold"])

        # # Finally we compute the reward
        # if elec_supply > 0:
        #     # reward += beta_0 * abs(HP_value)
        #     if to_assign == agent_ID:
        #         reward += beta_0 * abs(HP_value)
        #     elif to_assign == "any":
        #         reward += 0.5 * beta_0 * abs(HP_value)
        #     else:
        #         reward = 0.0
        # else:
        #     # reward += - beta_0 * abs(HP_value)
        #     if to_assign == agent_ID:
        #         reward += - beta_0 * abs(HP_value)
        #     elif to_assign == "any":
        #         reward += - 0.5 * beta_0 * abs(HP_value)
        #     else:
        #         reward = 0.0

        reward += beta_0 * green_HP_heat_injected

        return reward

    return green_injection
