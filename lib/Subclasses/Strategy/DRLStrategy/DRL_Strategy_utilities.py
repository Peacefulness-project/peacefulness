# In this file, some utilities are defined !
# In this file, we define a utility method to extract the information message from all the devices under an aggregator.
# We assume that devices are only visible to the aggregator which is directly managing them.
# As such, a superior aggregator is blind towards the devices managed by its subaggregators.
# We also extract the forecasting predictions of each subaggregator.

import numpy as np
import pandas as pd
import random
import math
from typing import Tuple, Dict, Callable, List, Optional
from copy import deepcopy

import json
from collections import defaultdict, deque

from src.common.Aggregator import Aggregator
from src.common.Strategy import Strategy


# ##########################################################################################
# Ascending interface/bottom_up_phase utilities
# ##########################################################################################
def determine_energy_prices(catalog: "Catalog", aggregator: "Aggregator", min_price: float, max_price: float):  # todo à revoir
    """
    This method is used to compute and return both the prices for energy selling and buying.
    """
    # First, we retrieve the energy prices proposed by the devices managed by the aggregator
    managed_devices_buying_prices = []
    managed_devices_buying_energies = []
    managed_devices_selling_prices = []
    managed_devices_selling_energies = []
    for device_name in aggregator.devices:
        message = catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")
        price = message["price"]
        Emax = message["energy_maximum"]
        Emin = message["energy_minimum"]
        if message["type"] != "storage":
            if Emax < 0:  # if the device wants to sell energy
                managed_devices_selling_prices.append(price)
                if Emax != Emin:
                    managed_devices_selling_energies.append(abs(Emax - Emin))
                else:
                    managed_devices_selling_energies.append(abs(Emax))
            elif Emax > 0:  # if the device wants to buy energy
                managed_devices_buying_prices.append(price)
                if Emax != Emin:
                    managed_devices_buying_energies.append(abs(Emax - Emin))
                else:
                    managed_devices_buying_energies.append(abs(Emax))
        else:
            if Emin < 0 < Emax:  # if the storage device is flexible
                managed_devices_selling_prices.append(price)
                managed_devices_buying_prices.append(price)
                managed_devices_selling_energies.append(abs(Emin))
                managed_devices_buying_energies.append(abs(Emax))
            elif Emin > 0:  # if the storage device only want to charge
                if Emax != Emin:
                    managed_devices_buying_energies.append(abs(Emax - Emin))
                else:
                    managed_devices_buying_energies.append(abs(Emax))
            elif Emax < 0:  # if the storage device only want to discharge
                managed_devices_selling_prices.append(price)
                if Emax != Emin:
                    managed_devices_selling_energies.append(abs(Emax - Emin))
                else:
                    managed_devices_selling_energies.append(abs(Emax))

    # Then, we retrieve the energy prices proposed by the sub-aggregators managed by the aggregator
    subaggregators_buying_prices = []
    subaggregators_buying_energies = []
    subaggregators_selling_prices = []
    subaggregators_selling_energies = []
    for subaggregator in aggregator.subaggregators:
        if f"Energy asked from {subaggregator.name} to {aggregator.name}" in catalog.keys:
            wanted_energy = catalog.get(f"Energy asked from {subaggregator.name} to {aggregator.name}")
        else:
            wanted_energy = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
        if isinstance(wanted_energy, list):  # into_list is not automatically used because of the if condition
            wanted_energy = wanted_energy[0]
        price = wanted_energy["price"]
        Emax = wanted_energy["energy_maximum"]
        Emin = wanted_energy["energy_minimum"]
        if Emax < 0:  # if the subaggregator wants to sell energy
            subaggregators_selling_prices.append(price)
            if Emax != Emin:
                subaggregators_selling_energies.append(Emax - Emin)
            else:
                subaggregators_selling_energies.append(Emax)
        elif Emax > 0:  # if the subaggregator wants to buy energy
            subaggregators_buying_prices.append(price)
            if Emax != Emin:
                subaggregators_buying_energies.append(Emax - Emin)
            else:
                subaggregators_buying_energies.append(Emax)

    # extending the lists into each corresponding list
    buying_prices = managed_devices_buying_prices + subaggregators_buying_prices
    buying_energies = managed_devices_buying_energies + subaggregators_buying_energies
    selling_prices = managed_devices_selling_prices + subaggregators_selling_prices
    selling_energies = managed_devices_selling_energies + subaggregators_selling_energies

    for index in range(len(buying_prices)):  # contribution or proportion of each device/subaggregator to the internal buying price
        buying_prices[index] = buying_prices[index] * buying_energies[index] / sum(buying_energies)
    for index in range(len(selling_prices)):  # contribution or proportion of each device/subaggregator to the internal selling price
        selling_prices[index] = selling_prices[index] * selling_energies[index] / sum(selling_energies)

    if buying_prices:
        buying_price = min(sum(buying_prices), max_price)
    else:
        buying_price = max_price
    if selling_prices:
        selling_price = max(sum(selling_prices), min_price)
    else:
        selling_price = min_price

    return buying_price, selling_price


