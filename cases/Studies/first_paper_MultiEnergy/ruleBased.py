# In this file, running the MARL mini-test case with defined rule based strategies
#######################################################################################################################
from pandas.core.computation.expressions import where
from supersuit import dtype_v0

from cases.Studies.first_paper_MultiEnergy.Parameters import ref_priorities_consumption_1, ref_priorities_production_1, ref_priorities_consumption_2, ref_priorities_production_2
from cases.Studies.first_paper_MultiEnergy.SimulationScript import create_simulation
import numpy as np

# my memory class
path_to_export = "cases/Studies/first_paper_MultiEnergy/Results/RBS"

comparison_simulation_length = 5304
performance_metrics = [
    "low_gas_price", "EnR_excess", "w2h_excess", "TES_full", "electric_microgrid.energy_bought_inside", "electric_microgrid.energy_bought_outside",
    "EMG_consumptions_priorities", "DHN_consumptions_priorities", "EMG_productions_priorities", "DHN_productions_priorities",
    "flexible_loads.LVE.energy_erased", "flexible_loads.LVE.money_spent",  # social cost (load satisfaction)
    "electric_microgrid.money_spent_outside", "electric_microgrid.money_earned_outside",  # exchange balance cost
    "combined_heat_power.LPG.money_spent",  # gas cost
    "Waste_to_heat.heat_dissipated", "Waste_to_heat.LTH.money",  # incinerator heat dissipation
    "combined_heat_power.LVE.energy_wanted", "combined_heat_power.LPG.energy_wanted", "electric_microgrid.LVE.energy_wanted",
    "combined_heat_power.heat_by_pass", "combined_heat_power.LTH.money",
    "heat_pump.LVE.energy_bought", "heat_pump.LVE.money_spent", "PV_field.LVE.energy_sold", "WT_field_1.LVE.energy_sold", "WT_field_2.LVE.energy_sold"  # HP green injection
                       ]

def performance_norm(performance_vector: dict) -> list:  # on peut bien évidemment prendre une norme plus complexe

    # Social cost
    load_erased_cost = np.array(performance_vector["flexible_loads.LVE.money_spent"])

    # HP green injection cost
    ENR_gen = np.array(performance_vector["PV_field.LVE.energy_sold"]) + np.array(performance_vector["WT_field_1.LVE.energy_sold"]) + np.array(performance_vector["WT_field_2.LVE.energy_sold"])
    # ENR_gen = ENR_gen != 0.0
    # ENR_gen = ENR_gen.astype(int)
    E_PAC = np.divide(ENR_gen, np.array(performance_vector["electric_microgrid.energy_bought_inside"]) + np.array(performance_vector["electric_microgrid.energy_bought_outside"]),
                      out=np.zeros_like(np.array(performance_vector["electric_microgrid.energy_bought_inside"]), dtype=float),
                      where=np.array(performance_vector["electric_microgrid.energy_bought_inside"]) + np.array(performance_vector["electric_microgrid.energy_bought_outside"]) !=0)
    E_PAC = E_PAC * np.array(performance_vector["heat_pump.LVE.energy_bought"])
    # HP_green_injection = np.array(performance_vector["heat_pump.LVE.energy_bought"]) * np.array(performance_vector["heat_pump.LVE.money_spent"]) * ENR_gen
    # HP_total_injection = np.array(performance_vector["heat_pump.LVE.energy_bought"]) * np.array(performance_vector["heat_pump.LVE.money_spent"])
    HP_green_injection = np.sum(E_PAC) / np.sum(np.array(performance_vector["heat_pump.LVE.energy_bought"]))

    # External electricity exchange balance
    elec_balance = np.array(performance_vector["electric_microgrid.money_earned_outside"]) - np.array(performance_vector["electric_microgrid.money_spent_outside"])

    # Wasted heat cost
    # heatSink_cost = np.array(performance_vector["combined_heat_power.heat_by_pass"]) * np.array(performance_vector["combined_heat_power.LTH.money"])  # CHP
    heatDissipated_cost = np.array(performance_vector["Waste_to_heat.heat_dissipated"]) * np.array(performance_vector["Waste_to_heat.LTH.money"])  # incinerator

    # CHP heat by pass
    CHP_heat_unused = np.array(performance_vector["combined_heat_power.heat_by_pass"]) * np.array(performance_vector["combined_heat_power.LTH.money"])

    # Gas cost
    gas_cost = np.array(performance_vector["combined_heat_power.LPG.money_spent"])

    # return [sum(elec_balance) - sum(gas_cost) - sum(load_erased_cost) - sum(heatSink_cost) - sum(heatDissipated_cost), sum(HP_green_injection) / sum(HP_total_injection)]
    return [sum(elec_balance) - sum(gas_cost) - sum(heatDissipated_cost) - sum(CHP_heat_unused), HP_green_injection]


ref_datalogger = create_simulation(comparison_simulation_length, [ref_priorities_consumption_1, ref_priorities_consumption_2],
                                   [ref_priorities_production_1, ref_priorities_production_2], f"comparison/reference", performance_metrics
                                   )
ref_results = {key: [] for key in performance_metrics}
for key in performance_metrics:
    ref_results[key] = ref_datalogger._values[key]
ref_performance = performance_norm(ref_results)

print(f"Performance of the reference strategy: {ref_performance}")