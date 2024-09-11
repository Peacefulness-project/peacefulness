# In this file, some utilities are defined !
# In this file, we define a utility method to extract the information message from all the devices under an aggregator.
# We assume that devices are only visible to the aggregator which is directly managing them.
# As such, a superior aggregator is blind towards the devices managed by its subaggregators.
# We also extract the forecasting predictions of each subaggregator.


import numpy as np
import pandas as pd
import random
from typing import Tuple, Dict, Callable


# ##########################################################################################
# Ascending interface/bottom_up_phase utilities
# ##########################################################################################
def determine_energy_prices(catalog: "Catalog", aggregator: "Aggregator", min_price: float, max_price: float):
    """
    This method is used to compute and return both the prices for energy selling and buying.
    """
    # First, we retrieve the energy prices proposed by the devices managed by the aggregator
    managed_devices_buying_prices = []
    managed_devices_buying_energies = []
    managed_devices_selling_prices = []
    managed_devices_selling_energies = []
    for device_name in aggregator.devices:
        price = catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["price"]
        Emax = catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
        if Emax < 0:  # if the device wants to sell energy
            # price = max(price, min_price)  # the minimum accepted energy price (€/kWh) for producers
            managed_devices_selling_prices.append(price)
            managed_devices_selling_energies.append(Emax)
        elif Emax > 0:  # if the device wants to buy energy
            # price = min(price, max_price)  # the maximum accepted energy price (€/kWh) for consumers
            managed_devices_buying_prices.append(price)
            managed_devices_buying_energies.append(Emax)
    # these prices are weighted by the energy proportion
    for index in range(len(managed_devices_selling_prices)):
        managed_devices_selling_prices[index] = max(min_price, managed_devices_selling_energies[index] * managed_devices_selling_prices[index] / sum(managed_devices_selling_energies))
    for index in range(len(managed_devices_buying_energies)):
        managed_devices_buying_prices[index] = min(max_price, managed_devices_buying_energies[index] * managed_devices_buying_prices[index] / sum(managed_devices_buying_energies))

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
        price = wanted_energy["price"]
        Emax = wanted_energy["energy_maximum"]
        if Emax < 0:  # if the subaggregator wants to sell energy
            # price = max(price, min_price)  # the minimum accepted energy price (€/kWh) for producers
            subaggregators_selling_prices.append(price)
            subaggregators_selling_energies.append(Emax)
        elif Emax > 0:  # if the subaggregator wants to buy energy
            # price = min(price, max_price)  # the maximum accepted energy price (€/kWh) for consumers
            subaggregators_buying_prices.append(price)
            subaggregators_buying_energies.append(Emax)
    # these prices are weighted by the energy proportion
    for index in range(len(subaggregators_selling_prices)):
        subaggregators_selling_prices[index] = max(min_price, subaggregators_selling_energies[index] * subaggregators_selling_prices[index] / sum(subaggregators_selling_energies))
    for index in range(len(subaggregators_buying_energies)):
        subaggregators_buying_prices[index] = min(max_price, subaggregators_buying_energies[index] * subaggregators_buying_prices[index] / sum(subaggregators_buying_energies))

    buying_prices = [*managed_devices_buying_prices, *subaggregators_buying_prices]
    selling_prices = [*managed_devices_selling_prices, *subaggregators_selling_prices]
    if buying_prices:
        buying_price = min(buying_prices)
    else:
        buying_price = 0.0
    if selling_prices:
        selling_price = max(selling_prices)
    else:
        selling_price = 0.0

    return buying_price, selling_price


