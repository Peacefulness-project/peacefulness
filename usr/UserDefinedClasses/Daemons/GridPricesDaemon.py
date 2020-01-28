# this daemon is designed to manage the price of a given energy for sellers or buyers
from common.Daemon import Daemon
from tools.UserClassesDictionary import user_classes_dictionary


class GridPricesDaemon(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)
        self._nature = parameters["nature"]
        self._buying_price = parameters["grid_buying_price"]
        self._selling_price = parameters["grid_selling_price"]

    def _user_register(self):
        self._catalog.add(f"{self._nature}.grid_buying_price", self._buying_price)
        self._catalog.add(f"{self._nature}.grid_selling_price", self._selling_price)

    def _process(self):
        pass


user_classes_dictionary[f"{GridPricesDaemon.__name__}"] = GridPricesDaemon




