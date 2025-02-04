# This file records function managing different options for balancing the grid
from typing import List, Dict, Tuple
import pandas as pd

# ################################################################################################################
# Consumption - todo à vérifier avec Timothé
# ################################################################################################################
# Heating loads
def assess_demand(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["name"] in ["old_house", "new_house", "office"]:
            quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_demand(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0.0, quantity_to_affect - quantity_available_for_this_option)
    # print("storage, " + str(quantity_to_affect))
    return quantity_to_affect, quantities_and_prices


def distribution_demand(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    for demand_message in sorted_demands:
        if demand_message["name"] in ["old_house", "new_house", "office"]:
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

# Thermal energy storage
def assess_charging_storage(strategy: "Strategy", aggregator: "Aggregator", demands: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in demands:
        if demand["name"] == "DHN_pipelines":
            quantity_for_this_option += demand["quantity"]

    return quantity_for_this_option


def exchanges_charging_storage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = max(0.0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_charging_storage(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
    for demand_message in sorted_demands:
        if demand_message["name"] == "DHN_pipelines":
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


# nothing (no storage is made and the biomass plant is less used)
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
def assess_base_load(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "incinerator":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_base_load(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0.0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_base_load(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    for offer_message in sorted_offers:
        if offer_message["name"] == "incinerator":
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
def assess_peak_load(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "fast_gas_boiler":
            quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

    return quantity_for_this_option


def exchanges_peak_load(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0.0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_peak_load(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    for offer_message in sorted_offers:
        if offer_message["name"] == "fast_gas_boiler":
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


# Discharging
def assess_discharging_storage(strategy: "Strategy", aggregator: "Aggregator", offers: List[Dict]) -> float:
    quantity_for_this_option = 0

    for demand in offers:
        if demand["name"] == "DHN_pipelines":
            quantity_for_this_option -= demand["quantity"]

    return quantity_for_this_option


def exchanges_discharging_storage(strategy: "Strategy", aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
    quantity_to_affect = - max(0.0, quantity_to_affect - quantity_available_for_this_option)
    return quantity_to_affect, quantities_and_prices


def distribution_discharging_storage(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
    for offer_message in sorted_offers:
        if offer_message["name"] == "DHN_pipelines":
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


# index = ["heat_loads", "charging_storage", "nothing"]
index = ["heat_loads", "nothing"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_demand, exchanges_demand, distribution_demand],
        # [assess_charging_storage, exchanges_charging_storage, distribution_charging_storage],
        [assess_nothing_option, exchanges_nothing_option, distribution_nothing_option],
        ]
options_consumption = pd.DataFrame(index=index, columns=columns, data=data)

# index = ["heat_baseload", "heat_peakload", "discharging_storage"]
index = ["heat_baseload", "heat_peakload"]
columns = ["assess", "exchange", "distribute"]
data = [[assess_base_load, exchanges_base_load, distribution_base_load],
        [assess_peak_load, exchanges_peak_load, distribution_peak_load]
        # , [assess_discharging_storage, exchanges_discharging_storage, distribution_discharging_storage],
        ]
options_production = pd.DataFrame(index=index, columns=columns, data=data)
