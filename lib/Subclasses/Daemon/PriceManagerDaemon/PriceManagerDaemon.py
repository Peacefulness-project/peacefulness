# this class serves as the mother for all demons managing prices of contracts.
# it fixes a price once and for all

from src.common.Daemon import Daemon


class PriceManagerDaemon(Daemon):

    def __init__(self, name, parameters):
        super().__init__(name, 1, parameters)
        self._buying_price = parameters["buying_price"]  # the price for buying 1 kWh of energy for the agent
        self._selling_price = parameters["selling_price"]  # the price for selling 1 kWh of energy for the agent
        # self._contract_list = None  # the list of contracts taken in charge by this daemon, added later

        # self._contract_list = self._catalog.get(f"contracts_{self._identifier}")  # the list of contract this daemon has to take in charge
        # self._catalog.remove(f"contracts_{self._identifier}")  # as this key is not used anymore, it is deleted

        # self._catalog.add(f"contracts_{self.name}", [])  # add a key in the catalog

        self._catalog.add(f"{self.name}.buying_price", self._get_buying_price())  # the buying price for energy is set
        self._catalog.add(f"{self.name}.selling_price", self._get_selling_price())  # the selling price for energy is set

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):  # nothing is specific to this class, as the price is fixed once and for all, but note that more developed price managers are dynamic
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






