# This contract is a contract in which the customer makes no effort.
from math import exp, log

from src.common.Contract import Contract
from src.tools.Utilities import sign


class CurtailmentRampContract(Contract):

    def __init__(self, name, nature, daemon_name, parameters):
        super().__init__(name, nature, daemon_name, parameters)

        self.description = "A contract where the customer can be curtailed and where she is refunded proportionally to the curtailment she suffers."

        self._bonus = parameters["bonus"]  # the money given to people accepting a curtailment contract

        # curtailment generates "effort" for each device, but this effort decreases with time
        # here, the depreciation follows an exponential rhythm and two parameters are needed: the residual and the time necessary to reach it
        # for example, a time of 1 month and 0.01 means that after 1 month, only 1% of the initial effort is still considered
        # /!\ do not put 0 for any of these values
        depreciation_time = parameters["depreciation_time"]  # the time necessary to reach the residual value, in hours
        depreciation_residual = parameters["depreciation_residual"]  # the proportion of effort still considered after the depreciation time
        self._tau = - depreciation_time / log(depreciation_residual)

        self._effort = {}  # a dictionary containing the effort for each device
        # todo: trouver combine pour passer du device à l'agent ?

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def initialization(self, device_name):
        self._effort[device_name] = {"effort": 1}  # the minimum effort is 1, to ensure a minimal refund

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def contract_modification(self, message, name):
        # billing
        if message["energy_maximum"] > 0:  # if the maximal quantity of energy is positive, it means that the device asks for energy
            message["price"] = self._catalog.get(f"{self._daemon_name}.buying_price") + self._effort[name]["effort"] * self._bonus  # getting the price per kW.h, at a price artificially corrected by a bonus
        elif message["energy_maximum"] <= 0:  # if the maximal quantity of energy is positive, it means that the device proposes energy
            message["price"] = self._catalog.get(f"{self._daemon_name}.selling_price") - self._effort[name]["effort"] * self._bonus  # getting the price per kW.h, at a price artificially corrected by the bonus

        message["energy_minimum"] = 0  # set the minimal quantity of energy to 0
        message["energy_nominal"] = min(abs(message["energy_maximum"] * 0.95), abs(message["energy_nominal"])) * sign(message["energy_maximum"])  # the abs() allows to manage both consumptions and productions
        # this contract forbids the quantity to be urgent
        # it means that the devices will never be sure to be served

        self._effort[name]["initial_request"] = message["energy_maximum"]  # record of the initial request of the device to compare it with the quantity served

        return message

    def billing(self, energy_wanted, energy_accorded, name):  # the action of the distribution phase
        energy_served = energy_accorded["quantity"]
        initial_quantity = energy_wanted["energy_maximum"]
        energy_erased = initial_quantity - energy_served  # the demand not satisfied by the aggregator

        # first, management of the refund
        refund = self._effort[name]["effort"] * self._bonus
        min_price = self._catalog.get(f"{self.nature.name}.limit_selling_price")
        max_price = self._catalog.get(f"{self.nature.name}.limit_buying_price")
        refund = min(max(refund, min_price), max_price)  # the refund is limited by the limits prices defined for the nature

        if energy_served < 0:  # if the device delivers energy
            # price is reset
            price = self._catalog.get(f"{self._daemon_name}.selling_price")
            energy_accorded["price"] = price

            # refund is added to the balances of money
            energy_sold = - energy_served
            energy_bought = 0
            money_earned = - price * energy_served - refund * energy_erased  # the producer is paid for the energy produced but also for the energy the aggregator refused him to produce
            money_spent = 0

        else:  # if the device consumes energy
            # price is reset
            price = self._catalog.get(f"{self._daemon_name}.buying_price")
            energy_accorded["price"] = price

            # refund is added to the balances of money
            energy_bought = energy_served
            energy_sold = 0
            money_earned = refund * energy_erased  # the refund the consumer gets if she is curtailed
            money_spent = price * energy_served  # what the consumer pay for the energy it consumes

        # second, management of the effort
        time_step = self._catalog.get("time_step")
        effort = self._effort[name]["effort"]
        effort = effort * exp(- time_step / self._tau)  # effort is depreciated along the time
        if initial_quantity != 0:  # if the device asked for something during the round
            effort += energy_erased / initial_quantity * time_step  # the proportion of energy refused is added to the effort
        self._effort[name]["effort"] = max(effort, 1)  # the effort is always at least of 1 to ensure a minimum refund

        return [energy_accorded, energy_erased, energy_bought, energy_sold, money_earned, money_spent]


