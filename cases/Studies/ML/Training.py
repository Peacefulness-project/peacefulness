from typing import *
from numpy import sqrt

from cases.Studies.ML. SimulationScript import create_simulation
from cases.Studies.ML.Utilities import *


def training(simulation_length: int, cluster_center_start_date: List, performance_norm: Callable, assessed_priorities:Dict):
    # performance assessment phase
    performances_record = PerformanceRecord(cluster_center_start_date)
    performance_metrics = [
                           "general_aggregator.coverage_rate",
    ]

    print("identification of the relevant strategy for each cluster")
    for i in range(len(cluster_center_start_date)):
        print(f"strategy search for cluster {i}")
        for priority_name in assessed_priorities:
            print(f"test of strategy {priority_name}")
            assessed_priority = assessed_priorities[priority_name]
            world = create_simulation(simulation_length, assessed_priority["consumption"],  assessed_priority["production"], f"training/{str(assessed_priority)}", performance_metrics, delay_days=cluster_center_start_date[i])

            datalogger = world.catalog.dataloggers["metrics"]
            raw_outputs = {}
            for key in performance_metrics:
                raw_outputs[key] = datalogger._values[key]

            # self_sufficiency_datalogger = world.catalog.dataloggers["self_sufficiency_frequency_1"]
            # curtailment_datalogger = world.catalog.dataloggers["curtailment_rate_frequency_1"]
            # aggregator_datalogger = world.catalog.dataloggers["aggregator_balances_frequency_1"]
            performance = performance_norm(raw_outputs)
            print(f"performance reached: {performance}")

            performances_record.add_to_record(priority_name, i, performance)
        print()

    # strategy assignation phase
    best_strategies = {}
    for center in performances_record.centers:
        best_strategies[center] = performances_record.sort_strategies(center)[0]

    print("\n\n")
    print(f"performance record: {performances_record.records}")
    print(f"best couples clusters/strategies: {best_strategies}")
    print("\n\n")

    return best_strategies, performances_record



