# This contract is the most basic in France: fixed tariffs, full freedom for users
from src.common.Contract import Contract


class TOUCompensationCooperativeContract(Contract):

    def __init__(self, name, nature, daemon_name, parameters):
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
    def _billing(self, quantity, agent_name):  # as the tariffs are not the same for selling or buying energy, this function redirects to the relevant function
        if quantity["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
            price = self._billing_buying(quantity["energy_maximum"])
        elif quantity["energy_maximum"] < 0:  # if the maximal quantity of energy is positive, it means that the device proposes energy
            price = self._billing_selling(quantity["energy_maximum"])
        else:  # if there is no need
            price = None  # no price is attributed

        return price

    def _billing_buying(self):
        price = self._catalog.get(f"{self._daemon_name}.buying_price") * 0.9  # getting the price per kW.h
        return price

    def _billing_selling(self):
        price = self._catalog.get(f"{self._daemon_name}.selling_price") / 0.9  # getting the price per kW.h
        return price

    def _user_billing(self, agent_name):  # here, the user_billing is used to compensate the agent for its effort
        current_effort = self._catalog.get(f"{agent_name}.{self.nature.name}.effort")["current_round_effort"]  # the new value of aggregated effort
        compensation = self._compensation_rate * current_effort  # calculation of the compensation in money accorded by the contract

        money = self._catalog.get(f"{agent_name}.money_spent") - compensation  # the compensation reduces the bill of the agent
        self._catalog.set(f"{agent_name}.money_spent", money)  # stores the new value





