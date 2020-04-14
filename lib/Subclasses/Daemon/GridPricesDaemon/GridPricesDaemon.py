# this daemon is designed to manage the price of a given energy for sellers or buyers
from src.common.Daemon import Daemon


class GridPricesDaemon(Daemon):

    def __init__(self, period=0, parameters=None):
        self._nature = parameters["nature"]

        name = "grid_prices_manager_for_nature" + self._nature
        super().__init__(name, period, parameters)

        self._buying_price = parameters["grid_buying_price"]
        self._selling_price = parameters["grid_selling_price"]

        self._catalog.add(f"{self._nature}.grid_buying_price", self._buying_price)
        self._catalog.add(f"{self._nature}.grid_selling_price", self._selling_price)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):
        pass






