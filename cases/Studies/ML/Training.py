from typing import *
from numpy import sqrt
from skopt import gp_minimize
import itertools

from cases.Studies.ML. SimulationScript import create_simulation
from cases.Studies.ML.Utilities import *


def training(simulation_length: int, cluster_center_start_dates: List, performance_norm: Callable, performance_metrics: List) -> Dict:
    # performance assessment phase

    print("identification of the relevant strategy for each cluster")
    best_strategies = {}
    research_method = systematic_test
    for cluster_center in cluster_center_start_dates:
        print(f"strategy search for cluster {cluster_center}")
        best_strategies[cluster_center] = research_method(cluster_center, simulation_length,
                                                          performance_metrics, performance_norm)
    print("Done\n")

    print("\n\n")
    # print(f"performance record: {performances_record.records}")
    print(f"best couples clusters/strategies: {best_strategies}")
    print("\n\n")

    return best_strategies


consumption_options = ['store', 'soft_DSM_conso', 'buy_outside_emergency', 'hard_DSM_conso']
production_options = ['unstore', 'soft_DSM_prod', 'sell_outside_emergency', 'hard_DSM_prod']
# assessed_priorities_consumption = [list(toto) for toto in itertools.permutations(consumption_options)]
# assessed_priorities_production = [list(toto) for toto in itertools.permutations(production_options)]
assessed_priorities_consumption = [consumption_options]
assessed_priorities_production = [production_options]


def systematic_test(cluster_center_start_date: int, simulation_length: int, performance_metrics: List, performance_norm: Callable) -> Tuple:
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
    best_strategy = performances_record.sort_strategies(0)[0]
    print(f"best strategy performance: {best_strategy[0]}")
    print(f"best strategy name: {best_strategy[1]}")
    print(best_strategy)

    return best_strategy


def bayesian_search(cluster_center_start_date: int, simulation_length: int, performance_metrics: List, performance_norm: Callable) -> Tuple:

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
    bounds = [(0, len(consumption_options)),  # consumption bounds
              (0, len(production_options))]    # production bounds

    results = gp_minimize(func=function_to_optimize,
                          dimensions=bounds,
                          n_calls=10,
                          n_random_starts=5,
                          # random_state=,
                          verbose=True,
                          )
    print(results.x)
    print(results.fun)
    print("\n\n")
    best_strategy = (results.fun, )

    return best_strategy