def my_devices(catalog: "Catalog", aggregator: "Aggregator") -> Tuple[Dict, Dict]:
    """
    This function is used to create the formalism message for each aggregator.
    Recursion is not needed. (needs confirmation from Timothé)
    """
    formalism_message = {aggregator.name: {"Energy_Consumption": {}, "Energy_Production": {}, "Energy_Storage": {}}}
    converter_message = {aggregator.name: {"Energy_Conversion": {}}}
    devices_list = []
    my_time = catalog.get("simulation_time")
    # Retrieving the list of devices managed by the aggregator
    for device_name in aggregator.devices:
        devices_list.append(catalog.devices[device_name])

    # Getting the specific message from the devices
    for device in devices_list:
        specific_message = deepcopy(catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted"))
        Emax = specific_message["energy_maximum"]
        Enom = specific_message["energy_nominal"]
        Emin = specific_message["energy_minimum"]
        if Enom == Emax:  # if the demand (consumption or production) is urgent
            Emin = Emax

        intermediate_dict = {**specific_message}
        # intermediate_dict.pop('aggregator')
        intermediate_dict.pop('energy_minimum')
        intermediate_dict.pop('energy_nominal')
        intermediate_dict.pop('energy_maximum')
        intermediate_dict.pop('price')
        # intermediate_dict.pop('CO2')  # todo voir après comment traiter les other data related to operational objectives

        if specific_message["type"] == "standard":  # if the device/energy system is either for consumption/production
            if Emax < 0:  # the energy system/device produces energy
                intermediate_dict.pop('type')
                formalism_message[aggregator.name]["Energy_Production"] = {**formalism_message[aggregator.name]["Energy_Production"], **{device.name: {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}}}
                specific_message.clear()
            elif Emax > 0:  # the energy system/device consumes energy
                intermediate_dict.pop('type')
                formalism_message[aggregator.name]["Energy_Consumption"] = {**formalism_message[aggregator.name]["Energy_Consumption"], **{device.name: {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}}}
                specific_message.clear()
        elif specific_message["type"] == "storage":  # if the device/energy system is for storage
            intermediate_dict.pop('type')
            # Calculating the total efficiency of the storage cycle
            my_charging_efficiency, my_discharging_efficiency = intermediate_dict["efficiency"].values()
            intermediate_dict["efficiency"] = my_charging_efficiency * my_discharging_efficiency
            # Calculating the current ESS capacity in kWh
            if my_time > 0:
                intermediate_dict["state_of_charge"] += 0.2
            intermediate_dict["capacity"] *= intermediate_dict["state_of_charge"]
            formalism_message[aggregator.name]["Energy_Storage"] = {**formalism_message[aggregator.name]["Energy_Storage"], **{device.name: {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}}}
            specific_message.clear()
        elif specific_message["type"] == "converter":  # if the device/energy system is for conversion
            intermediate_dict.pop('type')  # todo voir comment traiter les systèmes de conversion si efficiency est donnée de la meme maniere que le stockage
            converter_message[aggregator.name]["Energy_Conversion"] = {**converter_message[aggregator.name]["Energy_Conversion"], **{device.name: {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}}}
            specific_message.clear()

    return formalism_message, converter_message


def if_it_exists(my_data, my_func: Callable, additional_data_1=None, additional_data_2=None):
    if my_data:
        if not additional_data_1 and not additional_data_2:
            return my_func(my_data)
        elif additional_data_1 and not additional_data_2:
            return my_func(my_data, additional_data_1)
        elif additional_data_2 and not additional_data_1:
            return my_func(my_data, additional_data_2)
        else:
            return my_func(my_data, additional_data_1, additional_data_2)
    else:
        return 0.0


def my_basic_share(my_data, max_value, min_value):
    if my_data and max_value and min_value:
        if sum(max_value) == 0 and sum(min_value) == 0:
            return_value = 0.0
        else:
            return_value = sum(my_data) / ((sum(max_value) + sum(min_value)) / 2)
        return return_value


def mutualize_formalism_message(formalism_dict: dict) -> dict:
    """
    This function regroups the formalism dict around the typology of energy systems.
    """
    # Preparing the dict
    return_dict = {"Energy_Consumption": {}, "Energy_Production": {}, "Energy_Storage": {}}
    consumption_dict = {}
    production_dict = {}
    storage_dict = {}
    for aggregator_name in formalism_dict.keys():
        consumption_dict = {**consumption_dict, **formalism_dict[aggregator_name]["Energy_Consumption"]}
        production_dict = {**production_dict, **formalism_dict[aggregator_name]["Energy_Production"]}
        storage_dict = {**storage_dict, **formalism_dict[aggregator_name]["Energy_Storage"]}

    # Energy consumption and production associated dict of values
    energy_min = []
    energy_max = []
    flexibility = []
    interruptibility = []
    coming_volume = []

    for typology in [consumption_dict, production_dict]:
        for device_name in typology:
            for element in typology[device_name]:
                if element == 'energy_minimum':
                    energy_min.append(typology[device_name][element])
                elif element == 'energy_maximum':
                    energy_max.append(typology[device_name][element])
                elif element == 'flexibility':  # todo removed break, to take into account the length/number of steps where my device is flexible (A CHECKER AVEC TIMOTHE ET BRUNO)
                    if not isinstance(typology[device_name][element], list) and typology[device_name][element] != 0:
                        flexibility.append((energy_min[-1] + energy_max[-1]) / 2)
                    elif isinstance(typology[device_name][element], list):
                        for flexi in typology[device_name][element]:
                            if flexi != 0:
                                flexibility.append((energy_min[-1] + energy_max[-1]) / 2)
                                break
                elif element == 'interruptibility':  # todo removed break, to take into account the length/number of steps where my device is interruptible (A CHECKER AVEC TIMOTHE ET BRUNO)
                    if not isinstance(typology[device_name][element], list) and typology[device_name][element] != 0:
                        interruptibility.append((energy_min[-1] + energy_max[-1]) / 2)
                    elif isinstance(typology[device_name][element], list):
                        for inter in typology[device_name][element]:
                            if inter != 0:
                                interruptibility.append((energy_min[-1] + energy_max[-1]) / 2)
                                break
                else:
                    coming_volume.append(typology[device_name][element])

        if typology == consumption_dict and len(energy_min) != 0:  # at least one consumer device is managed by the aggregator
            return_dict["Energy_Consumption"] = {'energy_minimum': if_it_exists(energy_min, sum), 'energy_maximum': if_it_exists(energy_max, sum),
                                                 'flexibility': if_it_exists(flexibility, my_basic_share, energy_max, energy_min),
                                                 'interruptibility': if_it_exists(interruptibility, my_basic_share, energy_max, energy_min),
                                                 'coming_volume': if_it_exists(coming_volume, sum)}
            energy_min.clear()
            energy_max.clear()
            flexibility.clear()
            interruptibility.clear()
            coming_volume.clear()

        elif typology == production_dict and len(energy_min) != 0:  # at least one producer device is managed by the aggregator
            return_dict["Energy_Production"] = {'energy_minimum': if_it_exists(energy_min, sum), 'energy_maximum': if_it_exists(energy_max, sum),
                                                'flexibility': if_it_exists(flexibility, my_basic_share, energy_max, energy_min),
                                                'interruptibility': if_it_exists(interruptibility, my_basic_share, energy_max, energy_min),
                                                'coming_volume': if_it_exists(coming_volume, sum)}

    # Energy storage associated dict of values
    energy_min = []
    energy_max = []
    state_of_charge = []
    capacity = []
    self_discharge_rate = []
    efficiency = []

    for device_name in storage_dict:
        for element in storage_dict[device_name]:
            if element == 'energy_minimum':
                energy_min.append(storage_dict[device_name][element])
            elif element == 'energy_maximum':
                energy_max.append(storage_dict[device_name][element])
            elif element == 'state_of_charge':
                state_of_charge.append(storage_dict[device_name][element] * ((energy_min[-1] + energy_max[-1]) / 2))
            elif element == 'capacity':
                capacity.append(storage_dict[device_name][element])
            elif element == 'self_discharge_rate':
                self_discharge_rate.append(abs(storage_dict[device_name][element]) * ((energy_min[-1] + energy_max[-1]) / 2))
            else:
                efficiency.append(storage_dict[device_name][element] * ((energy_min[-1] + energy_max[-1]) / 2))

    if len(energy_min) != 0:  # at least one storage device is managed by the aggregator
        return_dict["Energy_Storage"] = {'energy_minimum': if_it_exists(energy_min, sum), 'energy_maximum': if_it_exists(energy_max, sum),
                                         'state_of_charge': if_it_exists(state_of_charge, my_basic_share, energy_max, energy_min),
                                         'capacity': if_it_exists(capacity, sum),
                                         'self_discharge_rate': abs(if_it_exists(self_discharge_rate, my_basic_share, energy_max, energy_min)),  # todo added the abs here in order to only get positive values in the input state (normalization between 0 and 1)
                                         'efficiency': if_it_exists(efficiency, my_basic_share, energy_max, energy_min)}

    return return_dict


# ##########################################################################################
# Descending interface/top_down_phase utilities
# ##########################################################################################
def from_tensor_to_dict(actions: np.ndarray, aggregators: list, agent: "Agent") -> Tuple[dict, dict]:
    """
    This method is used to translate the actions taken by the DRL agent into results understood by Peacefulness.
    The decision is to be stored.
    The return dict is under the format: {'Aggregator_1': {'Energy_Consumption': , 'Energy_Production': ...}, ...}
    The dict concerning energy exchanges is also returned.
    """
    list_of_columns = []
    if not agent.inference_flag:  # when training the model
        # Getting relevant info from the peacefulness_grid class considered for the RL agent
        agent_grid_topology = agent.grid.get_topology  # the return of the get_topology method
        agent_storage_devices = agent.grid.get_storage  # the return of the get_storage method
    else:  # while exploiting the model (inference)
        agent_grid_topology = agent.grid_topology[0]
        agent_storage_devices = {"dummy_key": 0}  # todo to be manually changed to 0 if needed during inference
    number_of_energy_exchanges_actions = actions_related_to_energy_exchange(agent_grid_topology)

    # Grouping actions into ones related to energy exchanges and ones related to management of energy consumption, production and storage inside the aggregators
    actions_related_to_aggregators = actions[:-sum(number_of_energy_exchanges_actions)]
    actions_related_to_exchange = actions[-sum(number_of_energy_exchanges_actions):]

    # Getting the dimensions of the dataframe
    number_of_aggregators = len(aggregators)  # index of the dataframe
    number_of_actions = int(len(actions_related_to_aggregators) / number_of_aggregators)  # number of columns
    if number_of_actions == 3:  # presence of energy consumers, production and storage
        list_of_columns.extend(["Energy_Consumption", "Energy_Production", "Energy_Storage"])
    elif number_of_actions == 2:  # presence of either energy consumers/production, consumers/storage or production/storage
        if max(agent_storage_devices.values()) == 0:  # presence of only energy consumers & production
            list_of_columns.extend(["Energy_Consumption", "Energy_Production"])
        else:
            if np.all(actions_related_to_aggregators < 0):  # presence of only energy production & storage
                list_of_columns.extend(["Energy_Production", "Energy_Storage"])
            else:  # presence of only energy consumers & storage
                list_of_columns.extend(["Energy_Consumption", "Energy_Storage"])
    elif number_of_actions == 1:  # presence of either energy consumers or energy production or energy storage
        if max(agent_storage_devices.values()) != 0:  # presence of only energy storage
            list_of_columns.extend(["Energy_Storage"])
        else:
            if np.all(actions_related_to_aggregators < 0):  # presence of only energy production
                list_of_columns.extend(["Energy_Production"])
            else:  # presence of only energy consumers
                list_of_columns.extend(["Energy_Consumption"])
    elif number_of_actions == 0:  # we only manage the energy exchanges between aggregators
        print("Attention, the Multi-Energy Grid in question consists of only energy exchangers aggregators !")
    else:
        raise Exception('The number of actions permitted for each aggregator is not correct !')

    # First we get a dataframe from the actions tensor or vector
    actions_related_to_aggregators = actions_related_to_aggregators.reshape(number_of_aggregators, number_of_actions)
    actions_to_dataframe = pd.DataFrame(
        data=actions_related_to_aggregators,
        index=aggregators,
        columns=list_of_columns
    )
    # We then get a dict from the dataframe
    actions_dict = actions_to_dataframe.to_dict()

    # Inverting the dict - to get the aggregators.names as keys.
    resulting_dict = {
        key: {k: v[key] for k, v in actions_dict.items()}
        for key in actions_dict[next(iter(actions_dict))].keys()
    }  # this is the dict of the actions related to management of device typologies inside the concerned aggregators

    # For energy exchanges
    exchange_dict = {}  # keys -> (('A1', 'A2'), ...) and values -> corresponding decision (energy exchange value)
    for index in range(sum(number_of_energy_exchanges_actions)):
        exchange = agent_grid_topology[index]
        exchange_value = actions_related_to_exchange[index]  # todo à vérifier si c'est le bon sens ou non
        number_of_concerned_aggregators = int((len(exchange) - 1) / 2)  # the format of each exchange is ('A1', 'A2', Emin, Emax, eta)
        concerned_aggregators = exchange[:number_of_concerned_aggregators]  # or ('A1', 'A2', 'A3', Emin, Emax, eta1, eta2)
        exchange_dict[concerned_aggregators] = float(exchange_value)  # or ('A1', 'A2', 'A3', 'A4', Emin, Emax, eta1, eta2, eta3)

    return resulting_dict, exchange_dict


def extract_decision(decision_message: dict, aggregator: "Aggregator") -> list:
    """
    From the decisions taken by the RL agent concerning the whole multi-energy grid, we extract the decision related to the current aggregator.
    """
    consumption = {}
    production = {}
    storage = {}
    # TODO prices, at least for now, the RL agent needs the energy prices as input information, but its actions don't impact the prices
    if aggregator.name in decision_message.keys():
        dummy_dict = {**decision_message[aggregator.name]}
        if "Energy_Consumption" in dummy_dict:
            consumption = decision_message[aggregator.name]["Energy_Consumption"]
            dummy_dict.pop("Energy_Consumption")
        if "Energy_Production" in dummy_dict:
            production = decision_message[aggregator.name]["Energy_Production"]
            dummy_dict.pop("Energy_Production")
        if "Energy_Storage" in dummy_dict:
            storage = decision_message[aggregator.name]["Energy_Storage"]
            dummy_dict.pop("Energy_Storage")

    if isinstance(consumption, dict) and len(consumption) == 0:
        consumption = 0.0

    if isinstance(production, dict) and len(production) == 0:
        production = 0.0

    if isinstance(storage, dict) and len(storage) == 0:
        storage = 0.0

    return [consumption, production, storage]


def retrieve_concerned_energy_exchanges(exchanges_message: dict, aggregator: "Aggregator"):
    """
    This method is used to act the decision taken by the RL agent regarding energy exchanges between aggregators.
    """
    resulting_dict = {}
    for tup in exchanges_message:
        if aggregator.name in tup:  # todo un check à faire pour vérifier qu'on fait le traitement ue seule fois
            resulting_dict = {**resulting_dict, **{tup: exchanges_message[tup]}}

    return resulting_dict


def actions_related_to_energy_exchange(exchange_list: list) -> list:
    """
    This function is used to determine how many decisions to take per each energy exchange in the MEG.
    """
    aggregators_names = []
    numerical_values = []
    number_of_actions_per_exchange = []  # each value corresponds to an energy exchange in the topology vector
    for exchange in exchange_list:  # each tuple in the topology
        for element in exchange:
            if isinstance(element, str):
                aggregators_names.append(element)  # aggregator names
            else:
                numerical_values.append(element)  # Emin, Emax and efficiency
        number_of_actions_per_exchange.append(int((len(numerical_values) - len(aggregators_names) + 1) / 2))

    return number_of_actions_per_exchange


def distribute_min_consumption(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], consumption_flow: float, money_earned_inside: float, energy_sold_inside: float):
    """
    The minimum quantity of energy demanded from consumption devices is served first.
    """
    returned_demands = []
    for demand in sorted_demands[:]:
        message = strategy._create_decision_message()
        message["quantity"] = demand["quantity_min"]
        message["price"] = min(max_price, demand["price"])
        if demand["name"] in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
            quantities_given = strategy._catalog.get(f"{demand["name"]}.{aggregator.nature.name}.energy_accorded")
            quantities_given.append(message)
        else:  # if it is a device
            quantities_given = message

        strategy._catalog.set(f"{demand["name"]}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

        money_earned_inside += message["quantity"] * message["price"]  # money earned by selling energy to the subaggregator
        energy_sold_inside += message["quantity"]  # the absolute value of energy sold inside
        consumption_flow -= message["quantity"]  # the energy quantity remained is determined

        # the energy consumption devices which don't provide any flexibility (Emin = Emax = Enom) are fully served
        if demand["emergency"] == 1:
            sorted_demands.remove(demand)
        else:
            my_message = strategy._catalog.get(f"{demand["name"]}.{aggregator.nature.name}.energy_wanted")
            my_message["energy_nominal"] -= my_message["energy_minimum"]
            my_message["energy_maximum"] -= my_message["energy_minimum"]
            my_message["energy_minimum"] -= my_message["energy_minimum"]
            returned_demands.append(my_message)

    return [sorted_demands, returned_demands, consumption_flow, money_earned_inside, energy_sold_inside]


# def distribute_consumption_decision(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], consumption_flows: List[float], money_earned_inside: float, energy_sold_inside: float):
#     """
#     To distribute the energy allocated to consumption for all the concerned devices.
#     """
#     for index in range(len(sorted_demands)):
#         name = sorted_demands[index]["name"]
#         price = sorted_demands[index]["price"]  # price of energy
#         message = strategy._create_decision_message()
#         message["quantity"] = consumption_flows[index]
#         message["price"] = min(price, max_price)
#         if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
#             quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
#             quantities_given.append(message)
#         else:  # if it is a device
#             quantities_given = message
#
#         strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served
#
#         money_earned_inside += message["quantity"] * message["price"]  # money earned by selling energy to the subaggregator
#         energy_sold_inside += message["quantity"]  # the absolute value of energy sold inside
#
#     return [money_earned_inside, energy_sold_inside]


def distribute_min_production(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], production_flow: float, money_spent_inside: float, energy_bought_inside: float):
    """
    The minimum quantity of energy demanded from production devices is served first.
    """
    returned_offers = []
    for offer in sorted_offers[:]:
        message = strategy._create_decision_message()
        message["quantity"] = offer["quantity_min"]
        message["price"] = max(min_price, offer["price"])
        if offer["name"] in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
            quantities_given = strategy._catalog.get(f"{offer["name"]}.{aggregator.nature.name}.energy_accorded")
            quantities_given.append(message)
        else:  # if it is a device
            quantities_given = message

        strategy._catalog.set(f"{offer["name"]}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

        money_spent_inside -= message["quantity"] * message["price"]  # money earned by selling energy to the subaggregator
        energy_bought_inside -= message["quantity"]  # the absolute value of energy sold inside
        production_flow += message["quantity"]  # the energy quantity remained is determined

        # the energy production devices which don't provide any flexibility (Emin=Emax=Enom) are fully served
        if offer["emergency"] == 1:
            sorted_offers.remove(offer)
        else:
            my_message = strategy._catalog.get(f"{offer["name"]}.{aggregator.nature.name}.energy_wanted")
            my_message["energy_nominal"] -= my_message["energy_minimum"]
            my_message["energy_maximum"] -= my_message["energy_minimum"]
            my_message["energy_minimum"] -= my_message["energy_minimum"]
            returned_offers.append(my_message)

    return [sorted_offers, returned_offers, production_flow, money_spent_inside, energy_bought_inside]


# def distribute_production_decision(strategy: "Strategy", aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], production_flows: List[float], money_spent_inside: float, energy_bought_inside: float):
#     """
#     To distribute the energy allocated to production for all the concerned devices.
#     """
#     for index in range(len(sorted_offers)):
#         name = sorted_offers[index]["name"]
#         price = sorted_offers[index]["price"]  # price of energy
#         message = strategy._create_decision_message()
#         message["quantity"] = production_flows[index]
#         message["price"] = max(price, min_price)
#         if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
#             quantities_given = strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
#             quantities_given.append(message)
#         else:  # if it is a device
#             quantities_given = message
#
#         strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served
#
#         money_spent_inside -= message["quantity"] * message["price"]  # money earned by selling energy to the subaggregator
#         energy_bought_inside -= message["quantity"]  # the absolute value of energy sold inside
#
#     return [money_spent_inside, energy_bought_inside]


def get_full_storage_message(strategy: "Strategy", aggregator: "Aggregator", sorted_storage: List[Dict]):
    """
    This function is used to get the full message of energy storage devices.
    """
    returned_storage = []
    for index in range(len(sorted_storage)):
        name = sorted_storage[index]["name"]
        returned_storage.append(strategy._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted"))
    return returned_storage


# def distribute_storage_decision(strategy: "Strategy", aggregator: "Aggregator", max_price: float, min_price: float, sorted_storage: List[Dict], storage_flows: List[float], money_earned_inside: float, energy_sold_inside: float, money_spent_inside: float, energy_bought_inside: float):
#     """
#     To distribute the energy allocated to storage for all the concerned devices.
#     """
#     for index in range(len(sorted_storage)):
#         name = sorted_storage[index]["name"]
#         price = sorted_storage[index]["price"]  # price of energy
#         message = strategy._create_decision_message()
#         message["quantity"] = storage_flows[index]
#
#         if message["quantity"] < 0:  # if the storage device is discharged
#             message["price"] = max(price, min_price)
#             money_spent_inside -= message["quantity"] * message["price"]  # money earned by selling energy to the subaggregator
#             energy_bought_inside -= message["quantity"]  # the absolute value of energy sold inside
#         else:  # if the storage device is charged
#             message["price"] = min(price, max_price)
#             money_earned_inside += message["quantity"] * message["price"]  # money earned by selling energy to the subaggregator
#             energy_sold_inside += message["quantity"]  # the absolute value of energy sold inside
#
#         quantities_given = message
#
#         strategy._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served
#
#     return [money_earned_inside, energy_sold_inside, money_spent_inside, energy_bought_inside]


# ##########################################################################################
# Utilities useful for Behavior Cloning
# ##########################################################################################
def identify_mirror_decisions(catalog: "Catalog", aggregator: "Aggregator"):
    """
    This function is used to get the action At at state St of the expert strategy.
    """
    internal_mirror_actions = None
    external_mirror_actions = None
    my_device_list = []
    concerned_aggregator = None
    for agg in catalog.aggregators:
        if agg == "mirror_" + aggregator.name:  # the aggregator managed by the expert operator strategy
            internal_mirror_actions = {}
            external_mirror_actions = {}
            concerned_aggregator = catalog.aggregators[agg]
            my_device_list = concerned_aggregator.devices
            break
    for device in my_device_list:
        internal_mirror_actions[device] = catalog.get(f"{device}.{aggregator.nature.name}.energy_accorded")

    if concerned_aggregator:
        if concerned_aggregator.superior:
            external_mirror_actions[concerned_aggregator.superior.name] = catalog.get(f"{agg}.{concerned_aggregator.superior.nature.name}.energy_accorded")
        for subaggregator in concerned_aggregator.subaggregators:
            external_mirror_actions[subaggregator.name] = catalog.get(f"{subaggregator.name}.{concerned_aggregator.nature.name}.energy_accorded")


    return concerned_aggregator, internal_mirror_actions, external_mirror_actions




# ##########################################################################################
# Utilities useful for optimization of sorting coefficients for demands, offers and storage
# ##########################################################################################
def optimized_sorting(raw_demands: List[Dict], raw_offers: List[Dict], raw_storage: List[Dict], sorted_demands: List[Dict], sorted_offers: List[Dict], sorted_storage: List[Dict], RL_cons: float, RL_prod: float, RL_stor: float, buy_p: float, sell_p: float, sorting_coeffs: Dict, compute_order: Callable):
    """
    This function is used to sort the demands/offers/storage devices according to the y-output computed from the sorting coefficients.
    If the energy system category is not concerned by the optimization of its sorting coefficients, the sorted list resulting from self.separate_quantities is returned.
    """
    if "demand" in sorting_coeffs:
        copy_of_demands = deepcopy(raw_demands)
        raw_demands = sorted(raw_demands, key=lambda d: compute_order(d, {"demand": sorting_coeffs["demand"]}, RL_cons, buy_p, sell_p), reverse=True)
        raw_demands = apply_sorting(copy_of_demands, raw_demands, sorted_demands)
    else:
        raw_demands = sorted_demands

    if "offer" in sorting_coeffs:
        copy_of_offers = deepcopy(raw_offers)
        raw_offers = sorted(raw_offers, key=lambda o: compute_order(o, {"offer": sorting_coeffs["offer"]}, RL_prod, buy_p, sell_p), reverse=True)
        raw_offers = apply_sorting(copy_of_offers, raw_offers, sorted_offers)
    else:
        raw_offers = sorted_offers

    if "storage" in sorting_coeffs:
        copy_of_storage = deepcopy(raw_storage)
        raw_storage = sorted(raw_storage, key=lambda s: compute_order(s, {"storage": sorting_coeffs["storage"]}, RL_stor, buy_p, sell_p), reverse=True)
        raw_storage = apply_sorting(copy_of_storage, raw_storage, sorted_storage)
    else:
        raw_storage = sorted_storage

    return [raw_demands, raw_offers, raw_storage]


def compute_output(full_message: Dict, sorting_coefficients: Dict, dispatchable_energy: float, max_price: float, min_price: float):
    """
    This function computes the "y" output based on the sorting coefficients.
    """
    # 1 - The demand and offer horizons are determined (forecast, flexibility)
    my_horizon = find_horizon(full_message)

    # 2 - the input is normalized
    input_vector = normalize_my_input(full_message, dispatchable_energy, max_price, min_price, my_horizon)

    # 3 - the y output of the sorting function is determined
    return calculate_sort_output(input_vector, sorting_coefficients, my_horizon)


def find_horizon(raw_message: Dict) -> int:
    """
    This function is used to find the horizon (forecast) for flexibility of standard devices.
    """
    if not raw_message["type"] == "standard":  # if storage devices
        horizon = 0
    else:  # for energy consumption and production devices
        horizon = len(raw_message["flexibility"])

    return horizon


def normalize_my_input(full_message: Dict, dispatch_RL: float, buying_price: float, selling_price: float, horizon: int) -> Tuple:
    """
    The energy dispatch decision by the DRL at the aggregator level is used to normalize the energy values for each category.
    For prices, the maximum_buying_price and minimum_selling_price are used.
    """
    used_price = (buying_price + selling_price) / 2

    if full_message["type"] == "standard":  # energy demand/generation devices
        temp_dict = []
        for key in full_message:
            if key == "price":
                temp_dict.append(full_message[key] / used_price)
            elif key == "flexibility":
                for step in range(horizon):
                    temp_dict.append(full_message[key][step] / dispatch_RL)
            elif key == "coming_volume":
                temp_dict.append(full_message[key] / (horizon * dispatch_RL))
            elif key == "type":
                temp_dict.append(full_message[key])
            elif key == "CO2":  # todo if added make sure the number of coefficients for prod/conso are increased by 1
                pass
            else:
                temp_dict.append(full_message[key] / dispatch_RL)
        normalized_input = tuple(temp_dict)

    else:  # energy storage
        temp_dict = []
        for key in full_message:
            if key == "type":
                temp_dict.append(full_message[key])
            elif key == "state_of_charge" or key == "self_discharge_rate":
                temp_dict.append(full_message[key])
            elif key == "efficiency":
                temp_dict.append(math.prod(full_message[key].values()))
            elif key == "price":
                temp_dict.append(full_message[key] / used_price)
            elif key == "CO2":  # todo if added make sure the number of coefficients for stor are increased by 1
                pass
            else:
                temp_dict.append(full_message[key] / full_message["capacity"])
        normalized_input = tuple(temp_dict)

    return normalized_input


def calculate_sort_output(normalized_input: Tuple, individual: Dict, horizon: int) -> float:
    """
    In this function, for each demand/offer/storage, an output value is computed (alpha_i * msg_i).
    These values are then sorted in a descending manner.
    The ordering is 'unique' to each individual (alpha_i) of the population.
    The list of order of serving is returned.
    """
    if "standard" not in normalized_input:  # storage devices
        normalized_input = list(normalized_input)
        normalized_input.remove("storage")
        if "storage" in individual:  # if the message corresponds to a storage device offering both charging and discharging
            y_output = np.dot(np.array(list(individual.values())[0]), np.array(normalized_input))
        else:  # if the storage device is either treated as energy production or consumption
            my_individual = list(list(individual.values())[0])
            original_individual = deepcopy(my_individual)
            my_individual[4] = original_individual[4] * original_individual[5]
            my_individual[5] = original_individual[6]
            my_individual[6] = original_individual[4] * original_individual[5]
            my_individual.insert(len(my_individual), original_individual[4] * original_individual[5])
            y_output = np.dot(np.array(my_individual), np.array(normalized_input))

    else:  # energy demand/generation devices
        normalized_input = list(normalized_input)
        normalized_input.remove("standard")
        if horizon == 1:  # alpha_coefficients and normalized_message have the same length
            y_output = np.dot(np.array(list(individual.values())[0]), np.array(normalized_input))
        else:  # normalized_message has bigger length
            my_individual = list(list(individual.values())[0])
            flex_coef = my_individual[4]
            for i in range(1, horizon):
                my_individual.insert(4 + i, flex_coef)
            y_output = np.dot(np.array(my_individual), np.array(normalized_input))

    return y_output


def apply_sorting(dict_1, sorted_dict_1, dict_2):
    """
    This function is used to apply the sorting for the decision message based on the same sorting applied to the information message.
    """
    pos = defaultdict(deque)
    for idx, myData in enumerate(dict_1):
        key = json.dumps(myData, sort_keys=True)  # deterministic string for dict content
        pos[key].append(idx)
    myIndices = []
    for myData in sorted_dict_1:
        key = json.dumps(myData, sort_keys=True)
        if not pos[key]:
            raise ValueError("sorted_list has a dict not present in original a or counts differ")
        myIndices.append(pos[key].popleft())
    sorted_dict_2 = [dict_2[i] for i in myIndices]

    return sorted_dict_2

# for optimizing ratios directly instead of sorting coefficients
def optimized_consumption_ratios(strategy: "Strategy", aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float, optimized_coeffs: Dict):
    i = 0
    # idx = strategy._catalog.get(f"simulation_time")
    # print(f"i am ratios -> {optimized_coeffs}")
    # print(f"i am Econ -> {energy_available_consumption}")
    if len(sorted_demands[0]) >= 1:  # if there are offers
        energy_to_be_shared = deepcopy(energy_available_consumption)
        while i <= len(optimized_coeffs["demand"]) - 1:  # as long as there is energy available
            name = sorted_demands[0][i]["name"]
            energy = min(max(0, energy_to_be_shared * optimized_coeffs["demand"][i]), sorted_demands[0][i]["quantity"])  # the quantity of energy needed todo static (wrt DRL decision)
            # energy = min(max(0, energy_available_consumption), sorted_demands[0][i]["quantity"] * optimized_coeffs["demand"][i])  # the quantity of energy needed todo static (wrt device)
            # energy = min(max(0, energy_available_consumption), sorted_demands[0][i]["quantity"] * optimized_coeffs["demand"][i][idx])  # the quantity of energy needed todo dynamic (wrt device)
            price = sorted_demands[0][i]["price"]  # the price of energy
            price = min(price, max_price)
            # print(f"i am {name} i asked for {sorted_demands[0][i]["quantity"]} and i got {energy} since my coefficient is {optimized_coeffs["demand"][i]}\n")
            Emin = sorted_demands[0][i]["quantity_min"]  # we get back the minimum, which has already been served
            message = strategy._create_decision_message()
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
        # print(f"after serving the true demands this is Econ that remains -> {energy_available_consumption}")
        # this block gives the remaining energy to the storage devices when counted as demand
        if len(sorted_demands[1]) >= 1 and energy_available_consumption > 0.0:
            remaining_total = 0.0
            for element in sorted_demands[1]:  # we sum all the emergency and the energy of demands
                remaining_total += element["quantity"]
                # print(f"storage devices are also consumers and in total are asking of {remaining_total}")

            if remaining_total != 0:
                energy_ratio = min(1, energy_available_consumption / remaining_total)  # the average rate of satisfaction, cannot be superior to 1
                # print(f"the ratio that they will get is {energy_ratio}")
                for demand in sorted_demands[1]:  # then we distribute a bit of energy to all demands
                    name = demand["name"]
                    energy = demand["quantity"]  # the quantity of energy needed
                    price = demand["price"]  # the price of energy
                    price = min(price, max_price)
                    energy *= energy_ratio

                    # print(f"i am storage device {name} i asked for {demand["quantity"]} and i got {energy}\n")

                    Emin = demand["quantity_min"]  # we get back the minimum, which has already been served
                    message = strategy._create_decision_message()
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

    return [energy_available_consumption, money_earned_inside, energy_sold_inside]


def identify_storage_devices(sorted_demands_or_offers: List[Dict]):
    """
    This function is used to separate storage demands/offers of energy from ones asked by specific devices.
    """
    storage_list = []
    real_list = []
    for entry in sorted_demands_or_offers:
        if "Storage" in entry["name"]:
            storage_list.append(entry)
        else:
            real_list.append(entry)

    return real_list, storage_list
