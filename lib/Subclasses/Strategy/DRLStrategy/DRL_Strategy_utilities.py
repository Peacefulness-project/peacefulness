# In this file, some utilities are defined !
# In this file, we define a utility method to extract the information message from all the devices under an aggregator.
# We assume that devices are only visible to the aggregator which is directly managing them.
# As such, a superior aggregator is blind towards the devices managed by its subaggregators.
# We also extract the forecasting predictions of each subaggregator.

import numpy as np
import pandas as pd
import random
from typing import Tuple, Dict, Callable
from copy import deepcopy


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
        intermediate_dict.pop('aggregator')
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
        return sum(my_data) / ((sum(max_value) + sum(min_value)) / 2)


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
                self_discharge_rate.append(storage_dict[device_name][element] * ((energy_min[-1] + energy_max[-1]) / 2))
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