def my_devices(catalog: "Catalog", aggregator: "Aggregator") -> Tuple[Dict, Dict]:
    """
    This function is used to create the formalism message for each aggregator.
    Recursion is not needed. (needs confirmation from Timothé)
    """
    formalism_message = {aggregator.name: {"Energy_Consumption": {}, "Energy_Production": {}, "Energy_Storage": {}}}
    converter_message = {aggregator.name: {"Energy_Conversion": {}}}
    devices_list = []

    # Retrieving the list of devices managed by the aggregator
    for device_name in aggregator.devices:
        devices_list.append(catalog.devices[device_name])

    # Getting the specific message from the devices
    for device in devices_list:
        Emax = catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
        Emin = catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
        specific_message = {**device.messages_manager.get_information_message}
        if specific_message["type"] == "standard":  # if the device/energy system is either for consumption/production
            if Emax < 0:  # the energy system/device produces energy
                intermediate_dict = {**specific_message}
                # print(intermediate_dict)
                intermediate_dict.pop("type")
                # print(intermediate_dict)
                formalism_message[aggregator.name]["Energy_Production"] = {**formalism_message[aggregator.name]["Energy_Production"], **{device.name: {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}}}
                # print(formalism_message)
                specific_message.clear()
            elif Emax > 0:  # the energy system/device consumes energy
                intermediate_dict = {**specific_message}
                # print(intermediate_dict)
                intermediate_dict.pop("type")
                # print(intermediate_dict)
                formalism_message[aggregator.name]["Energy_Consumption"] = {**formalism_message[aggregator.name]["Energy_Consumption"], **{device.name: {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}}}
                # print(formalism_message)
                specific_message.clear()
        elif specific_message["type"] == "storage":  # if the device/energy system is for storage
            intermediate_dict = {**specific_message}
            # print(intermediate_dict)
            intermediate_dict.pop("type")
            # print(intermediate_dict)
            formalism_message[aggregator.name]["Energy_Storage"] = {**formalism_message[aggregator.name]["Energy_Storage"], **{device.name: {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}}}
            # print(formalism_message)
            specific_message.clear()
        elif specific_message["type"] == "converter":  # if the device/energy system is for conversion
            intermediate_dict = {**specific_message}
            # print(intermediate_dict)
            intermediate_dict.pop("type")
            # print(intermediate_dict)
            converter_message[aggregator.name]["Energy_Conversion"] = {**converter_message[aggregator.name]["Energy_Conversion"], **{device.name: {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}}}
            # print(converter_message)
            specific_message.clear()

    return formalism_message, converter_message


def if_it_exists(my_data, my_func: Callable):
    if my_data:
        return my_func(my_data)
    else:
        return 0.0


def my_basic_mean(my_data):
    if len(my_data) != 0:
        return sum(my_data) / len(my_data)


def mutualize_formalism_message(formalism_dict: dict) -> dict:
    """
    This function regroups the formalism dict around the typology of energy systems.
    """
    # Preparing the dict
    return_dict = {}
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

    for element in [consumption_dict, production_dict]:
        for key in element:
            for subkey in element[key]:
                if subkey == 'energy_minimum':
                    energy_min.append(element[key][subkey])
                elif subkey == 'energy_maximum':
                    energy_max.append(element[key][subkey])
                elif subkey == 'flexibility':
                    flexibility.extend(element[key][subkey])
                elif subkey == 'interruptibility':
                    interruptibility.append(element[key][subkey])
                else:
                    coming_volume.append(element[key][subkey])
        if element == consumption_dict:
            return_dict = {**return_dict, **{
                "Energy_Consumption": {'energy_minimum': if_it_exists(energy_min, sum), 'energy_maximum': if_it_exists(energy_max, sum),
                                       'flexibility': if_it_exists(flexibility, min), 'interruptibility': if_it_exists(interruptibility, min),
                                       'coming_volume': if_it_exists(coming_volume, sum)}}
                           }
            energy_min.clear()
            energy_max.clear()
            flexibility.clear()
            interruptibility.clear()
            coming_volume.clear()
        else:
            return_dict = {**return_dict, **{
                "Energy_Production": {'energy_minimum': if_it_exists(energy_min, sum), 'energy_maximum': if_it_exists(energy_max, sum),
                                      'flexibility': if_it_exists(flexibility, min), 'interruptibility': if_it_exists(interruptibility, min),
                                      'coming_volume': if_it_exists(coming_volume, sum)}}
                           }
    # Energy storage associated dict of values
    energy_min = []
    energy_max = []
    state_of_charge = []
    capacity = []
    self_discharge_rate = []
    efficiency = []

    for key in storage_dict:
        for subkey in storage_dict[key]:
            if subkey == 'energy_minimum':
                energy_min.append(storage_dict[key][subkey])
            elif subkey == 'energy_maximum':
                energy_max.append(storage_dict[key][subkey])
            elif subkey == 'state_of_charge':
                state_of_charge.append(storage_dict[key][subkey])
            elif subkey == 'capacity':
                capacity.append(storage_dict[key][subkey])
            elif subkey == 'self_discharge_rate':
                self_discharge_rate.append(storage_dict[key][subkey])
            else:
                efficiency.append(storage_dict[key][subkey])

    return_dict = {**return_dict, **{
        "Energy_Storage": {'energy_minimum': if_it_exists(energy_min, sum), 'energy_maximum': if_it_exists(energy_max, sum),
                           'state_of_charge': if_it_exists(state_of_charge, my_basic_mean),
                           'capacity': if_it_exists(capacity, my_basic_mean),
                           'self_discharge_rate': if_it_exists(self_discharge_rate, my_basic_mean),
                           'efficiency': if_it_exists(efficiency, my_basic_mean)}}
                   }

    return return_dict


