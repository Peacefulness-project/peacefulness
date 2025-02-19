from skopt import gp_minimize
import shutil
from cases.Studies.ClusteringAndStrategy.Utilities import *
import pygad
import math

def training(simulation_length: int, cluster_centers: List, performance_norm: Callable, performance_metrics: List, assessed_priorities: Dict, create_simulation: Callable, case_name: str, clustering_metrics: List) -> Dict:
    # performance assessment phase
    print("identification of the relevant strategy for each cluster")
    research_method = bricolage
    best_strategies = research_method(cluster_centers, simulation_length,
                                      performance_metrics, performance_norm, assessed_priorities,
                                      create_simulation, case_name, clustering_metrics)
    print("Done\n")

    print("\n\n")
    print(f"best couples clusters/strategies:")
    for cluster, strategy in best_strategies.items():
        print(cluster, strategy)
    print("\n\n")

    return best_strategies


# def systematic_test(cluster_center_start_dates: List, simulation_length: int, performance_metrics: List, performance_norm: Callable, assessed_priorities: Dict[str, List], create_simulation: Callable, case_name: str) -> Tuple:
#     assessed_priorities_consumption = assessed_priorities["consumption"]
#     assessed_priorities_production = assessed_priorities["production"]
#
#     for cluster_center in cluster_center_start_dates:
#         performances_record = PerformanceRecord([cluster_center])
#         for i in range(len(assessed_priorities_consumption)):
#             for j in range(len(assessed_priorities_production)):
#                 # simulation
#                 def priorities_consumption(strategy: "Strategy"):
#                     return assessed_priorities_consumption[i]
#
#                 def priorities_production(strategy: "Strategy"):
#                     return assessed_priorities_production[j]
#
#                 print(f"test of strategy {assessed_priorities_consumption[i]}/{assessed_priorities_production[j]}")
#                 directory = f"training/{i}_{j}"
#                 datalogger = create_simulation(simulation_length, priorities_consumption,  priorities_production, directory, performance_metrics, delay_days=cluster_center)
#                 shutil.rmtree(f"cases/Studies/ClusteringAndStrategy/Results/{case_name}/training/", ignore_errors=False, onerror=None)
#
#                 # metering
#                 raw_outputs = {}
#                 for key in performance_metrics:
#                     raw_outputs[key] = datalogger.get_values(key)
#
#                 performance = performance_norm(raw_outputs)
#                 print(f"performance reached: {performance}")
#
#                 performances_record.add_to_record([assessed_priorities_consumption[i], assessed_priorities_production[j]], 0, performance)
#                 print()
#
#     # selection
#     performance, strategy_indices = performances_record.sort_strategies(0)[0]
#     best_strategy = (performance, {"consumption": strategy_indices[0], "production": strategy_indices[1]})
#     print(f"best strategy performance: {best_strategy[0]}")
#     print(f"best strategy name: {best_strategy[1]}")
#
#     return best_strategy


# def bayesian_search(cluster_center_start_dates: List, simulation_length: int, performance_metrics: List, performance_norm: Callable, assessed_priorities: Dict[str, List], create_simulation: Callable, case_name: str) -> Tuple:
#     assessed_priorities_consumption = assessed_priorities["consumption"]
#     assessed_priorities_production = assessed_priorities["production"]
#     consumption_options_number = len(assessed_priorities_consumption[0])
#     production_options_number = len(assessed_priorities_production[0])
#
#     # black box function for bayesian search
#     def function_to_optimize(priorities_indices: Tuple):
#         def priorities_consumption(strategy: "Strategy"):
#             return assessed_priorities_consumption[priorities_indices[0]]
#
#         def priorities_production(strategy: "Strategy"):
#             return assessed_priorities_production[priorities_indices[1]]
#         datalogger = create_simulation(simulation_length, priorities_consumption, priorities_production,
#                                        f"training/", performance_metrics)
#         shutil.rmtree(f"cases/Studies/ClusteringAndStrategy/Results/{case_name}/training/", ignore_errors=False, onerror=None)
#         raw_outputs = {}
#         for key in performance_metrics:
#             raw_outputs[key] = datalogger.get_values(key)
#
#     performance = performance_norm(raw_outputs)
#
#     return -performance  # "-" because the function tries to minimize
#
# # bounds correspond to indices of arrangement
# bounds = [(0, consumption_options_number-1),  # consumption bounds
#           (0, production_options_number-1)]  # production bounds
#
# results = gp_minimize(func=function_to_optimize,
#                       dimensions=bounds,
#                       n_calls=10,
#                       n_random_starts=5,
#                       # random_state=,
#                       verbose=False,
#                       )
# consumption_strategy = assessed_priorities_consumption[results.x[0]]
# production_strategy = assessed_priorities_production[results.x[1]]
# best_strategy = (results.fun, {"consumption": consumption_strategy, "production": production_strategy})
# print(f"{best_strategy}\n")
#
# return best_strategy

