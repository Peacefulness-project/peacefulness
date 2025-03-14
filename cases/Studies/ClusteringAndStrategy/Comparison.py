from typing import List, Dict, Callable
import math
seed = 0


def assess_reference(
        comparison_simulation_length: int, performance_norm: Callable,
        ref_priorities_consumption: Callable, ref_priorities_production: Callable,
        performance_metrics: List, create_simulation: Callable):

    # reference run
    print(f"start of the reference run")
    ref_datalogger = create_simulation(comparison_simulation_length, ref_priorities_consumption, ref_priorities_production, f"comparison/reference", performance_metrics,
                                       random_seed=seed, standard_deviation=0.15)
    ref_results = {key: [] for key in performance_metrics}
    for key in performance_metrics:
        ref_results[key] = ref_datalogger._values[key]
    ref_performance = performance_norm(ref_results)
    print("Done\n")

    print(f"Performance of the reference strategy: {ref_performance}")

    return ref_performance


def assess_performance(best_strategies: Dict, cluster_centers: List, clustering_metrics: List,
                       comparison_simulation_length: int, performance_norm: Callable,
                       performance_metrics: List, create_simulation: Callable, complement_path: str):

    # improved run
    cluster_along_time = {}
    def find_strategy(cons_or_prod: str):
        def find(strategy: "Strategy"):  # function identifying the cluster and the relevant strategy
            current_situation = [strategy._catalog.get(key) for key in clustering_metrics]
            distance_min = math.inf
            for i in range(len(cluster_centers)):
                center = cluster_centers[i]
                distance = sum([(center[j] - current_situation[j]) ** 2 for j in range(len(center))])
                if distance < distance_min:
                    cluster_id = i
                    distance_min = distance
                    ordered_list = best_strategies[i][1]
            iteration = strategy._catalog.get("simulation_time")
            if iteration >= len(cluster_along_time):
                time = strategy._catalog.get("physical_time")
                cluster_along_time[time] = cluster_id
            return ordered_list[cons_or_prod]
        return find

    print(f"start of the (presumably) better run")
    tested_datalogger = create_simulation(comparison_simulation_length, find_strategy("consumption"), find_strategy("production"), f"{complement_path}/comparison/improved", performance_metrics,
                                          random_seed=seed, standard_deviation=0.15)
    tested_results = {key: [] for key in performance_metrics}
    for key in performance_metrics:
        tested_results[key] = tested_datalogger._values[key]
    tested_performance = performance_norm(tested_results)
    print("Done\n")

    print(f"Performance of the improved strategy: {tested_performance}")

    return tested_performance, cluster_along_time

