# This contract is a contract in which the customer makes no effort.
from src.common.Contract import Contract
from src.tools.Utilities import sign


class LimitedCurtailmentContract(Contract):

    def __init__(self, name, nature, daemon_name, parameters):
        super().__init__(name, nature, daemon_name, parameters)

        self._curtailment_hours_available = parameters["curtailment_hours"]
        self._curtailment_hours = parameters["curtailment_hours"]

        self._remnant_hours = parameters["rotation_duration"]
        self._rotation_duration = parameters["rotation_duration"]

        self.description = "A contract where the customer has accepted to be curtailed for a limited duration along the year."

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, message, name):
        # curtailment rotation management
        self._remnant_hours -= 1  # decrement
        if self._remnant_hours == 0:  # reset of curtailment hours
            self._curtailment_hours_available = self._curtailment_hours
            self._remnant_hours = self._rotation_duration

        # billing
        if self._curtailment_hours_available > 0:  # if it is still possible to cut consumption, it works as the curtailment contract
            if message["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
                message["price"] = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price per kW.h
            elif message["energy_maximum"] < 0:  # if the maximal quantity of energy is positive, it means that the device proposes energy
                message["price"] = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price per kW.h

            message["energy_minimum"] = 0  # set the minimal quantity of energy to 0
            message["energy_nominal"] = min(abs(message["energy_maximum"] * 0.95), abs(message["energy_nominal"])) * sign(message["energy_maximum"])  # the abs() allows to manage both consumptions and productions
        else:  # if it is not possible anymore, it works as BAU contract
            if message["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
                message["price"] = self._catalog.get(f"{self._daemon_name}.buying_price")  # getting the price per kW.h
            elif message["energy_maximum"] < 0:  # if the maximal quantity of energy is positive, it means that the device proposes energy
                message["price"] = self._catalog.get(f"{self._daemon_name}.selling_price")  # getting the price per kW.h

            Emax = message["energy_maximum"]  # it is the maximal quantity of energy asked/received
            message["energy_minimum"] = Emax  # the minimal quantity of energy is put at the maximum to mean that it is urgent
            message["energy_nominal"] = Emax  # the nominal quantity of energy is put at the maximum to mean that it is urgent

        return message

    def billing(self, energy_wanted, energy_accorded, name):  # the action of the distribution phase
        energy_served = energy_accorded["quantity"]
        initial_quantity = energy_wanted["energy_maximum"]
        energy_erased = initial_quantity - energy_served  # the demand not satisfied by the aggregator

        if energy_erased > 1e-6:  # if there was a curtailment, the number of hours available decrease
            self._curtailment_hours_available -= 1

        if energy_served < 0:  # if the device delivers energy
            # price is reset
            price = self._catalog.get(f"{self._daemon_name}.selling_price")
            energy_accorded["price"] = price

            # refund is added to the balances of money
            energy_sold = - energy_served
            energy_bought = 0
            money_earned = - price * energy_served  # the producer is paid for the energy produced but also for the energy the aggregator refused him to produce
            money_spent = 0
        else:
            # price is reset
            price = self._catalog.get(f"{self._daemon_name}.buying_price")
            energy_accorded["price"] = price

            # refund is added to the balances of money
            energy_bought = energy_served
            energy_sold = 0
            money_earned = 0  # the refund the consumer gets if she is curtailed
            money_spent = price * energy_served  # what the consumer pay for the energy it consumes

        return [energy_accorded, energy_erased, energy_bought, energy_sold, money_earned, money_spent]


