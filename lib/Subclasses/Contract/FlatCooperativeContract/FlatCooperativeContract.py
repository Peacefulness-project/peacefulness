# This contract is a contract in which the customer makes no effort.
from src.common.Contract import Contract


class FlatCooperativeContract(Contract):

    def __init__(self, world, name, nature, identifier=None):
        super().__init__(world, name, nature, identifier)

        self.description = "A contract where the price is fixed over the time. Moreover, the customer always gets what she asks."

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
        price = self._catalog.get(f"{self.name}.selling_price") / 0.9  # getting the price per kW.h
        return price




