# This contract is a contract in which the customer makes no effort.
from src.common.Contract import Contract


class FlatEgoistContract(Contract):

    def __init__(self, name, nature, identifier):
        super().__init__(name, nature, identifier)

        self.description = "A contract where the price is fixed over the time. Moreover, the customer always gets what she asks."

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, quantity):
        price = self._catalog.get(f"{self.name}.buying_price")  # getting the price per kW.h
        return price

    def _billing_selling(self, quantity):
        price = self._catalog.get(f"{self.name}.selling_price")  # getting the price per kW.h
        return price

    # quantity management
    def quantity_modification(self, quantity, agent_name):
        Emax = quantity["energy_maximum"]  # it is the maximal quantity of energy asked/received
        quantity["energy_minimum"] = Emax  # the minimal quantity of energy is put at the maximum to mean that it is urgent
        quantity["energy_nominal"] = Emax  # the nominal quantity of energy is put at the maximum to mean that it is urgent

        quantity["price"] = self._billing(quantity, agent_name)  # attributing a price to the quantity

        return quantity  # this contract forces the priority to 1, which means it is always urgent




