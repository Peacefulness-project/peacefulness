# In this file, running the MARL mini-test case with defined rule based strategies
#######################################################################################################################
from cases.Studies.MultiAgent_RL.Parameters import ref_priorities_consumption_1, ref_priorities_production_1, ref_priorities_consumption_2, ref_priorities_production_2
from cases.Studies.MultiAgent_RL.SimulationScript import create_simulation

# my memory class
path_to_export = "cases/Studies/MultiAgent_RL/Results/RBS"

comparison_simulation_length = 8759
performance_metrics = [
                       "residential_dwellings.LVE.energy_erased", "residential_dwellings.LVE.money_spent", "residential_dwellings.LVE.energy_bought",
                       "industrial_process.LVE.energy_erased", "industrial_process.LVE.money_spent", "industrial_process.LVE.energy_bought",
                       "community_1.money_spent", "community_2.money_spent",
                       "community_1.money_earned", "community_2.money_earned"
                       ]
coef1 = 1
coef2 = 1
coef3 = 1
def performance_norm(performance_vector: dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
    resi_price = [performance_vector["residential_dwellings.LVE.money_spent"][i] / performance_vector["residential_dwellings.LVE.energy_bought"][i] for i in range(len(performance_vector["residential_dwellings.LVE.energy_bought"]))]
    res_erased = [resi_price[idx] * performance_vector["residential_dwellings.LVE.energy_erased"][idx] for idx in range(len(resi_price))]
    indus_price = [performance_vector["industrial_process.LVE.money_spent"][i] / performance_vector["industrial_process.LVE.energy_bought"][i] for i in range(len(performance_vector["industrial_process.LVE.energy_bought"]))]
    indus_erased = [indus_price[idx] * performance_vector["industrial_process.LVE.energy_erased"][idx] for idx in range(len(indus_price))]
    return (
            (abs(sum(performance_vector["community_1.money_earned"])) - abs(sum(performance_vector["community_1.money_spent"]))) * coef1
            + (abs(sum(performance_vector["community_1.money_earned"])) - abs(sum(performance_vector["community_2.money_spent"]))) * coef2
            - (abs(sum(res_erased)) + abs(sum(indus_erased))) * coef3
            )


ref_datalogger = create_simulation(comparison_simulation_length, [ref_priorities_consumption_1, ref_priorities_consumption_2],
                                   [ref_priorities_production_1, ref_priorities_production_2], f"comparison/reference", performance_metrics
                                   )
ref_results = {key: [] for key in performance_metrics}
for key in performance_metrics:
    ref_results[key] = ref_datalogger._values[key]
ref_performance = performance_norm(ref_results)

print(f"Performance of the reference strategy: {ref_performance}")