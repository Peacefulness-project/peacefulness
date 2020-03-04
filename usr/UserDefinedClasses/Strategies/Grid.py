# This sheet describes a strategy of a TSO
# It represents the higher level of energy management. Here, it is a black box: it both proposes and accepts unlimited amounts of energy
from common.Strategy import Strategy
from math import inf
from tools.UserClassesDictionary import user_classes_dictionary


class Grid(Strategy):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, aggregator):  # the grid, as it has no devices, has no distribution to make
        pass

    def publish_quantities(self, aggregator):  # the grid can always sell and buy an infinite quantity of energy
        selling_price = self._catalog.get(f"{aggregator.nature.name}.grid_buying_price")
        buying_price = self._catalog.get(f"{aggregator.nature.name}.grid_selling_price")

        grid_offer = [[-inf, selling_price], [inf, buying_price]]

        self._catalog.set(f"{aggregator.name}.{aggregator.nature.name}.energy_needs", grid_offer)

    def distribute_remote_energy(self, aggregator):  # the grid, as it has no devices, has no distribution to make
        # meanwhile, it always serve all the quantities asked by its subaggregator as long as the price announced fit its prices
        for managed_aggregator in aggregator.subaggregators:  # for each subaggregator
            quantities = self._catalog.get(f"{managed_aggregator.name}.quantities_asked")

            for couple in quantities:  # attribution of the correct price
                if couple[0] > 0:  # if the subaggregator wants to buy energy
                    if couple[1] < self._catalog.get(f"{aggregator.nature.name}.grid_buying_price"):  # if the price is below the grid tariff
                        couple = [0, 0]  # it is not served
                    else:  # if price proposed is above or equal to the price set for the grid
                        couple[1] = self._catalog.get(f"{aggregator.nature.name}.grid_buying_price")  # it is served and the price is adjusted

                elif couple[0] < 0:  # if the subaggregator wants to sell energy
                    if couple[1] > self._catalog.get(f"{aggregator.nature.name}.grid_selling_price"):  # if the price is above the grid tariff
                        couple = [0, 0]  # it is not served
                    else:  # if price proposed is below or equal to the price set for the grid
                        couple[1] = self._catalog.get(f"{aggregator.nature.name}.grid_selling_price")  # it is served and the price is adjusted

                self._catalog.set(f"{managed_aggregator.name}.quantities_given", quantities)


user_classes_dictionary[f"{Grid.__name__}"] = Grid