def bricolage(cluster_centers: List, simulation_length: int, performance_metrics: List, performance_norm: Callable, assessed_priorities: Dict[str, List], create_simulation: Callable, case_name: str, clustering_metrics: List) -> Dict:
    """
    Clusters are sorted by the number of days inside.
    For the cluster i, all the strategies are tested knowing that:
    - clusters < i (the less populous) use the best strategies identified
    - clusters > i (the more populous) use a random strategy

    Parameters
    ----------
    cluster_centers
    simulation_length
    performance_metrics
    performance_norm
    assessed_priorities
    create_simulation
    case_name
    clustering_metrics

    Returns
    -------

    """
    assessed_priorities_consumption = assessed_priorities["consumption"]
    assessed_priorities_production = assessed_priorities["production"]
    random_priorities_consumption = random_order_priorities(assessed_priorities_consumption[0])
    random_priorities_production = random_order_priorities(assessed_priorities_production[0])
    best_strategies = {}

    def find_cluster(strategy: "Strategy"):
        current_situation = [strategy._catalog.get(key) for key in clustering_metrics]
        distance_min = math.inf
        for i in range(len(cluster_centers)):
            center = cluster_centers[i]
            distance = sum([(center[j] - current_situation[j]) ** 2 for j in range(len(center))])
            if distance < distance_min:
                distance_min = distance
                cluster_id = i
        return cluster_id

    for k in range(len(cluster_centers)):
        performances_record = PerformanceRecord([k])
        for i in range(len(assessed_priorities_consumption)):
            for j in range(len(assessed_priorities_production)):
                def priorities_consumption(strategy: "Strategy"):
                    cluster_id = find_cluster(strategy)
                    if cluster_id < k:
                        return best_strategies[cluster_id][1]["consumption"]
                    elif cluster_id == k:
                        return assessed_priorities_consumption[i]
                    else:
                        return random_priorities_consumption(strategy)

                def priorities_production(strategy: "Strategy"):
                    cluster_id = find_cluster(strategy)
                    if cluster_id < k:
                        return best_strategies[cluster_id][1]["production"]
                    elif cluster_id == k:
                        return assessed_priorities_production[j]
                    else:
                        return random_priorities_production(strategy)

                # simulation
                print(f"test of strategy {assessed_priorities_consumption[i]}/{assessed_priorities_production[j]}")
                directory = f"training/{i}_{j}"
                datalogger = create_simulation(simulation_length, priorities_consumption,  priorities_production, directory, performance_metrics)
                shutil.rmtree(f"cases/Studies/ClusteringAndStrategy/Results/{case_name}/training/", ignore_errors=False, onerror=None)

                # metering
                raw_outputs = {}
                for key in performance_metrics:
                    raw_outputs[key] = datalogger.get_values(key)

                performance = performance_norm(raw_outputs)
                print(f"performance reached: {performance}")

                performances_record.add_to_record([assessed_priorities_consumption[i], assessed_priorities_production[j]], 0, performance)
                print()

        # selection
        performance, strategy_indices = performances_record.sort_strategies(0)[0]  # the maximum value is retained
        best_strategies[k] = (performance, {"consumption": strategy_indices[0], "production": strategy_indices[1]})
        print(f"best strategy performance: {best_strategies[k][0]}")
        print(f"best strategy name: {best_strategies[k][1]}")
        print(best_strategies)

    return best_strategies

