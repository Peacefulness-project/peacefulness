# In this file, running the MARL mini-test case with defined rule based strategies
#######################################################################################################################
from cases.Studies.MultiAgent_RL.Parameters import ref_priorities_consumption_1, ref_priorities_production_1, ref_priorities_consumption_2, ref_priorities_production_2
from cases.Studies.MultiAgent_RL.SimulationScript import create_simulation

# my memory class
path_to_export = "cases/Studies/MultiAgent_RL/Results/RBS"

comparison_simulation_length = 8759
performance_metrics = [
                        "residential_dwellings.LVE.energy_erased",
                       "industrial_process.LVE.energy_erased",
                       "local_community_1.energy_bought_outside",
                       "local_community_2.energy_bought_outside",
                       "local_community_1.energy_sold_outside",
                       "local_community_2.energy_sold_outside"
                       ]
coef1 = 1
coef2 = 1
coef3 = 1
def performance_norm(performance_vector: dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
    return (
            (abs(sum(performance_vector["local_community_1.energy_sold_outside"])) - abs(sum(performance_vector["local_community_1.energy_bought_outside"]))) * coef1
            + (abs(sum(performance_vector["local_community_2.energy_sold_outside"])) - abs(sum(performance_vector["local_community_2.energy_bought_outside"]))) * coef2
            - (abs(sum(performance_vector["residential_dwellings.LVE.energy_erased"])) + abs(sum(performance_vector["industrial_process.LVE.energy_erased"]))) * coef3
            )


ref_datalogger = create_simulation(comparison_simulation_length, [ref_priorities_consumption_1, ref_priorities_consumption_2],
                                   [ref_priorities_production_1, ref_priorities_production_2], f"comparison/reference", performance_metrics
                                   )
ref_results = {key: [] for key in performance_metrics}
for key in performance_metrics:
    ref_results[key] = ref_datalogger._values[key]
ref_performance = performance_norm(ref_results)

print(f"Performance of the reference strategy: {ref_performance}")