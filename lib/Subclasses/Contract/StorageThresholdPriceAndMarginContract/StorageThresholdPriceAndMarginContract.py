# This contract is a contract in which energy is bought only when the price is below a certain level and sold when the selling price allows to make a minimum margin.
from src.common.Contract import Contract


class ThresholdPriceAndMarginContract(Contract):

    def __init__(self, name, nature, daemon_name, parameters):
        super().__init__(name, nature, daemon_name, parameters)

        self.description = "A contract where energy is asked only if the price is above or below a given value."

        self._buying_threshold = parameters["buying_threshold"]
        self._margin = parameters["margin"]
        self._averaged_storage_cost = {}  # a dictionary computing the price of the energy in each storage

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, message, name):
        # billing
        buying_price = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price of energy per kW.h
        selling_price = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price of energy per kW.h

        selling_threshold = self._margin + 0

        if buying_price <= self._buying_threshold:  # if the value of energy is below a given value
            message["price"] = buying_price  # setting the price of energy per Kwh
            message["energy_nominal"] = 0
            message["energy_minimum"] = 0
        elif selling_price >= selling_threshold:  # if the value of energy is above a given value
            message["price"] = selling_price  # setting the price of energy per Kwh
            message["energy_maximum"] = - message["energy_minimum"]
            message["energy_nominal"] = 0
            message["energy_minimum"] = 0
        else:  # if the value of energy is below the limit value
            message["price"] = 0  # setting the price of energy per Kwh
            # and the quantity is set to 0
            message["energy_minimum"] = 0
            message["energy_nominal"] = 0
            message["energy_maximum"] = 0

        return message  # this contract forces the priority to 1, which means it is always urgent

    def billing(self, energy_accorded, name):  # the action of the distribution phase
        # déduire variation avec moyenne pondérée et intégrer pertes (faire publier pertes par les deivces)
        return energy_accorded  # if the function is not modified, it does not change the initial value