# ##########################################################################################
# Descending interface/top_down_phase utilities
# ##########################################################################################
def from_tensor_to_dict(actions: np.ndarray, aggregators: list, agent: "Agent") -> Tuple[dict, dict]:
    """
    This method is used to translate the actions taken by the A-C method into results understood by Peacefulness.
    The decision is to be stored.
    The return dict is under the format: {'Aggregator_1': {'Energy_Consumption': , 'Energy_Production': ...}, ...}
    The dict concerning energy exchanges is also returned.
    """
    list_of_columns = []

    # Getting relevant info from the peacefulness_grid class considered for the RL agent
    agent_grid_topology = agent.grid.get_topology  # the return of the get_topology method
    agent_storage_devices = agent.grid.get_storage  # the return of the get_storage method

    # Grouping actions into ones related to energy exchanges and ones related to management of energy consumption, production and storage inside the aggregators
    actions_related_to_aggregators = actions[:-len(agent_grid_topology)]
    actions_related_to_exchange = actions[-len(agent_grid_topology):]

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
    for index in range(len(agent_grid_topology)):
        exchange = agent_grid_topology[index]
        exchange_value = actions_related_to_exchange[index]
        number_of_concerned_aggregators = int((len(exchange) - 1) / 2)  # the format of each exchange is ('A1', 'A2', Emin, Emax, eta)
        concerned_aggregators = exchange[:number_of_concerned_aggregators]  # or ('A1', 'A2', 'A3', Emin, Emax, eta1, eta2)
        exchange_dict[concerned_aggregators] = exchange_value  # or ('A1', 'A2', 'A3', 'A4', Emin, Emax, eta1, eta2, eta3)

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

    return [consumption, production, storage]


def retrieve_concerned_energy_exchanges(exchanges_message: dict, aggregator: "Aggregator"):
    """
    This method is used to act the decision taken by the RL agent regarding energy exchanges between aggregators.
    """
    resulting_dict = {}
    for tup in exchanges_message:
        if aggregator.name in tup:
            resulting_dict = {**resulting_dict, **{tup: exchanges_message[tup]}}

    return resulting_dict


