# This contract is a contract in which the customer makes no effort.
from src.common.Contract import Contract


class ThresholdPricesContract(Contract):

    def __init__(self, name, nature, daemon_name, parameters):
        super().__init__(name, nature, daemon_name, parameters)

        self.description = "A contract where energy is asked only if the price of electricity is above or below a given value."

        self._buying_threshold = parameters["buying_threshold"]
        self._selling_threshold = parameters["selling_threshold"]

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, quantity):
        # billing
        if quantity["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
            buying_price = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price of energy per kW.h

            if buying_price <= self._buying_threshold:  # if the value of energy is below a given value
                quantity["price"] = buying_price  # setting the price of energy per Kwh
                # and the quantity is left unchanged
            else:  # if the value of energy is above the limit value
                quantity["price"] = buying_price  # setting the price of energy per Kwh
                # and the quantity is set to 0
                quantity["energy_minimum"] = 0
                quantity["energy_nominal"] = 0
                quantity["energy_maximum"] = 0

        elif quantity["energy_maximum"] < 0:  # if the maximal quantity of energy is negative, it means that the device proposes energy
            selling_price = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price of energy per kW.h

            if selling_price >= self._selling_threshold:  # if the value of energy is aboce a given value
                quantity["price"] = selling_price  # setting the price of energy per Kwh
                # and the quantity is left unchanged
            else:  # if the value of energy is below the limit value
                quantity["price"] = selling_price  # setting the price of energy per Kwh
                # and the quantity is set to 0
                quantity["energy_minimum"] = 0
                quantity["energy_nominal"] = 0
                quantity["energy_maximum"] = 0

        return quantity  # this contract forces the priority to 1, which means it is always urgent


