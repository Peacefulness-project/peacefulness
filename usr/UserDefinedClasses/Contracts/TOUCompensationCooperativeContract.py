# This contract is the most basic in France: fixed tariffs, full freedom for users
from common.Contract import Contract
from tools.UserClassesDictionary import user_classes_dictionary


class TOUCompensationCooperativeContract(Contract):

    def __init__(self, name, nature, parameters):
        super().__init__(name, nature, parameters)

        self.description = "A contract where the price is fixed over the time at the same tariff than the TOU contract." \
                           "Moreover, the customer accepts shiftable devices to be shifted " \
                           "and to define a range of energy instead of a nominal energy for adjustable devices." \
                           "Meanwhile, she gets money when it furnishes an effort."

        self._accumulated_effort = 0

        self._parameters = [parameters["buying_price"], parameters["selling_price"], parameters["effort_value"]]

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

    def _user_billing(self, agent_name):  # here, the user_billing is used to compensate the agent for its effort
        current_effort = - self._accumulated_effort
        self._accumulated_effort = self._catalog.get(f"{agent_name}.effort")  # the new value of aggregated effort
        current_effort += self._accumulated_effort

        compensation = self._parameters[0] * current_effort  # calculation of the compensation in money accorded by the contract
        money = self._catalog.get(f"{agent_name}.money_spent") + compensation
        self._catalog.set(f"{agent_name}.money_spent", money)  # stores the new value


user_classes_dictionary[f"{TOUCompensationCooperativeContract.__name__}"] = TOUCompensationCooperativeContract



