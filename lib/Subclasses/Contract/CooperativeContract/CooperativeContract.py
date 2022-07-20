# This contract is a contract in which the customer makes no effort.
from src.common.Contract import Contract


class CooperativeContract(Contract):

    def __init__(self, name, nature, daemon_name):
        super().__init__(name, nature, daemon_name)

        self.description = "A contract where the customer can be shifted."

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, quantity, name):  # as the tariffs are not the same for selling or buying energy, this function redirects to the relevant function
        if quantity["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
            quantity["price"] = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price per kW.h
        elif quantity["energy_maximum"] < 0:  # if the maximal quantity of energy is negative, it means that the device proposes energy
            quantity["price"] = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price per kW.h

        return quantity




