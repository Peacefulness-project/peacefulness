# this daemon is designed to manage the limit prices of a given energy for sellers or buyers
from src.common.Daemon import Daemon


class LimitPricesDaemon(Daemon):

    def __init__(self, parameters, period=1):
        self._nature = parameters["nature"]

        name = "grid_prices_manager_for_nature" + self._nature
        super().__init__(name, period, parameters)

        self._buying_price = parameters["limit_buying_price"]
        self._selling_price = parameters["limit_selling_price"]

        self._catalog.add(f"{self._nature}.limit_buying_price", self._buying_price)
        self._catalog.add(f"{self._nature}.limit_selling_price", self._selling_price)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):
        pass






