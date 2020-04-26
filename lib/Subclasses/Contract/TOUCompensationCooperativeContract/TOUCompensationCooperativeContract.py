# This contract is the most basic in France: fixed tariffs, full freedom for users
from src.common.Contract import Contract


class TOUCompensationCooperativeContract(Contract):

    def __init__(self, name, nature, daemon_name, parameters=None):
        super().__init__(name, nature, daemon_name, parameters)

        self.description = "A contract where the price is fixed over the time at the same tariff than the TOU contract." \
                           "Moreover, the customer accepts shiftable devices to be shifted " \
                           "and to define a range of energy instead of a nominal energy for adjustable devices." \
                           "Meanwhile, she gets money when it furnishes an effort."

        self._compensation_rate = parameters["compensation"]

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, quantity):
        price = self._catalog.get(f"{self._daemon_name}.buying_price") * 0.9  # getting the price per kW.h
        return price

    def _billing_selling(self, quantity):
        price = self._catalog.get(f"{self._daemon_name}.selling_price") / 0.9  # getting the price per kW.h
        return price

    def _user_billing(self, agent_name):  # here, the user_billing is used to compensate the agent for its effort
        current_effort = self._catalog.get(f"{agent_name}.{self.nature.name}.effort")["current_round_effort"]  # the new value of aggregated effort
        compensation = self._compensation_rate * current_effort  # calculation of the compensation in money accorded by the contract

        money = self._catalog.get(f"{agent_name}.money_spent") - compensation  # the compensation reduces the bill of the agent
        self._catalog.set(f"{agent_name}.money_spent", money)  # stores the new value





