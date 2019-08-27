# this daemon is designed to manage the price of a given energy for sellers or buyers

from common.Daemon import Daemon


class PriceManagerDaemon(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)
        self._nature = parameters[0]
        self._buying_price = parameters[1]
        self._selling_price = parameters[2]

    def _user_register(self):
        self._catalog.add(f"{self._nature}_buying_price", self._buying_price)
        self._catalog.add(f"{self._nature}_selling_price", self._selling_price)

    def _process(self):
        pass




