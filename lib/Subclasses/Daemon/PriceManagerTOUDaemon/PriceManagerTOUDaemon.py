# this daemon is designed to manage the price of a given energy for sellers or buyers
from src.common.Daemon import Daemon


class PriceManagerTOUDaemon(Daemon):

    def __init__(self, name, parameters):
        super().__init__(name, 1, parameters)

        self._buying_price = parameters["buying_price"]  # the price for buying 1 kWh of energy for the agent
        self._selling_price = parameters["selling_price"]  # the price for selling 1 kWh of energy for the agent

        self._hours = []
        hours_range = parameters["on-peak_hours"]
        for hour_range in hours_range:
            for i in range(hour_range[0], hour_range[1]):
                self._hours.append(i)

        self._moment = None  # indicates if the tariff is HP or HC

        self._moment = (self._catalog.get("physical_time").hour in self._hours) * 1  # 1 = HP, 0 = HC

        self._catalog.add(f"{self.name}.buying_price", self._get_buying_price())  # the buying price for energy is set
        self._catalog.add(f"{self.name}.selling_price", self._get_selling_price())  # the selling price for energy is set

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):  # make shifts between on-peak and off-peaks tariffs
        self._moment = (self._catalog.get("physical_time").hour in self._hours) * 1  # 1 = on-peak, 0 = off-peak

        self._catalog.set(f"{self.name}.buying_price", self._get_buying_price())  # the buying price for energy is set
        self._catalog.set(f"{self.name}.selling_price", self._get_selling_price())  # the selling price for energy is set

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def _get_buying_price(self):
        buying_price = self._buying_price[self._moment]
        return buying_price

    def _get_selling_price(self):
        selling_price = self._selling_price[self._moment]
        return selling_price






