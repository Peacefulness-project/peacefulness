from random import shuffle
from typing import *


def random_order_priorities_conso():
    ordered_list = ["store", "soft_DSM_conso", "hard_DSM_conso", "buy_outside_emergency"]
    shuffle(ordered_list)
    def random_priorities(strategy: "Strategy"):
            return ordered_list
    return random_priorities


def random_order_priorities_prod():
    ordered_list = ["soft_DSM_prod", "hard_DSM_prod", "sell_outside_emergency", "unstore"]
    shuffle(ordered_list)
    def random_priorities(strategy: "Strategy"):
        return ordered_list
    return random_priorities


class PerformanceRecord:  # records of performances observed for the different strategies applied to a cluster type
    def __init__(self, cluster_center_start_date: List):
        self._records: Dict = {i: {"center": cluster_center_start_date[i], "assessed_strategy": [], "performance": []} for i in range(len(cluster_center_start_date))}

    def add_to_record(self, assessed_strategy: str, cluster_center: int, performance: Dict):
        self._records[cluster_center]["assessed_strategy"].append(assessed_strategy)
        self._records[cluster_center]["performance"].append(performance)

    def sort_strategies(self, center: int) -> List[Tuple]:
        strategies = self._records[center]["assessed_strategy"]
        performances = self._records[center]["performance"]
        unsorted_couples = [(performances[i], strategies[i]) for i in range(len(strategies))]

        def get_perf(truc: Tuple):
            return truc[0]

        sorted_couples = sorted(unsorted_couples, key=get_perf, reverse=True)
        return sorted_couples

    @property
    def centers(self):
        return self._records.keys()

    @property
    def records(self):
        return self._records



