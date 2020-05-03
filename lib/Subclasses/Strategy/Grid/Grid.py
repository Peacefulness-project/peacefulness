# This sheet describes a strategy of a TSO
# It represents the higher level of energy management. Here, it is a black box: it both proposes and accepts unlimited amounts of energy
from src.common.Strategy import Strategy
from math import inf


class Grid(Strategy):

    def __init__(self):
        super().__init__("grid_strategy", "Special strategy: represents an infinite source/well of energy, like the national grid of electricity or gas. Does not manage nothing: just sell or buy energy when prices are superior to the ones practiced by the grid.")

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, aggregator):  # the grid, as it has no devices, has no distribution to make
        pass

    def distribute_remote_energy(self, aggregator):  # the grid, as it has no devices, has no distribution to make
        # meanwhile, it always serve all the quantities asked by its subaggregator as long as the price announced fit its prices
        for managed_aggregator in aggregator.subaggregators:  # for each subaggregator
            quantities_wanted = self._catalog.get(f"{managed_aggregator.name}.{aggregator.nature.name}.energy_wanted")

            quantities_accorded = []
            for element in quantities_wanted:  # attribution of the correct price
                quantity = element["energy_maximum"]
                price = element["price"]
                quantities_accorded.append({"quantity": quantity, "price": price})

                self._catalog.set(f"{managed_aggregator.name}.{aggregator.nature.name}.energy_accorded", quantities_accorded)





