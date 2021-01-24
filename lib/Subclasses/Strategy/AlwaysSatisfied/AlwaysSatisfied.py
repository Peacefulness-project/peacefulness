# This sheet describes a strategy always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from src.common.Strategy import Strategy
from src.tools.Utilities import sign
from src.common.Strategy import SupervisorException
from math import inf


class AlwaysSatisfied(Strategy):

    def __init__(self):
        super().__init__("always_satisfied_strategy", "Always serves everybody, whatever it can cost to him.")

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def bottom_up_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        energy_available_from_converters = 0  # the quantity of energy available thanks to converters

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters)
        energy_difference = maximum_energy_consumed - maximum_energy_produced

        quantities_and_prices = [{element: self._messages["top-down"][element] for element in self._messages["top-down"]}]  # the standard bottom-up message
        quantities_and_prices[0]["energy_minimum"] = energy_difference
        quantities_and_prices[0]["energy_nominal"] = energy_difference
        quantities_and_prices[0]["energy_maximum"] = energy_difference

        quantities_and_prices = self._publish_needs(aggregator, quantities_and_prices)

        return quantities_and_prices

    def top_down_phase(self, aggregator):  # after having exchanged with the exterior, the aggregator distributes the energy among its devices and aggregators
        quantities_asked = {"bought": 0, "sold": 0}
        quantities_given = {"bought": 0, "sold": 0}

        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        # counting the offers and the demands at its own level
        # what was asked
        for element in self._catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_wanted"):
            if element["energy_maximum"] > 0:  # energy the aggregator wanted to buy
                quantities_asked["bought"] += element["energy_maximum"]  # the quantity of energy asked the aggregator wanted to buy
            elif element["energy_maximum"] < 0:  # energy the aggregator wanted to sell
                quantities_asked["sold"] += element["energy_maximum"]  # the quantity of energy asked the aggregator wanted to sell

        # what is given
        for element in self._catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded"):
            if element["quantity"] > 0:  # energy bought by the aggregator
                quantities_given["bought"] += element["quantity"]  # the quantity of energy sold to the aggregator
                element["price"] = min(element["price"], max_price)  # maximum price is artificially limited

                # making balances
                # energy bought
                energy_bought_outside += element["quantity"]  # the absolute value of energy bought outside
                money_spent_outside += element["quantity"] * element["price"]  # the absolute value of money spent outside

            elif element["quantity"] < 0:  # energy sold by the aggregator
                quantities_given["sold"] += element["quantity"]  # the quantity of energy bought by the aggregator
                element["price"] = max(element["price"], min_price)  # minimum price is artificially limited

                # making balances
                # energy sold
                energy_sold_outside -= element["quantity"]  # the absolute value of energy sold outside
                money_earned_outside -= element["quantity"] * element["price"]  # the absolute value of money earned outside

        # energy distribution and billing
        if quantities_given == quantities_asked:  # if the aggregator got what it wanted

            # quantities concerning devices
            for name in aggregator.devices:
                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                energy = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]  # the maximum quantity of energy asked
                price = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted")["price"]  # the price of the energy asked

                # user-added elements management
                additional_elements = {element: message[element] for element in message}
                additional_elements.pop("quantity")
                additional_elements.pop("price")
                for additional_element in additional_elements:
                    message[additional_element] = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted")[additional_element]

                # balances
                if energy > 0:  # energy bought
                    price = min(price, max_price)

                    message["quantity"] = energy
                    message["price"] = price
                    self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", message)

                    money_earned_inside += energy * price  # money earned by selling energy to the device
                    energy_sold_inside += energy  # the absolute value of energy sold inside
                elif energy < 0:  # energy sold
                    price = max(price, min_price)

                    message["quantity"] = energy
                    message["price"] = price
                    self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", message)

                    money_spent_inside -= energy * price  # money spent by buying energy from the device
                    energy_bought_inside -= energy  # the absolute value of energy bought inside

            # quantities concerning subaggregators
            for subaggregator in aggregator.subaggregators:  # quantities concerning aggregators
                quantities_and_prices = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
                quantities_accorded = []

                # balances
                for element in quantities_and_prices:  # for each couple energy/price
                    message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                    message["quantity"] = element["energy_maximum"]
                    message["price"] = element["price"]

                    # user-added elements management
                    additional_elements = {element: message[element] for element in message}
                    additional_elements.pop("quantity")
                    additional_elements.pop("price")
                    for additional_element in additional_elements:
                        message[additional_element] = element[additional_element]

                    if element["energy_maximum"] > 0:  # energy bought
                        element["price"] = min(element["price"], max_price)  # maximum price is artificially limited

                        money_earned_inside += element["energy_maximum"] * element["price"]  # money earned by selling energy to the subaggregator
                        energy_sold_inside += element["energy_maximum"]  # the absolute value of energy sold inside
                    elif element["energy_maximum"] < 0:  # energy sold
                        element["price"] = max(element["price"], min_price)  # minimum price is artificially limited

                        money_spent_inside -= element["energy_maximum"] * element["price"]  # money spent by buying energy from the subaggregator
                        energy_bought_inside -= element["energy_maximum"]  # the absolute value of energy bought inside

                    quantities_accorded.append(message)

                self._catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", quantities_accorded)

        else:
            # as we suppose that there is always a grid able to buy/sell an infinite quantity of energy, we souldn't be in this case
            raise SupervisorException("An always satisfied strategy supposes the access to an infinite provider/consumer")

        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, energy_sold_inside, energy_bought_inside)






