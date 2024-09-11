from typing import List, Dict, Callable
import math


def comparison(best_strategies: Dict, cluster_centers: List, center_days: List, clustering_metrics: List,
               comparison_simulation_length: int, performance_norm: Callable,
               assessed_priorities: Dict, ref_priorities_consumption: Callable, ref_priorities_production: Callable,
               performance_metrics: List, create_simulation: Callable):

    def find_strategy(cons_or_prod: str):
        def find(strategy: "Strategy"):  # function identifying the cluster and the relevant strategy
            current_situation = [strategy._catalog.get(key) for key in clustering_metrics]
            distance_min = math.inf
            for i in range(len(cluster_centers)):
                center = cluster_centers[i]
                distance = sum([(center[j] - current_situation[j]) ** 2 for j in range(len(center))])
                if distance < distance_min:
                    distance_min = distance
                    ordered_list = best_strategies[center_days[i]][1]
            return ordered_list[cons_or_prod]
        return find

    # reference run
    print(f"start of the reference run")
    ref_datalogger = create_simulation(comparison_simulation_length, ref_priorities_consumption, ref_priorities_production, f"comparison/reference", performance_metrics)
    ref_results = {key: [] for key in performance_metrics}
    for key in performance_metrics:
        ref_results[key] = ref_datalogger._values[key]
    ref_performance = performance_norm(ref_results)
    print("Done\n")

    # improved run
    print(f"start of the (presumably) better run")
    tested_datalogger = create_simulation(comparison_simulation_length, find_strategy("consumption"), find_strategy("production"), f"comparison/improved", performance_metrics)
    tested_results = {key: [] for key in performance_metrics}
    for key in performance_metrics:
        tested_results[key] = tested_datalogger._values[key]
    tested_performance = performance_norm(tested_results)
    print("Done\n")

    print(f"Performance of the reference strategy: {ref_performance}")
    print(f"Performance of the improved strategy: {tested_performance}")