def distribute_to_standard_devices(device_list: list, energy_accorded: float, energy_price: float, catalog: "Catalog", aggregator: "Aggregator", message: dict) -> Tuple[float, float]:
    """
    This function is used for energy distribution and billing for standard devices managed by the aggregator.
    It concerns the energy producers and consumers.
    The minimum energy demands/offers are served first, the rest is then distributed equally over non-urgent devices.
    """
    # initializing
    energy_inside = 0.0
    money_inside = 0.0
    if f"{aggregator.name}.DRL_Strategy.failed_to_deliver" not in catalog.keys:
        failed_to_satisfy = 0.0
    else:
        failed_to_satisfy = catalog.get(f"{aggregator.name}.DRL_Strategy.failed_to_deliver")
    distribution_decision = {}
    non_urgent_devices = []

    if len(device_list) == 0:
        failed_to_satisfy += abs(energy_accorded)

    for device in device_list:
        Emin = catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
        Emax = catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
        # the minimum energy demand/offer is served first
        if abs(energy_accorded) > abs(Emin):  # to take into account both negative and positive signs
            distribution_decision[device.name] = Emin
            energy_accorded -= Emin
        elif 0 < abs(energy_accorded) < abs(Emin) and return_sign(energy_accorded, Emin):  # to take into account both negative and positive signs
            distribution_decision[device.name] = energy_accorded
            failed_to_satisfy += abs(abs(Emin) - abs(energy_accorded))
            energy_accorded = 0.0
        else:
            distribution_decision[device.name] = 0.0
            failed_to_satisfy += abs(Emin)

        # the urgency of the demand/offer is determined
        if Emin == Emax:  # the energy demand/offer is urgent
            message['quantity'] = distribution_decision[device.name]
            message["price"] = energy_price
            catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
            energy_inside += abs(message['quantity'])
            money_inside += abs(message['quantity'] * energy_price)
        else:  # the energy demand/offer is not a priority
            non_urgent_devices.append(device)

    for device in non_urgent_devices:  # the remaining energy is equally distributed over the rest of the devices
        message['quantity'] = distribution_decision[device.name] + energy_accorded / len(non_urgent_devices)
        message["price"] = energy_price
        catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
        energy_inside += abs(message['quantity'])
        money_inside += abs(message['quantity'] * energy_price)

    if f"{aggregator.name}.DRL_Strategy.failed_to_deliver" not in catalog.keys:
        catalog.add(f"{aggregator.name}.DRL_Strategy.failed_to_deliver", failed_to_satisfy)
    else:
        catalog.set(f"{aggregator.name}.DRL_Strategy.failed_to_deliver", failed_to_satisfy)

    return energy_inside, money_inside


def return_sign(a: float, b: float):
    """
    This utility function is used to check if two numbers are either both positive/negative or not.
    """
    result = (a >= 0) == (b >= 0)
    return result


