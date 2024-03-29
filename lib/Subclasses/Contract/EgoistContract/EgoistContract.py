# This contract is a contract in which the customer makes no effort.
from src.common.Contract import Contract


class EgoistContract(Contract):

    def __init__(self, name, nature, daemon_name):
        super().__init__(name, nature, daemon_name)

        self.description = "A contract where the customer always gets what she asks."

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, message, name):
        # billing
        if message["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
            message["price"] = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price per kW.h
        elif message["energy_maximum"] < 0:  # if the maximal quantity of energy is positive, it means that the device proposes energy
            message["price"] = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price per kW.h

        Emax = message["energy_maximum"]  # it is the maximal quantity of energy asked/received
        message["energy_minimum"] = Emax  # the minimal quantity of energy is put at the maximum to mean that it is urgent
        message["energy_nominal"] = Emax  # the nominal quantity of energy is put at the maximum to mean that it is urgent

        return message  # this contract forces the priority to 1, which means it is always urgent




