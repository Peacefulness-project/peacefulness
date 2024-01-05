# This sheet describes a strategy of a TSO
# It represents the higher level of energy management. Here, it is a black box: it both proposes and accepts unlimited amounts of energy
from src.common.Strategy import Strategy
from math import inf


class Grid(Strategy):

    def __init__(self):
        super().__init__("grid_strategy", "Special strategy: represents an infinite source/well of energy, like the national grid of electricity or gas. Does not manage nothing: just sell or buy energy when prices are superior to the ones practiced by the grid.")

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def multi_energy_balance_check(self, aggregator):
        pass

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def bottom_up_phase(self, aggregator):  # the grid, as it has no devices, has no distribution to make
        pass

    def top_down_phase(self, aggregator):  # the grid, as it has no devices, has no distribution to make
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed


        # quantities concerning devices
        for name in aggregator.devices:
            message = self._create_decision_message()
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
                # print(name, self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded"))

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
                message = self._create_decision_message()
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

        self._update_balances(aggregator, energy_bought_inside, 0, energy_sold_inside, 0, money_spent_inside, 0, money_earned_inside, 0, energy_sold_inside, energy_bought_inside)