def distribute_to_storage_devices(storage_list: list, energy_accorded_to_storage: float, buying_price: float, selling_price: float, catalog: "Catalog", aggregator: "Aggregator", message: dict) -> Tuple[float, float, float, float]:
    """
    This function is used for energy distribution and billing for energy storage systems managed by the aggregator.
    The devices who have needs that encounter the average needs are to stay idle.
    The minimum energy demands/offers are served first, the rest is then distributed equally over non-urgent devices.
    """
    # initializing
    if f"{aggregator.name}.DRL_Strategy.failed_to_deliver" not in catalog.keys:
        failed_to_satisfy = 0.0
    else:
        failed_to_satisfy = catalog.get(f"{aggregator.name}.DRL_Strategy.failed_to_deliver")
    distribution_decision = {}
    non_urgent_storage = []
    energy_bought_inside = 0.0
    money_spent_inside = 0.0
    energy_sold_inside = 0.0
    money_earned_inside = 0.0

    if len(storage_list) == 0:
        failed_to_satisfy += abs(energy_accorded_to_storage)

    for storage in storage_list:
        Emax = catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
        Emin = catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
        sign_min = return_sign(Emin, energy_accorded_to_storage)
        if not sign_min:  # the device wants the opposite of the average want of the energy storage systems managed by the aggregator, thus it will be idle
            message["quantity"] = 0
            message["price"] = 0
            catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
        else:  # the device wants the same as the average want of the energy storage systems managed by the aggregator
            if abs(energy_accorded_to_storage) > abs(Emin):  # to take into account both negative and positive signs
                distribution_decision[storage.name] = Emin
                energy_accorded_to_storage -= Emin
            elif 0 < abs(energy_accorded_to_storage) < abs(Emin):  # to take into account both negative and positive signs
                distribution_decision[storage.name] = energy_accorded_to_storage
                failed_to_satisfy += abs(abs(Emin) - abs(energy_accorded_to_storage))
                energy_accorded_to_storage = 0
            else:
                distribution_decision[storage.name] = 0.0
                failed_to_satisfy += abs(Emin)
            # the urgency is determined
            if Emin == Emax:  # the energy storage system has urgency
                message["quantity"] = distribution_decision[storage.name]
                if Emin < 0:  # the energy storage system wants to sell its energy
                    message["price"] = selling_price
                    energy_bought_inside += abs(message["quantity"])
                    money_spent_inside += abs(message['quantity'] * message["price"])
                else:  # the energy storage system wants to buy energy
                    message["price"] = buying_price
                    energy_sold_inside += abs(message["quantity"])
                    money_earned_inside += abs(message['quantity'] * message["price"])
                catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
            else:
                sign_max = return_sign(Emax, energy_accorded_to_storage)
                if not sign_max:
                    message["quantity"] = distribution_decision[storage.name]
                    if Emin < 0:  # the energy storage system wants to sell its energy
                        message["price"] = selling_price
                        energy_bought_inside += abs(message["quantity"])
                        money_spent_inside += abs(message['quantity'] * message["price"])
                    else:  # the energy storage system wants to buy energy
                        message["price"] = buying_price
                        energy_sold_inside += abs(message["quantity"])
                        money_earned_inside += abs(message['quantity'] * message["price"])
                    catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
                else:
                    non_urgent_storage.append(storage)

    for storage in non_urgent_storage:  # the remaining energy is equally distributed over the rest of the devices
        Emin = catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
        message["quantity"] = distribution_decision[storage.name] + energy_accorded_to_storage / len(non_urgent_storage)
        if Emin < 0:  # the energy storage system wants to sell its energy
            message["price"] = selling_price
            energy_bought_inside += abs(message["quantity"])
            money_spent_inside += abs(message['quantity'] * message["price"])
        else:  # the energy storage system wants to buy energy
            message["price"] = buying_price
            energy_sold_inside += abs(message["quantity"])
            money_earned_inside += abs(message['quantity'] * message["price"])
        catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)

    if f"{aggregator.name}.DRL_Strategy.failed_to_deliver" not in catalog.keys:
        catalog.add(f"{aggregator.name}.DRL_Strategy.failed_to_deliver", failed_to_satisfy)
    else:
        catalog.set(f"{aggregator.name}.DRL_Strategy.failed_to_deliver", failed_to_satisfy)

    return energy_bought_inside, money_spent_inside, energy_sold_inside, money_earned_inside


