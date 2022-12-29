# This contract is a contract in which the customer makes no effort.
from src.common.Contract import Contract
from src.tools.Utilities import sign


class CurtailmentContract(Contract):

    def __init__(self, name, nature, daemon_name):
        super().__init__(name, nature, daemon_name)

        self.description = "A contract where the customer can be curtailed."

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, message, name):
        # billing
        if message["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
            message["price"] = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price per kW.h
        elif message["energy_maximum"] < 0:  # if the maximal quantity of energy is positive, it means that the device proposes energy
            message["price"] = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price per kW.h

        message["energy_minimum"] = 0  # set the minimal quantity of energy to 0
        message["energy_nominal"] = min(abs(message["energy_maximum"] * 0.95), abs(message["energy_nominal"])) * sign(message["energy_maximum"])  # the abs() allows to manage both consumptions and productions
        # this contract forbids the quantity to be urgent
        # it means that the devices will never be sure to be served

        return message




