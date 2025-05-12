from lib.Subclasses.Strategy.TrainingStrategy.TrainingStrategy import TrainingStrategy
from typing import List, Dict, Tuple, Callable
import pandas as pd


class MLStrategy(TrainingStrategy):
    def __init__(self, priorities_consumption: Callable, priorities_production: Callable):
        super().__init__(priorities_consumption, priorities_production)

        index = ["min"]
        columns = ["assess", "exchange", "distribute"]
        data = [[assess_min_conso, exchanges_min_conso, distribution_min_conso]
                ]
        self._options_consumption = pd.DataFrame(index=index, columns=columns, data=data)

        index = ["min"]
        columns = ["assess", "exchange", "distribute"]
        data = [[assess_min_prod, exchanges_min_prod, distribution_min_prod]
                ]
        self._options_production = pd.DataFrame(index=index, columns=columns, data=data)

    def add_consumption_options(self, consumption_dataframe: pd.DataFrame):
        """
        This function completes the standard list of options available for consumption.

        Parameters
        ----------
        consumption_dataframe: Dataframe, a dataframe built as followed:
        - columns are "assess", "exchange" and "distribute"
        - the index is a list of strings
        - the data is composed of functions managing the options
        """

        self._options_consumption = pd.concat([self._options_consumption, consumption_dataframe])

    def add_production_options(self, production_dataframe: pd.DataFrame):
        """
        This function completes the standard list of options available for production.

        Parameters
        ----------
        production_dataframe: Dataframe, a dataframe built as followed:
        - columns are "assess", "exchange" and "distribute"
        - the index is a list of strings
        - the data is composed of functions managing the options
        """

        self._options_production = pd.concat([self._options_production, production_dataframe])

    # ##########################################################################################
    # Priorities functions
    # ##########################################################################################

    def _assess_quantities_for_each_option(self, aggregator: "Aggregator") -> Dict:
        [demands, offers, storage] = self._sort_quantities(aggregator, self._sort_function)
        quantity_per_option = {"consumption": {}, "production": {}}
        priorities_consumption = self._get_priorities_consumption()
        priorities_production = self._get_priorities_production()
        demands = demands + storage
        offers = offers + storage

        for priority in priorities_consumption:
            quantity_per_option["consumption"][priority] = self._options_consumption.loc[priority]["assess"](self, aggregator, demands)
            if priority == "nothing":
                break
        for priority in priorities_production:
            quantity_per_option["production"][priority] = self._options_production.loc[priority]["assess"](self, aggregator, offers)
            if priority == "nothing":
                break

        # balances update
        min_cons = quantity_per_option["consumption"]["min"]
        min_prod = quantity_per_option["production"]["min"]
        max_cons = sum(quantity_per_option["consumption"].values()) - min_cons
        max_prod = sum(quantity_per_option["production"].values()) - min_prod
        # self._catalog.set(f"{aggregator.name}.minimum_energy_consumption", min_cons)
        # self._catalog.set(f"{aggregator.name}.maximum_energy_consumption", max_cons)
        # self._catalog.set(f"{aggregator.name}.minimum_energy_production", min_prod)
        # self._catalog.set(f"{aggregator.name}.maximum_energy_production", max_prod)

        return quantity_per_option

    def _apply_priorities_exchanges(self, aggregator: "Aggregator", quantity_to_affect: float,
                                    quantity_available_per_option: Dict, quantities_and_prices: List, cons_or_prod: str):
        priorities_consumption = self._get_priorities_consumption()
        priorities_production = self._get_priorities_production()

        if cons_or_prod == "consumption":
            for priority in priorities_consumption:
                quantity_to_affect, quantities_and_prices = self._options_consumption.loc[priority]["exchange"](self, aggregator,
                                                                                                                quantity_to_affect,
                                                                                                                quantities_and_prices)
                if priority == "nothing":
                    break
        else:
            for priority in priorities_production:
                quantity_to_affect, quantities_and_prices = self._options_production.loc[priority]["exchange"](self, aggregator,
                                                                                                               quantity_to_affect,
                                                                                                               quantities_and_prices)
                if priority == "nothing":
                    break

    def _apply_priorities_distribution(self, aggregator: "Aggregator", min_price: float, max_price: float,
                                       sorted_demands, sorted_offers,
                                       energy_available_consumption: float, energy_available_production: float) -> Tuple:
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside
        priorities_consumption = self._get_priorities_consumption()
        priorities_production = self._get_priorities_production()

        for priority in priorities_consumption:
            [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside] = self._options_consumption.loc[priority]["distribute"](self, aggregator, min_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)
            if priority == "nothing":
                break
        for priority in priorities_production:
            [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside] = self._options_production.loc[priority]["distribute"](self, aggregator, max_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)
            if priority == "nothing":
                break

        return energy_bought_inside, energy_sold_inside, money_spent_inside, money_earned_inside

# ################################################################################################################
# min management
# ################################################################################################################
# min prod