# def distribute_energy_exchanges(catalog: "Catalog", aggregator: "Aggregator", energy_accorded_to_exchange: dict, grid_topology: list, converter_list: dict, buying_price: float, selling_price: float, message: dict) -> Tuple[float, float, float, float, float, float, float, float]:
#     """
#     This function computes the energy exchanges (direct ones and with conversion systems).
#     Since we don't know how do decisions correspond to energy exchanges, we first verify if they are bound by the min and max.
#     Then we look for the one closest to the nominal.
#     May be subject to change if finally we output the matrix of the grid's topology as in the input to the model.
#     """
#     # initializing
#     energy_bought_inside = 0.0
#     money_spent_inside = 0.0
#     energy_sold_inside = 0.0
#     money_earned_inside = 0.0
#     energy_bought_outside = 0.0
#     money_spent_outside = 0.0
#     energy_sold_outside = 0.0
#     money_earned_outside = 0.0
#
#     aggregator_energy_exchanges_from_grid_topology = []
#     for tup in grid_topology:
#         if aggregator.name in tup:
#             aggregator_energy_exchanges_from_grid_topology.append(tup)
#
#     aggregator_energy_exchanges_from_RL_decision = []
#     dummy_dict = {**energy_accorded_to_exchange}
#     for key, value in energy_accorded_to_exchange.items():
#         if value != 0:
#             aggregator_energy_exchanges_from_RL_decision.append(value)
#             dummy_dict.pop(key)
#     if len(dummy_dict) == len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision):
#         for key, value in dummy_dict.items():
#             aggregator_energy_exchanges_from_RL_decision.append(value)
#     else:
#         for i in range(len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision)):
#             aggregator_energy_exchanges_from_RL_decision.append(0)
#
#     if len(aggregator_energy_exchanges_from_grid_topology) != len(aggregator_energy_exchanges_from_RL_decision):
#         raise Exception(f"The {aggregator.name}'s occurrences in energy exchanges don't match the corresponding number of decisions taken by the RL !")
#
#     # Quantities concerning energy conversion systems
#     decision_message = {}
#     for device in converter_list:
#         decision_message[device] = []
#         for element in aggregator_energy_exchanges_from_RL_decision[:]:
#             if converter_list[device]["energy_minimum"] <= element <= converter_list[device]["energy_maximum"]:
#                 decision_message[device].append(element)
#         if len(decision_message[device]) > 1:
#             distance = {}
#             for element in decision_message[device]:
#                 distance[element] = abs(element - converter_list[device]["energy_nominal"])
#             decision_message[device] = min(distance, key=distance.get)
#             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#         elif len(decision_message[device]) == 0 and len(aggregator_energy_exchanges_from_RL_decision) == 1:  # safeguard
#             decision_message[device] = aggregator_energy_exchanges_from_RL_decision[0]
#             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#         elif len(decision_message[device]) == 0 and len(aggregator_energy_exchanges_from_RL_decision) != 1:  # safeguard, random choice if more are present, since no element verifies the condition
#             decision_message[device] = random.choice(aggregator_energy_exchanges_from_RL_decision)
#             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#         else:  # if there is only one element
#             decision_message[device] = decision_message[device][0]
#             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#
#         message["quantity"] = decision_message[device]
#         if decision_message[device] < 0:  # energy selling
#             message["price"] = selling_price
#             energy_sold_outside += abs(message["quantity"])
#             money_earned_outside += abs(message['quantity'] * message["price"])
#         else:  # energy buying
#             message["price"] = buying_price
#             energy_bought_outside += abs(message["quantity"])
#             money_spent_outside += abs(message['quantity'] * message["price"])
#         catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
#
#     # Quantities concerning sub-aggregators
#     if aggregator_energy_exchanges_from_RL_decision:
#         for subaggregator in aggregator.subaggregators:
#             decision_message[subaggregator.name] = []
#             quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
#             # print(f"top-down phase, quantities_and_prices: {quantities_and_prices}")
#             for element in aggregator_energy_exchanges_from_RL_decision[:]:
#                 # print(element)
#                 if quantities_and_prices[0]["energy_minimum"] <= element <= quantities_and_prices[0]["energy_maximum"]:
#                     decision_message[subaggregator.name].append(element)
#             if len(decision_message[subaggregator.name]) > 1:
#                 distance = {}
#                 for element in decision_message[subaggregator.name]:
#                     distance[element] = abs(element - quantities_and_prices["energy_nominal"])
#                 decision_message[subaggregator.name] = min(distance, key=distance.get)
#                 aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
#             elif len(decision_message[subaggregator.name]) == 0 and len(aggregator_energy_exchanges_from_RL_decision) == 1:  # safeguard, we take the only present element regardless
#                 decision_message[subaggregator.name] = aggregator_energy_exchanges_from_RL_decision[0]
#                 aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
#             elif len(decision_message[subaggregator.name]) == 0 and len(aggregator_energy_exchanges_from_RL_decision) != 1:  # safeguard, random choice if more are present, since no element verifies the condition
#                 decision_message[subaggregator.name] = random.choice(aggregator_energy_exchanges_from_RL_decision)
#                 aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
    #         else:  # if there is only one element
    #             # print(decision_message[subaggregator.name])
    #             decision_message[subaggregator.name] = decision_message[subaggregator.name][0]
    #             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
    #
    #         message["quantity"] = decision_message[subaggregator.name]
    #         if decision_message[subaggregator.name] < 0:  # energy selling
    #             message["price"] = selling_price
    #             energy_bought_inside += abs(message["quantity"])
    #             money_spent_inside += abs(message['quantity'] * message["price"])
    #         else:  # energy buying
    #             message["price"] = buying_price
    #             energy_sold_inside += abs(message["quantity"])
    #             money_earned_inside += abs(message['quantity'] * message["price"])
    #         catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)
    # else:
    #     print("The aggregator does not exchange with its subaggregators nor with its superior aggregator !")
    #
    # return energy_bought_inside, money_spent_inside, energy_sold_inside, money_earned_inside, energy_bought_outside, money_spent_outside, energy_sold_outside, money_earned_outside


