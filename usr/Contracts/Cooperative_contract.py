# This contract is the most basic in France: fixed tariffs, full freedom for users
from common.Contract import Contract


class CooperativeContract(Contract):

    def __init__(self, name):
        operations_allowed = [[], ["shiftable"], ["adjustable"], []]  # no operations are allowed for the supervisor
        super().__init__(name, operations_allowed)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, energy_amount, agent_name, nature):
        price = self._catalog.get(f"{nature.name}_buying_price")  # getting the price per kW.h
        money = self._catalog.get(f"{agent_name}.money") + price * energy_amount  # updating the amount of money spent/earned by the agent
        print(money)
        self._catalog.set(f"{agent_name}.money", money)

    def _billing_selling(self, energy_amount, agent_name, nature):
        price = self._catalog.get(f"{nature.name}_selling_price")  # getting the price per kW.h
        money = self._catalog.get(f"{agent_name}.money") + price * energy_amount  # updating the amount of money spent/earned by the agent
        self._catalog.set(f"{agent_name}.money", money)
        print(money)

    # dissatisfaction management
    def shiftable_dissatisfaction(self, agent_name, device_name, natures):
        dissatisfaction = self._catalog.get(f"{agent_name}.dissatisfaction") + 1
        self._catalog.set(f"{agent_name}.dissatisfaction", dissatisfaction)  # dissatisfaction increments

    def adjustable_dissatisfaction(self, agent_name, device_name, natures):
        dissatisfaction = self._catalog.get(f"{agent_name}.dissatisfaction")
        for nature in natures:
            energy_wanted_min = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_minimum")  # minimum quantity of energy
            energy_wanted = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")  # nominal quantity of energy
            energy_wanted_max = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_maximum")  # maximum quantity of energy
            energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")

            dissatisfaction += min(abs(energy_wanted_min - energy_accorded), abs(energy_wanted_max - energy_accorded)) / energy_wanted  # ... dissatisfaction increases

        self._catalog.set(f"{agent_name}.dissatisfaction", dissatisfaction)



