# This file records function managing different options for balancing the grid
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
    # print("storage, " + str(quantity_to_affect))
    return quantity_to_affect, quantities_and_prices


def distribution_short_term_storage(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    for demand_message in sorted_demands:
        if demand_message["name"] == "heating":
            name = demand_message["name"]
            energy = min(demand_message["quantity"], energy_available_consumption)  # the quantity of energy needed
            price = demand_message["price"]  # the price of energy
            price = min(price, max_price)

            Emin = demand_message["quantity_min"]  # we get back the minimum, which has already been served
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
    for demand_message in sorted_demands:
        if demand_message["name"] == "heat_storage":
            # print("dnd", demand_message["quantity"], energy_available_consumption)
            name = demand_message["name"]
            energy = min(demand_message["quantity"], energy_available_consumption)  # the quantity of energy needed
            price = demand_message["price"]  # the price of energy
            price = min(price, max_price)

            # Emin = demand_message["quantity_min"]  # we get back the minimum, which has already been served
            message = strategy.__class__.decision_message()
            message["quantity"] += energy
            message["price"] = price

            quantities_given = message

            strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

            money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
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

    return sorted_demands, 0, money_earned_inside, energy_sold_inside


# ################################################################################################################
# production
# ################################################################################################################

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
    for offer_message in sorted_offers:
        if offer_message["name"] == "heat_pump":
            name = offer_message["name"]
            # print("qzefswf", offer_message["quantity"], - energy_available_production)
            energy = max(offer_message["quantity"], - energy_available_production)  # the quantity of energy needed
            price = offer_message["price"]  # the price of energy
            price = min(price, min_price)

            Emin = offer_message["quantity_min"]  # we get back the minimum, which has already been served
            message = strategy.__class__.decision_message()
            message["quantity"] = Emin + energy
            message["price"] = price

            quantities_given = message
            strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

            money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
            energy_bought_inside -= energy  # the absolute value of energy sold inside
            energy_available_production += energy
            # print(energy)

    return sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside


# unstore
def assess_unstorage(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "heat_storage":
            quantity_for_this_option -= demand["quantity"]

    return quantity_for_this_option


def exchanges_unstorage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_unstorage(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    for offer_message in sorted_offers:
        if offer_message["name"] == "heat_storage":
            name = offer_message["name"]
            energy = max(offer_message["quantity"], - energy_available_production)  # the quantity of energy needed
            price = offer_message["price"]  # the price of energy
            price = min(price, min_price)

            message = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
            # Emin = offer_message["quantity_min"]  # we get back the minimum, which has already been served
            message["quantity"] += energy
            message["price"] = price  # bon bah c'est le prix du déstockage qui prend le dessus dans tous les cas

            quantities_given = message
            strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is dserved

            money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
            energy_bought_inside -= energy  # the absolute value of energy sold inside
            energy_available_production += energy

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
