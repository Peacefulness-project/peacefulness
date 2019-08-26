# This contract is the one wanted for
from common.Contract import Contract


class ClassicContract(Contract):

    def __init__(self, name):
        operations_allowed = [[], [], [], []]  # no operations are allowed for the supervisor
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
    # nothing here as the supervisor is supposed to give always