def assess_min_prod(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for offer in offers:
        if offer["type"] != "storage":
            quantity_for_this_option -= offer["quantity_min"]

    return quantity_for_this_option


def exchanges_min_prod(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float,
                       quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


# no specific function for distribution, the canonical one is used
def distribution_min_prod(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    lines_to_remove = []  # a list containing the number of lines having to be removed
    for i in range(len(sorted_offers)):  # offers
        if sorted_offers[i]["type"] != "storage":
            energy = sorted_offers[i]["quantity"]
            price = sorted_offers[i]["price"]
            price = max(price, min_price)
            name = sorted_offers[i]["name"]

            if sorted_offers[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

                if energy < - energy_available_production:  # if the quantity offered is superior to the rest of energy available
                    unwanted_cuts = strategy._catalog.get("unwanted_delivery_cuts")
                    strategy._catalog.set("unwanted_delivery_cuts", unwanted_cuts - energy - energy_available_production)
                    energy = - energy_available_production  # it is served partially, even if it is urgent

                    message = strategy._create_decision_message()
                    message["quantity"] = energy
                    message["price"] = price

                    if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                        quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                        quantities_given.append(message)
                    else:  # if it is a device
                        quantities_given = message

                    strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                    money_spent_inside -= energy * price  # money spent by buying energy from the subaggregator
                    energy_bought_inside -= energy  # the absolute value of energy bought inside
                    energy_available_production += energy  # the difference between the max and the min is consumed

            else:  # if there is a demand for a min of energy too
                energy_minimum = sorted_offers[i]["quantity_min"]  # the minimum quantity of energy asked
                energy_maximum = sorted_offers[i]["quantity"]  # the maximum quantity of energy asked

                if energy_minimum < - energy_available_production:  # if the quantity offered is superior to the rest of energy available
                    unwanted_cuts = strategy._catalog.get("unwanted_delivery_cuts")
                    strategy._catalog.set("unwanted_delivery_cuts", unwanted_cuts - energy_minimum - energy_available_production)
                    energy = - energy_available_production  # it is served partially, even if it is urgent
                else:
                    energy = energy_minimum

                message = strategy._create_decision_message()
                message["quantity"] = energy
                message["price"] = price
                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                    sorted_offers[i]["quantity_min"] = 0
                    sorted_offers[i]["quantity"] = energy_maximum - energy_minimum  # the need is updated
                else:  # if it is a device
                    quantities_given = message

                money_spent_inside -= energy * price  # money spent by buying energy from the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy bought inside
                energy_available_production += energy  # the difference between the max and the min is consumed
                sorted_offers[i]["quantity"] = energy_maximum - energy

    lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion
    for line_index in lines_to_remove:  # removing the already served elements
        sorted_offers.pop(line_index)

    return [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside]


# min consumption
def assess_min_conso(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["type"] != "storage":
            quantity_for_this_option += demand["quantity_min"]

    return quantity_for_this_option


def exchanges_min_conso(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


# no specific function for distribution, the canonical one is used
def distribution_min_conso(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    lines_to_remove = []  # a list containing the number of lines having to be removed
    for i in range(len(sorted_demands)):  # demands
        if sorted_demands[i]["type"] != "storage":
            energy = sorted_demands[i]["quantity"]
            name = sorted_demands[i]["name"]
            price = sorted_demands[i]["price"]
            price = min(price, max_price)

            if sorted_demands[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

                if energy > energy_available_consumption + 1e-6:  # if the quantity demanded is superior to the rest of energy available
                    unwanted_cuts = strategy._catalog.get("unwanted_delivery_cuts")
                    strategy._catalog.set("unwanted_delivery_cuts", unwanted_cuts + energy-energy_available_consumption)
                    energy = energy_available_consumption  # it is served partially, even if it is urgent

                message = strategy._create_decision_message()
                message["quantity"] = energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

            else:
                energy_minimum = sorted_demands[i]["quantity_min"]  # the minimum quantity of energy asked
                energy_maximum = sorted_demands[i]["quantity"]  # the maximum quantity of energy asked

                if energy_minimum > energy_available_consumption:  # if the quantity demanded is superior to the rest of energy available
                    unwanted_cuts = strategy._catalog.get("unwanted_delivery_cuts")
                    strategy._catalog.set("unwanted_delivery_cuts", unwanted_cuts + energy_minimum - energy_available_consumption)
                    energy = energy_available_consumption  # it is served partially, even if it is urgent
                else:
                    energy = energy_minimum

                message = strategy._create_decision_message()
                message["quantity"] = energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                    sorted_demands[i]["quantity_min"] = 0
                    sorted_demands[i]["quantity"] = energy_maximum - energy_minimum  # the need is updated
                else:  # if it is a device
                    quantities_given = message

                strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside
                sorted_demands[i]["quantity"] = energy_maximum - energy

    lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion
    for line_index in lines_to_remove:  # removing the already served elements
        sorted_demands.pop(line_index)

    return [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside]
