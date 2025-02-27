# This file records function managing different options for balancing the grid
from typing import List, Dict, Tuple
import pandas as pd

# ################################################################################################################
# Consumption - todo à vérifier avec Timothé
# ################################################################################################################
# dissipation
def assess_dissipation(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["name"] == "heat_sink":
            quantity_for_this_option += demand["quantity"]

    return quantity_for_this_option


def exchanges_dissipation(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_dissipation(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    i = 0
    name = "heat_sink"
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



# nothing
def assess_nothing_option(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    return quantity_for_this_option


def exchanges_nothing_option(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = 0
    return quantity_to_affect, quantities_and_prices


def distribution_nothing_option(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):

    return sorted_demands, 0, money_earned_inside, energy_sold_inside


# ################################################################################################################
# Production - todo à vérifier avec Timothé
# ################################################################################################################
# The Base load technology (biomass plant)
def assess_renewable_generation(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "biomass_plant":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_renewable_generation(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0.0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_renewable_generation(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    for offer_message in sorted_offers:
        if offer_message["name"] == "biomass_plant":
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


# The more flexible but more polluting energy generation system
def assess_fossil_generation(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = aggregator.capacity["buying"] / aggregator.efficiency

    return quantity_for_this_option


def exchanges_fossil_generation(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    # message = {element: strategy._messages["bottom-up"][element] for element in strategy._messages["bottom-up"]}
    message = strategy.__class__.information_message()
    quantity_remaining = max(0, quantity_to_affect - quantity_available_for_this_option)
    quantity_bought = quantity_to_affect - quantity_remaining

    message["energy_minimum"] = quantity_bought
    message["energy_nominal"] = quantity_bought
    message["energy_maximum"] = quantity_bought

    quantities_and_prices.append(message)

    return quantity_remaining, quantities_and_prices


def distribution_fossil_generation(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    return sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside




index = ["dissipation", "nothing"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_dissipation, exchanges_dissipation, distribution_dissipation],
        [assess_nothing_option, exchanges_nothing_option, distribution_nothing_option],
        ]
options_consumption = pd.DataFrame(index=index, columns=columns, data=data)

index = ["biomass", "gas"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_renewable_generation, exchanges_renewable_generation, distribution_renewable_generation],
        [assess_fossil_generation, exchanges_fossil_generation, distribution_fossil_generation]
        ]
options_production = pd.DataFrame(index=index, columns=columns, data=data)
