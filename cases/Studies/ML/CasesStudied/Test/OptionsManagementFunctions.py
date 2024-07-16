# This file records function managing different options for balancing the grid
from typing import List, Dict, Tuple
import pandas as pd


# ################################################################################################################
# production
# ################################################################################################################

# store
def assess_storage(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["type"] == "storage":
            quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_storage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_storage(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0

    if len(sorted_demands) >= 1:  # if there are offers
        while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
            if sorted_demands[i]["type"] == "storage":
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
        if sorted_demands[i]["quantity"] and sorted_demands[i]["type"] != "storage":  # if the demand really exists
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


# outside energy
def assess_buy_outside(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = aggregator.capacity["buying"] / aggregator.efficiency

    return quantity_for_this_option


def exchanges_buy_outside(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    # message = {element: strategy._messages["bottom-up"][element] for element in strategy._messages["bottom-up"]}
    message = strategy.__class__.information_message()
    quantity_remaining = max(0, quantity_to_affect - quantity_available_for_this_option)
    quantity_bought = quantity_to_affect - quantity_remaining

    message["energy_minimum"] = quantity_bought
    message["energy_nominal"] = quantity_bought
    message["energy_maximum"] = quantity_bought

    quantities_and_prices.append(message)

    return quantity_remaining, quantities_and_prices


def distribution_buy_outside(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside

# ################################################################################################################
# consumption side

# soft DSM
def assess_soft_DSM_conso(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["emergency"] <= 0.9 and demand["type"] != "storage":
            quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option

def exchanges_soft_DSM_conso(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices

def distribution_soft_DSM_conso(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0

    if len(sorted_demands) >= 1:  # if there are offers
        while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
            if sorted_demands[i]["emergency"] <= 0.9 and sorted_demands[i]["type"] != "storage":
                name = sorted_demands[i]["name"]
                energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
                price = sorted_demands[i]["price"]  # the price of energy
                price = min(price, max_price)

                Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
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
        if sorted_demands[i]["quantity"] and sorted_demands[i]["emergency"] <= 0.9 and sorted_demands[i]["type"] != "storage":  # if the demand really exists
            name = sorted_demands[i]["name"]
            energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
            price = sorted_demands[i]["price"]  # the price of energy
            price = min(price, max_price)

            Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
            message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
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

# hard DSM
def assess_hard_DSM_conso(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["emergency"] > 0.9 and demand["type"] != "storage":
            quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option

def exchanges_hard_DSM_conso(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices

def distribution_hard_DSM_conso(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0

    if len(sorted_demands) >= 1:  # if there are offers
        while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
            if sorted_demands[i]["emergency"] > 0.9 and sorted_demands[i]["type"] != "storage":
                name = sorted_demands[i]["name"]
                energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
                price = sorted_demands[i]["price"]  # the price of energy
                price = min(price, max_price)

                Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: strategy.__class__.decision_message()[element] for element in strategy.__class__.decision_message()}
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
        if sorted_demands[i]["quantity"] and sorted_demands[i]["emergency"] > 0.9 and sorted_demands[i]["type"] != "storage":  # if the demand really exists
            name = sorted_demands[i]["name"]
            energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
            price = sorted_demands[i]["price"]  # the price of energy
            price = min(price, max_price)

            Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
            message = {element: strategy._messages["top-down"][element] for element in strategy._messages["top-down"]}
            message["quantity"] = Emin + energy
            message["price"] = price
            if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                quantities_given.append(message)
            else:  # if it is a device
                quantities_given = message

            strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded",
                              quantities_given)  # it is served

            money_earned_inside += energy * price  # money earned by selling energy to the device
            energy_sold_inside += energy  # the absolute value of energy sold inside
            energy_available_consumption -= energy

    return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside


# ################################################################################################################
# production
# min

# soft DSM
def assess_soft_DSM_prod(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["emergency"] <= 0.9 and demand["type"] != "storage":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option

def exchanges_soft_DSM_prod(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices

def distribution_soft_DSM_prod(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0

    if len(sorted_offers) >= 1:  # if there are offers
        while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
            if sorted_offers[i]["emergency"] <= 0.9 and sorted_offers[i]["type"] != "storage":
                name = sorted_offers[i]["name"]
                energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
                price = sorted_offers[i]["price"]  # the price of energy
                price = max(price, min_price)

                Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = strategy.__class__.decision_message()
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
        if sorted_offers[i]["quantity"] and sorted_offers[i]["emergency"] <= 0.9 and sorted_offers[i]["type"] != "storage":  # if the demand really exists
            name = sorted_offers[i]["name"]
            energy = max(sorted_offers[i]["quantity"], - energy_available_production)  # the quantity of energy needed
            price = sorted_offers[i]["price"]  # the price of energy
            price = max(price, min_price)

            Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
            message = strategy.__class__.decision_message()
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

# hard DSM
def assess_hard_DSM_prod(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["emergency"] > 0.9 and demand["type"] != "storage":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option

def exchanges_hard_DSM_prod(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices

def distribution_hard_DSM_prod(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0

    if len(sorted_offers) >= 1:  # if there are offers
        while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
            if sorted_offers[i]["emergency"] > 0.9 and sorted_offers[i]["type"] != "storage":
                name = sorted_offers[i]["name"]
                energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
                price = sorted_offers[i]["price"]  # the price of energy
                price = max(price, min_price)

                Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = strategy.__class__.decision_message()
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
        if sorted_offers[i]["quantity"] and sorted_offers[i]["emergency"] > 0.9 and sorted_offers[i]["type"] != "storage":  # if the demand really exists
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
        if demand["type"] == "storage":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option

def exchanges_unstorage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices

def distribution_unstorage(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    i = 0

    if len(sorted_offers) >= 1:  # if there are offers
        while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
            if sorted_offers[i]["type"] == "storage":
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
        if sorted_offers[i]["quantity"] and sorted_offers[i]["type"] == "storage":  # if the demand really exists
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

# outside energy
def assess_sell_outside(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = aggregator.capacity["selling"] * aggregator.efficiency

    return quantity_for_this_option


def exchanges_sell_outside(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    message = {element: strategy.__class__.information_message()[element] for element in
               strategy.__class__.information_message()}
    quantity_remaining = max(0, quantity_to_affect - quantity_available_for_this_option)
    quantity_sold = quantity_to_affect - quantity_remaining

    message["energy_minimum"] = - quantity_sold
    message["energy_nominal"] = - quantity_sold
    message["energy_maximum"] = - quantity_sold

    quantities_and_prices.append(message)

    return quantity_remaining, quantities_and_prices


def distribution_sell_outside(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float,
                               energy_bought_inside: float):
    return sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside


index = ["soft_DSM_conso", "hard_DSM_conso", "buy_outside_emergency", "store"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_soft_DSM_conso, exchanges_soft_DSM_conso, distribution_soft_DSM_conso],
        [assess_hard_DSM_conso, exchanges_hard_DSM_conso, distribution_hard_DSM_conso],
        [assess_buy_outside, exchanges_buy_outside, distribution_buy_outside],
        [assess_storage, exchanges_storage, distribution_storage]
        ]
options_consumption = pd.DataFrame(index=index, columns=columns, data=data)

index = ["soft_DSM_prod", "hard_DSM_prod", "sell_outside_emergency", "unstore"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_soft_DSM_prod, exchanges_soft_DSM_prod, distribution_soft_DSM_prod],
        [assess_hard_DSM_prod, exchanges_hard_DSM_prod, distribution_hard_DSM_prod],
        [assess_sell_outside, exchanges_sell_outside, distribution_sell_outside],
        [assess_unstorage, exchanges_unstorage, distribution_unstorage]
        ]
options_production = pd.DataFrame(index=index, columns=columns, data=data)
