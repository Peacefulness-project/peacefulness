# This contract is the most basic in France: fixed tariffs, full freedom for users
from common.Contract import Contract


class CooperativeContract(Contract):

    def __init__(self, name, nature):
        operations_allowed = [[], ["shiftable"], ["adjustable"], []]  # no operations are allowed for the supervisor
        super().__init__(name, nature, operations_allowed)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    # billing
    def _billing_buying(self, energy_amount, agent_name, nature):
        price = self._catalog.get(f"{nature.name}_buying_price")  # getting the price per kW.h
        money = self._catalog.get(f"{agent_name}.money") + price * energy_amount  # updating the amount of money spent/earned by the agent
        self._catalog.set(f"{agent_name}.money", money)

    def _billing_selling(self, energy_amount, agent_name, nature):
        price = self._catalog.get(f"{nature.name}_selling_price")  # getting the price per kW.h
        money = self._catalog.get(f"{agent_name}.money") + price * energy_amount  # updating the amount of money spent/earned by the agent
        self._catalog.set(f"{agent_name}.money", money)

    # dissatisfaction management
    def shiftable_dissatisfaction(self, agent_name, device_name, natures):
        pass

    def adjustable_dissatisfaction(self, agent_name, device_name, natures):
        pass



