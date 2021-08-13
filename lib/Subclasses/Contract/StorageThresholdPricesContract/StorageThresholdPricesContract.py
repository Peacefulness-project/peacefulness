# This contract is a contract in which energy is asked/proposes only when the price is below/above a defined value.
from src.common.Contract import Contract


class StorageThresholdPricesContract(Contract):

    def __init__(self, name, nature, daemon_name, parameters):
        super().__init__(name, nature, daemon_name, parameters)

        self.description = "A contract dedicated to storage devices where loading or unloading mode is defined according to price of energy"

        self._buying_threshold = parameters["buying_threshold"]
        self._selling_threshold = parameters["selling_threshold"]

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, quantity, name):
        # billing
        buying_price = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price of energy per kWh
        selling_price = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price of energy per kWh

        # billing
        buying_price = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price of energy per kW.h
        selling_price = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price of energy per kW.h

        if buying_price <= self._buying_threshold:  # if the value of energy is below a given value
            quantity["price"] = buying_price  # setting the price of energy per Kwh
            quantity["energy_nominal"] = 0
            quantity["energy_minimum"] = 0
        elif selling_price >= self._selling_threshold:  # if the value of energy is above a given value
            quantity["price"] = selling_price  # setting the price of energy per Kwh
            quantity["energy_maximum"] = quantity["energy_minimum"]
            quantity["energy_nominal"] = 0
            quantity["energy_minimum"] = 0
        else:  # if the value of energy is below the limit value
            quantity["price"] = 0  # setting the price of energy per Kwh
            # and the quantity is set to 0
            quantity["energy_minimum"] = 0
            quantity["energy_nominal"] = 0
            quantity["energy_maximum"] = 0

        return quantity



