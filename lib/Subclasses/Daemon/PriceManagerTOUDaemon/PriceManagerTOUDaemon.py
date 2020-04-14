# this daemon is designed to manage the price of a given energy for sellers or buyers
from src.common.Daemon import Daemon


class PriceManagerTOUDaemon(Daemon):

    def __init__(self, period=0, parameters=None):
        self._identifier = parameters["identifier"]  # the identifier used for the contracts managed by this

        name = "price_manager_" + self._identifier
        super().__init__(name, period, parameters)

        self._buying_price = parameters["buying_price"]  # the price for buying 1 kWh of energy for the agent
        self._selling_price = parameters["selling_price"]  # the price for selling 1 kWh of energy for the agent
        self._contract_list = None  # the list of contracts taken in charge by this daemon, added later

        self._contract_list = self._catalog.get(f"contracts_{self._identifier}")  # the list of contract this daemon has to take in charge
        self._catalog.remove(f"contracts_{self._identifier}")  # as this key is not used anymore, it is deleted

        self._hours = []
        hours_range = parameters["hours"]
        for hour_range in hours_range:
            for i in range(hour_range[0], hour_range[1]):
                self._hours.append(i)

        self._moment = None  # indicates if the tariff is HP or HC

        self._moment = (self._catalog.get("physical_time").hour in self._hours) * 1  # 1 = HP, 0 = HC

        for contract_name in self._contract_list:  # for all the contracts taken in charge
            self._catalog.set(f"{contract_name}.buying_price", self._get_buying_price())  # the buying price for energy is set
            self._catalog.set(f"{contract_name}.selling_price", self._get_selling_price())  # the selling price for energy is set

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):  # make shifts between on-peak and off-peaks tariffs
        self._moment = (self._catalog.get("physical_time").hour in self._hours) * 1  # 1 = on-peak, 0 = off-peak

        for contract_name in self._contract_list:  # for all the contracts taken in charge
            self._catalog.set(f"{contract_name}.buying_price", self._get_buying_price())  # the buying price for energy is set
            self._catalog.set(f"{contract_name}.selling_price", self._get_selling_price())  # the selling price for energy is set

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def _get_buying_price(self):
        buying_price = self._buying_price[self._moment]
        return buying_price

    def _get_selling_price(self):
        selling_price = self._selling_price[self._moment]
        return selling_price






