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

        self._parameters = {"effort_value": parameters}

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

    def _user_billing(self, agent_name):  # here, the user_billing is used to compensate the agent for its effort
        current_effort = - self._accumulated_effort
        self._accumulated_effort = self._catalog.get(f"{agent_name}.effort")  # the new value of agregated effort
        current_effort += self._accumulated_effort

        compensation = self._parameters["effort_value"] * current_effort  # calculation of the compensation in money accorded by the contract
        money = self._catalog.get(f"{agent_name}.money") + compensation
        self._catalog.set(f"{agent_name}.money", money)  # stores the new value


user_classes_dictionary[f"{TOUCompensationCooperativeContract.__name__}"] = TOUCompensationCooperativeContract



