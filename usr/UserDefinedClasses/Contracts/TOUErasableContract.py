# This contract is a contract in which the customer accepts to never be served.
from common.Contract import Contract
from tools.UserClassesDictionary import user_classes_dictionary


class TOUErasableContract(Contract):

    def __init__(self, name, nature, parameters=None):
        super().__init__(name, nature)

        self.description = "A contract where the price is fixed over the time at a lower tariff than the TOU contract." \
                           "Meanwhile, the customer can be shifted and erased, which means she accepts not be served at all."

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
        return min(priority, 0.95)  # this contract forbids the priority to be equal to 1
        # it means that the devices of this agent will never be urgent


user_classes_dictionary[f"{TOUErasableContract.__name__}"] = TOUErasableContract