def distribute_energy_exchanges(catalog: "Catalog", aggregator: "Aggregator", energy_accorded_to_exchange: dict, grid_topology: list, converter_list: dict, buying_price: float, selling_price: float, message: dict, scope: list):
    """
    This function computes the energy exchanges (direct ones and with conversion systems).
    May be subject to change.
    """
    # Initializing
    if f"{aggregator.name}.DRL_Strategy.failed_to_deliver" not in catalog.keys:
        failed_to_satisfy = 0.0
    else:
        failed_to_satisfy = catalog.get(f"{aggregator.name}.DRL_Strategy.failed_to_deliver")
    energy_bought_inside = 0.0
    money_spent_inside = 0.0
    energy_sold_inside = 0.0
    money_earned_inside = 0.0
    energy_bought_outside = 0.0
    money_spent_outside = 0.0
    energy_sold_outside = 0.0
    money_earned_outside = 0.0

    # Solving hierarchical energy exchanges; those concerning superior aggregator and subaggregators, be it direct or through a device connecting just both of them
    # todo il y a aussi l'aspect du signe de l'echange + et - pour quel agregateur ?
    decision_message = {}
    fixed_prices_by_superior = {}
    energy_exchanges_left = {**energy_accorded_to_exchange}
    for exchange in grid_topology:
        if aggregator.name in exchange:
            # First, we check for superior aggregators, since they distribute first
            if aggregator.superior:
                if aggregator.superior.name in exchange:
                    if aggregator.superior in scope:  # if the superior aggregator is also managed by the DRL strategy
                        if exchange[:2] in energy_accorded_to_exchange:
                            decision_message[aggregator.name] = energy_accorded_to_exchange[exchange[:2]]
                            if decision_message[aggregator.name] < 0:  # selling of energy
                                energy_sold_outside -= decision_message[aggregator.name]
                                money_earned_outside -= decision_message[aggregator.name] * selling_price
                            else:  # buying of energy
                                energy_bought_outside += decision_message[aggregator.name]
                                money_spent_outside += decision_message[aggregator.name] * buying_price
                            energy_exchanges_left.pop(exchange[:2])
                    elif aggregator.superior.strategy.name == "grid_strategy":  # if the superior is managed by the grid strategy
                        if exchange[:2] in energy_accorded_to_exchange:
                            decision_message[aggregator.name] = energy_accorded_to_exchange[exchange[:2]]
                            message["quantity"] = decision_message[aggregator.name]
                            if decision_message[aggregator.name] < 0:  # selling of energy
                                message["price"] = selling_price
                                energy_sold_outside -= decision_message[aggregator.name]
                                money_earned_outside -= decision_message[aggregator.name] * message["price"]
                            else:  # buying of energy
                                message["price"] = buying_price
                                energy_bought_outside += decision_message[aggregator.name]
                                money_spent_outside += decision_message[aggregator.name] * message["price"]
                            energy_exchanges_left.pop(exchange[:2])
                            catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded", message)
                    else:  # if the superior aggregator is managed by another strategy
                        quantities_and_prices = catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded")
                        if not isinstance(quantities_and_prices, list):  # todo check with Timothé why it is a list in the first place
                            decision_message[aggregator.name] = quantities_and_prices["quantity"]
                            fixed_prices_by_superior[aggregator.name] = quantities_and_prices["price"]
                        else:
                            decision_message[aggregator.name] = quantities_and_prices[0]["quantity"]
                            fixed_prices_by_superior[aggregator.name] = quantities_and_prices[0]["price"]
                        if decision_message[aggregator.name] < 0:  # selling of energy
                            energy_sold_outside -= decision_message[aggregator.name]
                            money_earned_outside -= decision_message[aggregator.name] * fixed_prices_by_superior[aggregator.name]
                        else:  # buying of energy
                            energy_bought_outside += decision_message[aggregator.name]
                            money_spent_outside += decision_message[aggregator.name] * fixed_prices_by_superior[aggregator.name]
                        if exchange[:2] in energy_accorded_to_exchange:
                            failed_to_satisfy += abs(abs(energy_accorded_to_exchange[exchange[:2]]) - abs(decision_message[aggregator.name]))  # Penalty
                            energy_exchanges_left.pop(exchange[:2])

            # Then, we check for subaggregators after that
            else:
                for subaggregator in aggregator.subaggregators:
                    if subaggregator.name in exchange:
                        if exchange[:2] in energy_accorded_to_exchange:
                            decision_message[subaggregator.name] = energy_accorded_to_exchange[exchange[:2]]
                            message["quantity"] = decision_message[subaggregator.name]
                            if decision_message[subaggregator.name] < 0:  # selling of energy
                                message["price"] = selling_price
                                energy_bought_inside -= decision_message[subaggregator.name]
                                money_spent_inside -= decision_message[subaggregator.name] * message["price"]
                            else:  # buying of energy
                                message["price"] = buying_price
                                energy_sold_inside += decision_message[subaggregator.name]
                                money_earned_inside += decision_message[subaggregator.name] * message["price"]
                            energy_exchanges_left.pop(exchange[:2])
                            if not subaggregator in scope:
                                quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
                                if not isinstance(quantities_and_prices, list):  # todo check with Timothé why it is a list in the first place
                                    wanted_energy = quantities_and_prices["energy_maximum"]
                                    failed_to_satisfy += abs(abs(message["quantity"]) - abs(wanted_energy))  # Penalty
                                else:
                                    wanted_energy = quantities_and_prices[0]["energy_maximum"]
                                    failed_to_satisfy += abs(abs(message["quantity"]) - abs(wanted_energy))  # Penalty
                            catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)

    # The rest of energy exchanges
    copy_of_left_exchanges = {**energy_exchanges_left}
    for device in converter_list:
        for exchange in copy_of_left_exchanges:
            my_flag = False
            for my_aggregator in converter_list[device]:
                if my_aggregator.name in exchange:
                    my_flag = True
                else:
                    my_flag = False
                    break
            if my_flag:
                decision_message[device.name] = energy_exchanges_left[exchange]
                if decision_message[device.name] < 0:  # the aggregator sells energy through this energy conversion system
                    message["price"] = selling_price
                    energy_sold_outside -= decision_message[device.name]
                    money_earned_outside -= decision_message[device.name] * message["price"]
                else:  # the aggregator buys energy through this energy conversion system
                    message["price"] = buying_price
                    energy_bought_outside += decision_message[device.name]
                    money_spent_outside += decision_message[device.name] * message["price"]
                message["quantity"] = decision_message[device.name]
                catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
                energy_exchanges_left.pop(exchange)
                break

    return energy_bought_inside, money_spent_inside, energy_sold_inside, money_earned_inside, energy_bought_outside, money_spent_outside, energy_sold_outside, money_earned_outside

