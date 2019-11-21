# This contract is a contract in which the customer give poser to the supervisor but does not accept not be served.
from common.Contract import Contract
from tools.UserClassesDictionary import user_classes_dictionary


class TOUCooperativeContract(Contract):

    def __init__(self, name, nature, parameters=None):
        super().__init__(name, nature)

        self.description = "A contract where the price is fixed over the time at a lower tariff than the TOU contract." \
                           "Meanwhile, the customer accepts shiftable devices to be shifted " \
                           "and to define a range of energy instead of a nominal energy for adjustable devices."

        self._parameters = [parameters["selling_price"], parameters["buying_price"]]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        self._catalog.set(f"{self.name}.{self.nature.name}.buying_price", self._parameters[0])  # the price paid to buy energy of a given nature with this contract
        self._catalog.set(f"{self.name}.{self.nature.name}.selling_price", self._parameters[1])  # the price received by selling energy  of a given nature with this contract

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, energy_amount, agent_name):
        price = self._catalog.get(f"{self.name}.{self.nature.name}.buying_price")  # getting the price per kW.h
        money = self._catalog.get(f"{agent_name}.money_spent") + price * energy_amount  # updating the amount of money spent/earned by the agent
        self._catalog.set(f"{agent_name}.money_spent", money)  # stores the new value

    def _billing_selling(self, energy_amount, agent_name):
        price = self._catalog.get(f"{self.name}.{self.nature.name}.selling_price")  # getting the price per kW.h
        money = self._catalog.get(f"{agent_name}.money_earned") + price * energy_amount  # updating the amount of money spent/earned by the agent
        self._catalog.set(f"{agent_name}.money_earned", money)  # stores the new value


user_classes_dictionary[f"{TOUCooperativeContract.__name__}"] = TOUCooperativeContract




