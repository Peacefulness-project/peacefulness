# This sheet describes a strategy always refusing to trade with other
# It can correspond to the strategy of an island, for example
from lib.Subclasses.Strategy.BiddingStrategy.BiddingStrategy import BiddingStrategy
from typing import Callable, Dict, List
import math


class NaiveBidStrategy(BiddingStrategy):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def create_bids(self, minimum_energy_consumed: float, maximum_energy_consumed: float, minimum_energy_produced: float, maximum_energy_produced: float, maximum_energy_charge: float, maximum_energy_discharge: float) -> List[Dict]:
        bids = []

        # minimum management: a first bid to make sure the grid can deliver the minimum energy
        if minimum_energy_consumed > maximum_energy_produced:  # if energy is lacking
            energy_difference_minimum = minimum_energy_consumed - maximum_energy_produced
            price_min = math.inf
        elif minimum_energy_produced > maximum_energy_consumed:  # if there is too much energy
            energy_difference_minimum = - minimum_energy_produced - maximum_energy_consumed
            price_min = - math.inf
        else:
            energy_difference_minimum = 0
            price_min = 0
        message_min = self._create_information_message()
        message_min["energy_minimum"] = energy_difference_minimum
        message_min["energy_nominal"] = energy_difference_minimum
        message_min["energy_maximum"] = energy_difference_minimum
        message_min["price"] = price_min
        bids.append(message_min)

        # maximum management: the second bid seeks to fulfill the non-necessary energy
        energy_difference_maximum = maximum_energy_consumed - maximum_energy_produced - energy_difference_minimum
        if energy_difference_maximum > 0:
            price_max = - math.inf
        elif energy_difference_maximum < 0:
            price_max = math.inf
        else:
            price_max = 0

        message_max = self._create_information_message()
        message_max["energy_minimum"] = 0
        message_max["energy_nominal"] = 0
        message_max["energy_maximum"] = energy_difference_maximum
        message_max["price"] = price_max
        bids.append(message_max)

        return bids




