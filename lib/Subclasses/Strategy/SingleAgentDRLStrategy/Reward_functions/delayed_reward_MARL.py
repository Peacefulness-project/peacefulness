# In this file, the template of reward functions is showcased for future reward functions to be defined !
from typing import Dict, List
import numpy as np

def MARL_MECS_Rt(rewards: Dict, metrics: Dict, worst_scenario: Dict):
    """
    *args : the necessary arguments to define the reward function we want to use
    """
    # 1st objective - reducing the OPEX of the electric MG and the DHN.
    bought_out = 0.0
    sold_out = 0.0
    erased_energy = []
    erased_price = []
    erased_costs = 0.0
    gas_energy = []
    gas_price = []
    gas_costs = 0.0
    CHP_heat_sink_energy = []
    CHP_heat_sink_price = []
    heat_sink_costs = 0.0
    rigid_consumption = []
    green_supply = np.zeros_like(next(iter(metrics.values())))
    HP_elec_injection = []
    HP_heat_injection = []
    HP_elec_money = []
    HP_heat_money = []
    artificial_DHN_energy = []
    artificial_DHN_money = []
    for key in metrics:
        if "spent_outside" in key:
            bought_out = sum(metrics[key])
        elif "earned_outside" in key:
            sold_out = sum(metrics[key])
        elif "energy_erased" in key:
            erased_energy = abs(np.array(metrics[key]))
        elif "flexible_loads" in key and "money" in key:
            erased_price = np.array(metrics[key])
        elif "LPG.energy_bought" in key:
            gas_energy = abs(np.array(metrics[key]))
        elif "LPG" in key and "money" in key:
            gas_price = abs(np.array(metrics[key]))
        elif "by_pass" in key:
            CHP_heat_sink_energy = abs(np.array(metrics[key]))
        elif "combined" in key and "LTH.money" in key:
            CHP_heat_sink_price = np.array(metrics[key])
        elif "rigid" in key and "energy" in key:
            rigid_consumption = abs(np.array(metrics[key]))
        elif ("PV" in key and "energy" in key) or  ("WT" in key and "energy" in key):
            green_supply += abs(np.array(metrics[key]))
        elif "pump" in key and "energy_bought" in key:
            HP_elec_injection = abs(np.array(metrics[key]))
        elif "pump" in key and "energy_sold" in key:
            HP_heat_injection = abs(np.array(metrics[key]))
        elif "pump" in key and "LVE.money" in key:
            HP_elec_money = np.array(metrics[key])
        elif "pump" in key and "LTH.money" in key:
            HP_heat_money = np.array(metrics[key])
        elif "artificial" in key and "LTH.energy" in key:
            artificial_DHN_energy = np.array(metrics[key])
        elif "artificial" in key and "LTH.money" in key:
            artificial_DHN_money = np.array(metrics[key])

    erased_costs = sum(erased_energy * erased_price)
    gas_costs = sum(gas_energy * gas_price)
    heat_sink_costs = sum(CHP_heat_sink_energy * CHP_heat_sink_price)
    exchange_costs = sold_out - bought_out
    artificial_DHN_costs = sum(artificial_DHN_energy * artificial_DHN_money)
    overall_costs = exchange_costs - erased_costs - (gas_costs + heat_sink_costs) * 0.5 - artificial_DHN_costs * 0.5


    # 2nd objective - ensuring HP green energy injection.
    green_rt = 0.0
    penalty_rt = 0.0
    green_diff = green_supply - rigid_consumption
    green_good = green_diff >= 0
    green_bad = green_diff < 0
    green_good = green_good.astype(int)
    green_bad = green_bad.astype(int)
    green_injection = green_good * HP_elec_injection
    green_money = green_good * (HP_elec_injection * HP_elec_money + HP_heat_injection * HP_heat_money) / 2
    not_green_money = green_bad * (HP_elec_injection * HP_elec_money + HP_heat_injection * HP_heat_money) / 2
    # if sum(green_injection) / sum(HP_elec_injection) > 0.85:
    #     green_rt = sum(green_money)
    # else:
    #     penalty_rt = - sum(not_green_money)
    green_rt = sum(green_money)
    penalty_rt = - sum(not_green_money)

    # Rewards assignment
    rewards["agent_1"] += overall_costs + (green_rt + penalty_rt) * 0.5
    rewards["agent_1"] /= (worst_scenario["agent_1"])
    rewards["agent_2"] += (green_rt + penalty_rt) * 0.5 - (gas_costs + heat_sink_costs) * 0.5 - artificial_DHN_costs * 0.5
    rewards["agent_2"] /= (worst_scenario["agent_2"])

    return rewards