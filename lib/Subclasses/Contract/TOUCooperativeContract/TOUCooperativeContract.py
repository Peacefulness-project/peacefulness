# This contract is a contract in which the customer give poser to the supervisor but does not accept not be served.
from src.common.Contract import Contract


class TOUCooperativeContract(Contract):

    def __init__(self, name, nature, identifier=None):
        super().__init__(name, nature, identifier)

        self.description = "A contract where the price is fixed over the time at a lower tariff than the TOU contract." \
                           "Meanwhile, the customer accepts shiftable devices to be shifted " \
                           "and to define a range of energy instead of a nominal energy for adjustable devices."

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        pass

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, quantity):
        price = self._catalog.get(f"{self.name}.buying_price") * 0.9  # getting the price per kW.h
        return price

    def _billing_selling(self, quantity):
        price = self._catalog.get(f"{self.name}.selling_price") * 0.9  # getting the price per kW.h
        return price






