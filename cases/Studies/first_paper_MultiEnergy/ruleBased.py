# In this file, running the MARL mini-test case with defined rule based strategies
#######################################################################################################################
from cases.Studies.first_paper_MultiEnergy.Parameters import ref_priorities_consumption_1, ref_priorities_production_1, ref_priorities_consumption_2, ref_priorities_production_2
from cases.Studies.first_paper_MultiEnergy.SimulationScript import create_simulation

# my memory class
path_to_export = "cases/Studies/first_paper_MultiEnergy/Results/RBS"

comparison_simulation_length = 8760
performance_metrics = [
                       "Waste_to_heat.LTH.money_earned", "combined_heat_power.LPG.money_spent",
                       "electric_microgrid.money_spent_outside", "electric_microgrid.money_earned_outside",
                       ]

def performance_norm(performance_vector: dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
    return sum(performance_vector["electric_microgrid.money_earned_outside"]) - sum(performance_vector["electric_microgrid.money_spent_outside"]) - sum(performance_vector["Waste_to_heat.LTH.money_earned"]) - sum(performance_vector["combined_heat_power.LPG.money_spent"])


ref_datalogger = create_simulation(comparison_simulation_length, [ref_priorities_consumption_1, ref_priorities_consumption_2],
                                   [ref_priorities_production_1, ref_priorities_production_2], f"comparison/reference", performance_metrics
                                   )
ref_results = {key: [] for key in performance_metrics}
for key in performance_metrics:
    ref_results[key] = ref_datalogger._values[key]
ref_performance = performance_norm(ref_results)

print(f"Performance of the reference strategy: {ref_performance}")