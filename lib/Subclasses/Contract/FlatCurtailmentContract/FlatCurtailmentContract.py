# This contract is a contract in which the customer makes no effort.
from src.common.Contract import Contract
from src.tools.Utilities import sign


class FlatCurtailmentContract(Contract):

    def __init__(self, name, nature, identifier):
        super().__init__(name, nature, identifier)

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
        price = self._catalog.get(f"{self.name}.buying_price") * 0.8  # getting the price per kW.h
        return price

    def _billing_selling(self, quantity):
        price = self._catalog.get(f"{self.name}.selling_price") / 0.8  # getting the price per kW.h
        return price

    # quantity management
    def quantity_modification(self, quantity, agent_name):
        quantity["energy_minimum"] = 0  # set the minimal quantity of energy to 0
        quantity["energy_nominal"] = min(abs(quantity["energy_maximum"]*0.95), abs(quantity["energy_nominal"])) * sign(quantity["energy_maximum"])  # the abs() allows to manage both consumptions and productions
        # this contract forbids the quantity to be urgent
        # it means that the devices will never be sure to be served

        quantity["price"] = self._billing(quantity, agent_name)

        return quantity




