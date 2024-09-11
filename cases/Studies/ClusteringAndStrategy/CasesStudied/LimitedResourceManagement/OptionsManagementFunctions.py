# This file records function managing different options for balancing the grid
import math
from typing import List, Dict, Tuple
import pandas as pd


# ################################################################################################################
# consumption
# ################################################################################################################

# short term storage (spatial heating)
def assess_short_term_storage(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["name"] == "heating":
            quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_short_term_storage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_short_term_storage(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0

    if len(sorted_demands) >= 1:  # if there are offers
        while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
            if sorted_demands[i]["name"] == "heating":
                name = sorted_demands[i]["name"]
                energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
                price = sorted_demands[i]["price"]  # the price of energy
                price = min(price, max_price)

                Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = strategy.__class__.decision_message()
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

            i += 1

        # this block gives the remaining energy to the last unserved device
        if sorted_demands[i]["quantity"] and sorted_demands[i]["name"] != "heating":  # if the demand really exists
            name = sorted_demands[i]["name"]
            energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
            price = sorted_demands[i]["price"]  # the price of energy
            price = min(price, max_price)

            Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
            message = strategy.__class__.decision_message()
            message["quantity"] = Emin + energy
            message["price"] = price
            if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                quantities_given.append(message)
            else:  # if it is a device
                quantities_given = message

            strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

            money_earned_inside += energy * price  # money earned by selling energy to the device
            energy_sold_inside += energy  # the absolute value of energy sold inside
            energy_available_consumption -= energy

    return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside


# long term storage (geothermy)
def assess_long_term_storage(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["name"] == "heat_storage":
            quantity_for_this_option += demand["quantity"]

    return quantity_for_this_option


def exchanges_long_term_storage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_long_term_storage(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0

    if len(sorted_demands) >= 1:  # if there are offers
        while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
            if sorted_demands[i]["name"] == "heat_storage":
                name = sorted_demands[i]["name"]
                energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
                price = sorted_demands[i]["price"]  # the price of energy
                price = min(price, max_price)

                Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = strategy.__class__.decision_message()
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

            i += 1

        # this block gives the remaining energy to the last unserved device
        if sorted_demands[i]["quantity"] and sorted_demands[i]["name"] != "heat_storage":  # if the demand really exists
            name = sorted_demands[i]["name"]
            energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
            price = sorted_demands[i]["price"]  # the price of energy
            price = min(price, max_price)

            Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
            message = strategy.__class__.decision_message()
            message["quantity"] = Emin + energy
            message["price"] = price
            if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                quantities_given.append(message)
            else:  # if it is a device
                quantities_given = message

            strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

            money_earned_inside += energy * price  # money earned by selling energy to the device
            energy_sold_inside += energy  # the absolute value of energy sold inside
            energy_available_consumption -= energy

    return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside


# nothing (no storage is made and the heat pump is less used)
def assess_nothing_option(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    return quantity_for_this_option


def exchanges_nothing_option(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = 0
    return quantity_to_affect, quantities_and_prices


def distribution_nothing_option(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):

    return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside


# ################################################################################################################
# production
# min

# heat pump
def assess_heat_pump(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "heat_pump":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_heat_pump(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_heat_pump(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0

    if len(sorted_offers) >= 1:  # if there are offers
        while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
            if sorted_offers[i]["name"] == "heat_pump":
                name = sorted_offers[i]["name"]
                energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
                price = sorted_offers[i]["price"]  # the price of energy
                price = max(price, min_price)

                Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy sold inside
                energy_available_production += energy

            i += 1

        # this line gives the remnant of energy to the last unserved device
        if sorted_offers[i]["quantity"] and sorted_offers[i]["name"] == "heat_pump":  # if the demand really exists
            name = sorted_offers[i]["name"]
            energy = max(sorted_offers[i]["quantity"], - energy_available_production)  # the quantity of energy needed
            price = sorted_offers[i]["price"]  # the price of energy
            price = max(price, min_price)

            Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
            message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
            message["quantity"] = Emin + energy
            message["price"] = price

            if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                quantities_given.append(message)
            else:  # if it is a device
                quantities_given = message

            strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

            money_spent_inside -= energy * price  # money spent by buying energy from the device
            energy_bought_inside -= energy  # the absolute value of energy bought inside

    return sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside


# unstore
def assess_unstorage(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "heat_storage":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_unstorage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_unstorage(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0

    if len(sorted_offers) >= 1:  # if there are offers
        while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
            if sorted_offers[i]["name"] == "heat_storage":
                name = sorted_offers[i]["name"]
                energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
                price = sorted_offers[i]["price"]  # the price of energy
                price = max(price, min_price)

                Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy sold inside
                energy_available_production += energy

            i += 1

        # this line gives the remnant of energy to the last unserved device
        if sorted_offers[i]["quantity"] and sorted_offers[i]["name"] == "heat_storage":  # if the demand really exists
            name = sorted_offers[i]["name"]
            energy = max(sorted_offers[i]["quantity"], - energy_available_production)  # the quantity of energy needed
            price = sorted_offers[i]["price"]  # the price of energy
            price = max(price, min_price)

            Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
            message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
            message["quantity"] = Emin + energy
            message["price"] = price

            if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                quantities_given.append(message)
            else:  # if it is a device
                quantities_given = message

            strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

            money_spent_inside -= energy * price  # money spent by buying energy from the device
            energy_bought_inside -= energy  # the absolute value of energy bought inside

    return sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside


index = ["spatial_heating", "long_term_storage", "nothing"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_short_term_storage, exchanges_short_term_storage, distribution_short_term_storage],
        [assess_long_term_storage, exchanges_long_term_storage, distribution_long_term_storage],
        [assess_nothing_option, exchanges_nothing_option, distribution_nothing_option],
        ]
options_consumption = pd.DataFrame(index=index, columns=columns, data=data)

index = ["heat_pump", "long_term_unstorage"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_heat_pump, exchanges_heat_pump, distribution_heat_pump],
        [assess_unstorage, exchanges_unstorage, distribution_unstorage],
        ]
options_production = pd.DataFrame(index=index, columns=columns, data=data)
