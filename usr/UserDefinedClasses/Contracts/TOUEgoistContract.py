# This contract is a contract in which the customer makes no effort.
from common.Contract import Contract


class TOUEgoistContract(Contract):

    def __init__(self, name, nature, parameters=None):
        super().__init__(name, nature)

        self.description = "A contract where the price is fixed over the time. Moreover, the customer always gets what she asks."

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, energy_amount, agent_name):
        price = self._catalog.get(f"{self._nature.name}_buying_price")  # getting the price per kW.h
        money = self._catalog.get(f"{agent_name}.money") + price * energy_amount  # updating the amount of money spent/earned by the agent
        self._catalog.set(f"{agent_name}.money", money)  # stores the new value

    def _billing_selling(self, energy_amount, agent_name):
        price = self._catalog.get(f"{self._nature.name}_selling_price")  # getting the price per kW.h
        money = self._catalog.get(f"{agent_name}.money") + price * energy_amount  # updating the amount of money spent/earned by the agent
        self._catalog.set(f"{agent_name}.money", money)  # stores the new value

    # priority management
    def priority_modification(self, priority):
        return 1  # this contract forces the priority to 1, which means it is always urgent


