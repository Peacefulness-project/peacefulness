from random import shuffle
from typing import *
from math import factorial
import copy


def random_order_priorities(priorities_list: List) -> Callable:
    shuffle(priorities_list)

    def random_priorities(strategy: "Strategy") -> List:
        return priorities_list
    return random_priorities


def permute(container: List) -> List[List]:
    """
    Returns all the permutations possible from a list, in an order guaranteeing that each successive permutation is obtained by permuting only 2 elements of the previous permutation.

    Parameters
    ----------
    container: List, the list from which permutations are created

    Returns
    -------
    permutation_list: List[List], a list containing all the permutations

    """
    permutation_list = []  # the list of permutations
    permutation = container
    list_size = len(container)
    j = 0
    k = 1
    for i in range(factorial(list_size)):
        permutation[j], permutation[k] = permutation[k], permutation[j]
        if j < k:  # if we are going crescent
            if k == list_size - 1:  # if we reach the end of the list, we start decreasing
                k -= 2
            else:  # we keep increasing
                j += 1
                k += 1
        else:
            if k == 0:  # if we reach the start of the list, we strat increasing
                k += 2
            else:  # we keep decreasing
                j -= 1
                k -= 1
        permutation_list.append(copy.deepcopy(permutation))

    return permutation_list


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


class MultiPerformanceRecord:  # records of performances observed for the different strategies applied to a cluster type
    def __init__(self):
        self._strategy_records: List = []
        self._performance_records: List = []

    def add_to_record(self, assessed_strategies, performance: Dict):
        self._strategy_records.append(assessed_strategies)
        self._performance_records.append(performance)

    def sort_strategies(self) -> List:
        unsorted_couples = [(self._performance_records[i], self._strategy_records[i]) for i in range(len(self._performance_records))]

        def get_perf(run_record: Tuple):
            return run_record[0]

        sorted_couples = sorted(unsorted_couples, key=get_perf, reverse=True)
        sorted_performance = (sorted_couple[0] for sorted_couple in sorted_couples)
        sorted_strategies = (sorted_couple[1] for sorted_couple in sorted_couples)

        return sorted_couples

