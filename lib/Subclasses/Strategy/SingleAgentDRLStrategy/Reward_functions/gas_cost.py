# In this file, the template of reward functions is showcased for future reward functions to be defined !
# This specific reward function computes the costs at aggregator level (money earned and spent outside).
from typing import Dict, List

def define_my_Rt(beta_0: float):
    """
    :param beta_0: coefficient w.r.t penalty for not totally serving loads.
    """
    def gas_cost(iteration_result: Dict, metrics:List=None, agent_ID:str=None, action_reduction_dict:Dict=None):  # todo patchwork solution
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
            if "LPG" in metric or "priority" in metric or "combined_heat_power" in metric or "wanted" in metric:
                key_list.append(metric)

        # We then retrieve the correct value from the iteration dict
        reward = 0.0
        gas_price = 0.0
        gas_energy = 0.0
        dissipated_heat = 0.0
        wanted_gas = {}
        wanted_elec = {}
        wanted_heat = {}
        wanted_agg = {}
        wanted_h_agg = {}
        to_assign = ""
        srl_signal = True
        for key in key_list:
            if "LPG.money" in key:
                gas_price = iteration_result[key]
            elif "bought" in key:
                gas_energy = iteration_result[key]
            elif "priority" in key:
                srl_signal = False
                to_assign = (
                            "agent_1" if iteration_result[key] > 0
                            else "agent_2" if iteration_result[key] < 0
                            else "any"
                            )
            elif "LPG" in key and "wanted" in key:
                wanted_gas = iteration_result[key]
            elif "combined" in key and "LVE" in key:
                wanted_elec = iteration_result[key]
            elif "LTH" in key and "wanted" in key:
                wanted_heat = iteration_result[key]
            elif "microgrid" in key:
                wanted_agg = iteration_result[key]
            elif "district" in key:
                wanted_h_agg = iteration_result[key]
            elif "heat_by_pass" in key:
                dissipated_heat = iteration_result[key]

        # Finally we compute the reward
        gas_energy = wanted_gas["energy_nominal"]
        if gas_energy != 0.0:
            elec_CHP_price = wanted_gas["price"] / wanted_elec["efficiency"]
            heat_CHP_price = (wanted_gas["price"] / wanted_heat["efficiency"]) * abs(dissipated_heat / wanted_heat["energy_nominal"])
            reward += beta_0 * abs(gas_energy) / 16000.0
        else:
            elec_CHP_price = 0.0
            heat_CHP_price = 0.0
            reward = 0.0


        # if gas_price != 0.0:
        #     if not srl_signal:
        #         if to_assign == agent_ID:
        #             reward += - beta_0 * abs((gas_price * gas_energy) / (gas_price * 16000.0))
        #         elif to_assign == "any":
        #             reward += - 0.5 * beta_0 * abs((gas_price * gas_energy) / (gas_price * 16000.0))
        #         else:
        #             reward = 0.0
        #     else:
        #         reward = beta_0 * abs(gas_price) / (0.16 * 16000)
                # reward = beta_0 * abs(gas_price)
            # reward += - beta_0 * abs((gas_price * gas_energy) / (gas_price * 16000.0))

        if elec_CHP_price < wanted_agg[0]['price'] and heat_CHP_price < wanted_h_agg[0]['price']:  # price for gas is advantageous % main grid
            # reward -= 0.5 * reward
            reward = reward * 1
        else:
            # reward += 0.5 * reward
            reward = reward * (-1)

        return reward

    return gas_cost
