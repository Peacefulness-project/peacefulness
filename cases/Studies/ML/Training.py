from skopt import gp_minimize

from cases.Studies.ML.CasesStudied.Test.SimulationScript import create_simulation
from cases.Studies.ML.Utilities import *


def training(simulation_length: int, cluster_center_start_dates: List, performance_norm: Callable, performance_metrics: List, assessed_priorities: Dict) -> Dict:
    # performance assessment phase
    print("identification of the relevant strategy for each cluster")
    best_strategies = {}
    research_method = bayesian_search
    for cluster_center in cluster_center_start_dates:
        print(f"strategy search for cluster {cluster_center}")
        best_strategies[cluster_center] = research_method(cluster_center, simulation_length,
                                                          performance_metrics, performance_norm, assessed_priorities)
    print("Done\n")

    print("\n\n")
    print(f"best couples clusters/strategies: {best_strategies}")
    print("\n\n")

    return best_strategies


def systematic_test(cluster_center_start_date: int, simulation_length: int, performance_metrics: List, performance_norm: Callable, assessed_priorities: Dict[str, List]) -> Tuple:
    assessed_priorities_consumption = assessed_priorities["consumption"]
    assessed_priorities_production = assessed_priorities["production"]

    performances_record = PerformanceRecord([cluster_center_start_date])
    for i in range(len(assessed_priorities_consumption)):
        for j in range(len(assessed_priorities_production)):
            # simulation
            def priorities_consumption(strategy: "Strategy"):
                return assessed_priorities_consumption[i]

            def priorities_production(strategy: "Strategy"):
                return assessed_priorities_production[j]

            print(f"test of strategy {i}/{j}")
            datalogger = create_simulation(simulation_length, priorities_consumption,  priorities_production, f"training/{i}_{j}", performance_metrics, delay_days=cluster_center_start_date)

            # metering
            raw_outputs = {}
            for key in performance_metrics:
                raw_outputs[key] = datalogger.get_values(key)

            performance = performance_norm(raw_outputs)
            print(f"performance reached: {performance}")

            performances_record.add_to_record([assessed_priorities_consumption[i], assessed_priorities_production[i]], 0, performance)
            print()

    # selection
    performance, strategy_indices = performances_record.sort_strategies(0)[0]
    best_strategy = (performance,
                     [strategy_indices[0], strategy_indices[1]]
                     )
    print(f"best strategy performance: {best_strategy[0]}")
    print(f"best strategy name: {best_strategy[1]}")

    return best_strategy


def bayesian_search(cluster_center_start_date: int, simulation_length: int, performance_metrics: List, performance_norm: Callable, assessed_priorities: Dict[str, List]) -> Tuple:
    assessed_priorities_consumption = assessed_priorities["consumption"]
    assessed_priorities_production = assessed_priorities["production"]
    consumption_options_number = len(assessed_priorities_consumption[0])
    production_options_number = len(assessed_priorities_production[0])

    # black box function for bayesian search
    def function_to_optimize(priorities_indices: Tuple):
        def priorities_consumption(strategy: "Strategy"):
            return assessed_priorities_consumption[priorities_indices[0]]

        def priorities_production(strategy: "Strategy"):
            return assessed_priorities_production[priorities_indices[1]]
        datalogger = create_simulation(simulation_length, priorities_consumption, priorities_production,
                                       f"training/", performance_metrics, delay_days=cluster_center_start_date)
        raw_outputs = {}
        for key in performance_metrics:
            raw_outputs[key] = datalogger.get_values(key)

        performance = performance_norm(raw_outputs)

        return -performance  # "-" because the function tries to minimize

    # bounds correspond to indices of arrangement
    bounds = [(0, consumption_options_number),  # consumption bounds
              (0, production_options_number)]  # production bounds

    results = gp_minimize(func=function_to_optimize,
                          dimensions=bounds,
                          n_calls=10,
                          n_random_starts=5,
                          # random_state=,
                          verbose=False,
                          )
    consumption_strategy = assessed_priorities_consumption[results.x[0]]
    production_strategy = assessed_priorities_production[results.x[1]]
    best_strategy = (results.fun, [consumption_strategy, production_strategy])
    print(f"{best_strategy}\n")

    return best_strategy

