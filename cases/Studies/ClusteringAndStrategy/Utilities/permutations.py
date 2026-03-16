from typing import List
from math import factorial
import copy


def permute(container: List) -> List[List]:
    """
    Returns all the permutations possible from a list, in an order guaranteeing that each successive permutation is obtained by permuting only 2 elements of the previous permutation.

    Parameters
    ----------
    container: List, the list from which permutations are created

    Returns
    -------

    """
    permutation_list = []  # the list of permutations
    permutation = container
    list_size = len(container)
    j = 0
    k = 1
    for i in range(factorial(list_size)):
        print(j, k)
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


