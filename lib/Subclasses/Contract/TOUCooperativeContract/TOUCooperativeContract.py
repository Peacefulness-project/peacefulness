# This contract is a contract in which the customer give poser to the supervisor but does not accept not be served.
from src.common.Contract import Contract


class TOUCooperativeContract(Contract):

    def __init__(self, name, nature, daemon_name):
        super().__init__(name, nature, daemon_name)

        self.description = "A contract where the price is fixed over the time at a lower tariff than the TOU contract." \
                           "Meanwhile, the customer accepts shiftable devices to be shifted " \
                           "and to define a range of energy instead of a nominal energy for adjustable devices."

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, quantity):  # as the tariffs are not the same for selling or buying energy, this function redirects to the relevant function
        if quantity["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
            quantity["price"] = self._catalog.get(f"{self._daemon_name}.buying_price") * 0.9  # getting the price per kW.h
        elif quantity["energy_maximum"] < 0:  # if the maximal quantity of energy is positive, it means that the device proposes energy
            quantity["price"] = self._catalog.get(f"{self._daemon_name}.selling_price") / 0.9  # getting the price per kW.h

        return quantity






