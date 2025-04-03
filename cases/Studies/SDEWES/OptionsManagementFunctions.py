# This file records function managing different options for balancing the grid
import math
from typing import List, Dict, Tuple
import pandas as pd


# ################################################################################################################
# consumption
# ################################################################################################################

# storage
def assess_storage(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["name"] == "BESS":
            quantity_for_this_option += demand["quantity"]

    return quantity_for_this_option


def exchanges_storage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_storage(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0
    name = "BESS"
    while sorted_demands[i]["name"] != name:  # as long as the storage is not found
        i += 1

    if sorted_demands[i]["name"] == name:
        if energy_available_consumption > sorted_demands[i]["quantity"]:  # if there is enough energy
            energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
        else:  # if there is not enough energy available
            energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
        price = sorted_demands[i]["price"]  # the price of energy
        price = min(price, max_price)

        message = strategy.__class__.decision_message()
        message["quantity"] = energy
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


# industrial
# def assess_load(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
#     quantity_for_this_option = 0
#
#     for demand in demands:
#         if demand["name"] == "background":
#             quantity_for_this_option += demand["quantity"] - demand["quantity_min"]
#
#     return quantity_for_this_option
#
#
# def exchanges_load(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
#     return quantity_to_affect, quantities_and_prices
#
#
# def distribution_load(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
#     i = 0
#     name = "background"
#     while sorted_demands[i]["name"] != name and i < len(sorted_demands) - 1:  # as long as the storage is not found
#         i += 1
#
#     if sorted_demands[i]["name"] == name:
#         if energy_available_consumption > sorted_demands[i]["quantity"]:  # if there is enough energy
#             energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
#         else:  # if there is not enough energy available
#             energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
#         price = sorted_demands[i]["price"]  # the price of energy
#         price = min(price, max_price)
#
#         Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
#         message = strategy.__class__.decision_message()
#         message["quantity"] = Emin + energy
#         message["price"] = price
#         if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
#             quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
#             quantities_given.append(message)
#         else:  # if it is a device
#             quantities_given = message
#
#         strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served
#
#         money_earned_inside += energy * price  # money earned by selling energy to the device
#         energy_sold_inside += energy  # the absolute value of energy sold inside
#         energy_available_consumption -= energy
#
#     return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside


# nothing (no storage is made and the industrial is curtailed)
def assess_nothing_option(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    return quantity_for_this_option


def exchanges_nothing_option(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_nothing_option(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):

    return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside


# ################################################################################################################
# production
# min

# production
def assess_prod(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "localDieselGenerator":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_prod(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    # quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_prod(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0
    name = "localDieselGenerator"
    while sorted_offers[i]["name"] != name:  # as long as the storage is not found
        i += 1

    if sorted_offers[i]["name"] == name:
        if energy_available_production > - sorted_offers[i]["quantity"]:  # if there is enough energy
            energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
        else:  # if there is not enough energy available
            energy = max(sorted_offers[i]["quantity"], - energy_available_production)  # the quantity of energy needed
        price = sorted_offers[i]["price"]  # the price of energy
        price = max(price, min_price)

        message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
        message["quantity"] = energy
        message["price"] = price

        if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
            quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
            quantities_given.append(message)
        else:  # if it is a device
            quantities_given = message

        strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

        money_spent_inside -= energy * price  # money spent by buying energy from the device
        energy_bought_inside -= energy  # the absolute value of energy bought inside
        energy_available_production += energy  # the difference between the max and the min is consumed

    return sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside


# unstore
def assess_unstorage(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for offer in offers:
        if offer["name"] == "BESS":
            quantity_for_this_option -= offer["quantity_min"]

    return quantity_for_this_option


def exchanges_unstorage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    # quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_unstorage(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0
    name = "BESS"
    while sorted_offers[i]["name"] != name and i < len(sorted_offers) - 1:  # as long as the storage is not found
        i += 1

    if sorted_offers[i]["name"] == name:
        if energy_available_production > - sorted_offers[i]["quantity_min"]:  # if there is enough energy
            energy = sorted_offers[i]["quantity_min"]  # the quantity of energy needed
        else:  # if there is not enough energy available
            energy = - energy_available_production  # the quantity of energy needed
        price = sorted_offers[i]["price"]  # the price of energy
        price = max(price, min_price)

        message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
        message["quantity"] = energy + strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # integration of decision taken regarding the charge
        message["price"] = price

        if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
            quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
            quantities_given.append(message)
        else:  # if it is a device
            quantities_given = message

        strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

        money_spent_inside -= energy * price  # money spent by buying energy from the device
        energy_bought_inside -= energy  # the absolute value of energy bought inside
        energy_available_production += energy  # the difference between the max and the min is consumed

    return sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside


# outside energy
def assess_buy_outside(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    return quantity_for_this_option


def exchanges_buy_outside(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    message = strategy.__class__.information_message()
    quantity_for_this_option = aggregator.capacity["buying"] / aggregator.efficiency
    quantity_remaining = max(0, quantity_to_affect - quantity_for_this_option)
    quantity_bought = quantity_to_affect - quantity_remaining

    message["energy_minimum"] = quantity_bought
    message["energy_nominal"] = quantity_bought
    message["energy_maximum"] = quantity_bought

    quantities_and_prices.append(message)

    return quantity_remaining, quantities_and_prices


def distribution_buy_outside(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside


index = ["storage", "nothing"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_storage, exchanges_storage, distribution_storage],
        [assess_nothing_option, exchanges_nothing_option, distribution_nothing_option],
        ]
options_consumption = pd.DataFrame(index=index, columns=columns, data=data)

index = ["production", "unstorage", "grid"]
data = [[assess_prod, exchanges_prod, distribution_prod],
        [assess_unstorage, exchanges_unstorage, distribution_unstorage],
        [assess_buy_outside, exchanges_buy_outside, distribution_buy_outside],
        ]
options_production = pd.DataFrame(index=index, columns=columns, data=data)