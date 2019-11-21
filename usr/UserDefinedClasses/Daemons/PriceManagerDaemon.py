# this daemon is designed to manage the price of a given energy for sellers or buyers

from common.Daemon import Daemon
from tools.UserClassesDictionary import user_classes_dictionary


class PriceManagerDaemon(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)
        self._nature = parameters["nature"]
        self._buying_price = parameters["buying_price"]
        self._selling_price = parameters["selling_price"]

    def _user_register(self):
        self._catalog.add(f"{self.name}.{self._nature}.buying_price", self._buying_price)
        self._catalog.add(f"{self.name}.{self._nature}.selling_price", self._selling_price)

    def _process(self):
        pass


user_classes_dictionary[f"{PriceManagerDaemon.__name__}"] = PriceManagerDaemon




