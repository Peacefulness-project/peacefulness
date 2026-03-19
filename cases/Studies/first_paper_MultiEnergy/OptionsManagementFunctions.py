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
        if demand["name"] == "Heat_storage":
            quantity_for_this_option += demand["quantity"]

    return quantity_for_this_option


def exchanges_storage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_storage(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0
    name = "Heat_storage"
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


# heat pump
def assess_sell_heat_pump(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if "heat_pump" in demand["name"]:
            quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_sell_heat_pump(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_sell_heat_pump(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0
    name = "heat_pump"
    while not name in sorted_demands[i]["name"]:  # as long as the storage is not found
        i += 1

    if name in sorted_demands[i]["name"]:
        name = sorted_demands[i]["name"]
        if energy_available_consumption > sorted_demands[i]["quantity"]:  # if there is enough energy
            energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
        else:  # if there is not enough energy available
            energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
        price = sorted_demands[i]["price"]  # the price of energy
        price = min(price, max_price)

        Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
        # message = strategy.__class__.decision_message()
        # message["quantity"] = Emin + energy
        # message["price"] = price

        message = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
        if isinstance(message['quantity'], list):
            idx = message['aggregator'].index(aggregator.name)
            message['quantity'][idx] = Emin + energy
            message['price'][idx] = price

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


# flexible chargers
def assess_chargers(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["name"] == "flexible_loads":
            quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_chargers(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_chargers(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0
    name = "flexible_loads"
    while sorted_demands[i]["name"] != name and i < len(sorted_demands) - 1:  # as long as the storage is not found
        i += 1

    if sorted_demands[i]["name"] == name:
        if energy_available_consumption > sorted_demands[i]["quantity"]:  # if there is enough energy
            energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
        else:  # if there is not enough energy available
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


# nothing (no storage is made and the industrial is curtailed)
def assess_nothing_option(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    return quantity_for_this_option


def exchanges_nothing_option(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_nothing_option(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):

    return sorted_demands, 0, money_earned_inside, energy_sold_inside


# outside energy
def assess_sell_outside(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    return quantity_for_this_option


def exchanges_sell_outside(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    message = strategy.__class__.information_message()
    quantity_for_this_option = aggregator.capacity["selling"] * aggregator.efficiency
    quantity_remaining = max(0, quantity_to_affect - quantity_for_this_option)
    quantity_sold = quantity_to_affect - quantity_remaining

    message["energy_minimum"] = quantity_sold
    message["energy_nominal"] = quantity_sold
    message["energy_maximum"] = quantity_sold

    quantities_and_prices.append(message)

    return quantity_remaining, quantities_and_prices


def distribution_sell_outside(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    return sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside


# ################################################################################################################
# production
# min

# heat production
def assess_prod_w2h(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "Waste_to_heat":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_prod_w2h(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    # quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_prod_w2h(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0
    name = "Waste_to_heat"
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


# heat pump
def assess_buy_heat_pump(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if "heat_pump" in demand["name"]:
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_buy_heat_pump(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_buy_heat_pump(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0
    name = "heat_pump"
    while not name in sorted_offers[i]["name"]:  # as long as the storage is not found
        i += 1

    if name in sorted_offers[i]["name"]:
        name = sorted_offers[i]["name"]
        if energy_available_production > - sorted_offers[i]["quantity"]:  # if there is enough energy
            energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
        else:  # if there is not enough energy available
            energy = max(sorted_offers[i]["quantity"], - energy_available_production)  # the quantity of energy needed
        price = sorted_offers[i]["price"]  # the price of energy
        price = max(price, min_price)

        # message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
        # message["quantity"] = energy
        # message["price"] = price

        message = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
        if isinstance(message['quantity'], list):
            idx = message['aggregator'].index(aggregator.name)
            message['quantity'][idx] = energy
            message['price'][idx] = price

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


# CHP
def assess_CHP(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "combined_heat_power":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_CHP(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    # quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_CHP(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0
    name = "combined_heat_power"
    if len(sorted_offers) > 0:
        while sorted_offers[i]["name"] != name:  # as long as the storage is not found
            i += 1

        if sorted_offers[i]["name"] == name:
            if energy_available_production > - sorted_offers[i]["quantity"]:  # if there is enough energy
                energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
            else:  # if there is not enough energy available
                energy = max(sorted_offers[i]["quantity"], - energy_available_production)  # the quantity of energy needed
            price = sorted_offers[i]["price"]  # the price of energy
            price = max(price, min_price)

            message = {element: strategy.__class__.decision_message()[element] for element in
                       strategy.__class__.decision_message()}
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
        if offer["name"] == "Heat_storage":
            quantity_for_this_option -= offer["quantity_min"]

    return quantity_for_this_option


def exchanges_unstorage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_unstorage(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0
    name = "Heat_storage"
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


# no energy production option
def assess_nada_option(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    return quantity_for_this_option


def exchanges_nada_option(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantities_and_prices: List[Dict]) -> Tuple:
    return quantity_to_affect, quantities_and_prices


def distribution_nada_option(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):

    return sorted_offers, 0, money_spent_inside, energy_bought_inside


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


index = ["flexible_chargers", "sellHP", "sellGrid", "nothing"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_chargers, exchanges_chargers, distribution_chargers],
        [assess_sell_heat_pump, exchanges_sell_heat_pump, distribution_sell_heat_pump],
        [assess_sell_outside, exchanges_sell_outside, distribution_sell_outside],
        [assess_nothing_option, exchanges_nothing_option, distribution_nothing_option],
        ]
options_consumption_1 = pd.DataFrame(index=index, columns=columns, data=data)

index = ["storage", "nothing"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_storage, exchanges_storage, distribution_storage],
        [assess_nothing_option, exchanges_nothing_option, distribution_nothing_option],
        ]
options_consumption_2 = pd.DataFrame(index=index, columns=columns, data=data)

index = ["buyCHP", "buyGrid", "nothing"]
data = [[assess_CHP, exchanges_CHP, distribution_CHP],
        [assess_buy_outside, exchanges_buy_outside, distribution_buy_outside],
        [assess_nada_option, exchanges_nada_option, distribution_nada_option],
        ]
options_production_1 = pd.DataFrame(index=index, columns=columns, data=data)

index = ["buyCHP", "buyHP", "buyW2H", "unstorage", "nothing"]
data = [[assess_CHP, exchanges_CHP, distribution_CHP],
        [assess_buy_heat_pump, exchanges_buy_heat_pump, distribution_buy_heat_pump],
        [assess_prod_w2h, exchanges_prod_w2h, distribution_prod_w2h],
        [assess_unstorage, exchanges_unstorage, distribution_unstorage],
        [assess_nada_option, exchanges_nada_option, distribution_nada_option],
        ]
options_production_2 = pd.DataFrame(index=index, columns=columns, data=data)
