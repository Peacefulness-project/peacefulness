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


def assess_performance(find_strategy_consumption: Callable, find_strategy_production: Callable,
                       comparison_simulation_length: int, performance_norm: Callable,
                       performance_metrics: List, create_simulation: Callable, complement_path: str):

    # improved run
    cluster_along_time = {}

    print(f"start of the (presumably) better run")
    tested_datalogger = create_simulation(comparison_simulation_length, find_strategy_consumption, find_strategy_production, f"{complement_path}/comparison/improved", performance_metrics,
                                          random_seed=seed, standard_deviation=0.15)
    tested_results = {key: [] for key in performance_metrics}
    for key in performance_metrics:
        tested_results[key] = tested_datalogger._values[key]
    tested_performance = performance_norm(tested_results)
    print("Done\n")

    print(f"Performance of the improved strategy: {tested_performance}")

    return tested_performance, cluster_along_time