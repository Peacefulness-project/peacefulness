# this class serves as the mother for all demons managing prices of contracts.
# it fixes a price once and for all

from src.common.Daemon import Daemon


class PriceManagerDaemon(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)
        self._buying_price = parameters["buying_price"]  # the price for buying 1 kWh of energy for the agent
        self._selling_price = parameters["selling_price"]  # the price for selling 1 kWh of energy for the agent
        self._contract_list = None  # the list of contracts taken in charge by this daemon, added later
        self._identifier = parameters["identifier"]  # the identifier used for the contracts managed by this

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        self._contract_list = self._catalog.get(f"contracts_{self._identifier}")  # the list of contract this daemon has to take in charge
        self._catalog.remove(f"contracts_{self._identifier}")  # as this key is not used anymore, it is deleted

        for contract_name in self._contract_list:  # for all the contracts taken in charge
            self._catalog.set(f"{contract_name}.buying_price", self._get_buying_price())  # the buying price for energy is set
            self._catalog.set(f"{contract_name}.selling_price", self._get_selling_price())  # the selling price for energy is set

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):  # nothing is specific to this class, as the price is fixed once and for all, but note that more developed price managers may be dynamic
        pass

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def _get_buying_price(self):
        buying_price = self._buying_price
        return buying_price

    def _get_selling_price(self):
        selling_price = self._selling_price
        return selling_price






