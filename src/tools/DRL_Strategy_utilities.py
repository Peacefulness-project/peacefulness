# In this file, some utilities are defined !
# In this file, we define a utility method to extract the information message from all the devices under an aggregator.
# We assume that devices are only visible to the aggregator which is directly managing them.
# As such, a superior aggregator is blind towards the devices managed by its subaggregators.
# We also extract the forecasting predictions of each subaggregator.

import numpy as np
import pandas as pd
from collections import Counter


# ##########################################################################################
# Ascending interface/bottom_up_phase utilities
# ##########################################################################################
def determine_energy_prices(strategy: "Strategy", aggregator: "Aggregator", min_price: float, max_price: float):
    """
    This method is used to compute and return both the prices for energy selling and buying.
    """
    buying_prices = []
    selling_prices = []

    # First, we retrieve the energy prices proposed by the devices managed by the aggregator
    for device_name in aggregator.devices:
        price = strategy._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["price"]
        Emax = strategy._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
        if Emax < 0:  # if the device wants to sell energy
            price = max(price, min_price)  # the minimum accepted energy price (€/kWh) for producers
            selling_prices.append(price)
        elif Emax > 0:  # if the device wants to buy energy
            price = min(price, max_price)  # the maximum accepted energy price (€/kWh) for consumers
            buying_prices.append(price)

    # Then, we retrieve the energy prices proposes by the sub-aggregators managed by the aggregator
    for subaggregator in aggregator.subaggregators:
        wanted_energy = strategy._catalog.get(f"{subaggregator.name}{aggregator.nature.name}.energy_wanted")
        for element in wanted_energy:
            price = element["price"]
            Emax = element["energy_maximum"]
            if Emax < 0:  # if the device wants to sell energy
                price = max(price, min_price)  # the minimum accepted energy price (€/kWh) for producers
                selling_prices.append(price)
            elif Emax > 0:  # if the device wants to buy energy
                price = min(price, max_price)  # the maximum accepted energy price (€/kWh) for consumers
                buying_prices.append(price)

    buying_price = min(buying_prices)
    selling_price = max(selling_prices)

    return buying_price, selling_price


def my_devices(world: "World", aggregator: "Aggregator") -> dict:
    """
    This function is used to create the formalism message for each aggregator.
    Recursion is not needed. (needs confirmation from Timothé)
    """
    formalism_message = {}
    devices_list = []

    # Retrieving the list of devices managed by the aggregator
    for device_name in aggregator.devices:
        devices_list.append(world.catalog.devices[device_name])

    # Getting the specific message from the devices
    for device in devices_list:
        Emax = world._catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
        Emin = world._catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
        specific_message = device.messages_manager.get_information_message()
        if specific_message["type"] == "standard":  # if the device/energy system is either for consumption/production
            if Emax < 0:  # the energy system/device produces energy
                intermediate_dict = specific_message
                intermediate_dict.pop("type")
                formalism_message[aggregator.name]["Energy_Production"][device.name] = {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}
            else:  # the energy system/device consumes energy
                intermediate_dict = specific_message
                intermediate_dict.pop("type")
                formalism_message[aggregator.name]["Energy_Consumption"][device.name] = {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}
        elif specific_message["type"] == "storage":  # if the device/energy system is for storage
            intermediate_dict = specific_message
            intermediate_dict.pop("type")
            formalism_message[aggregator.name]["Energy_Storage"][device.name] = {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}
        elif specific_message["type"] == "converter":  # if the device/energy system is for conversion
            intermediate_dict = specific_message
            intermediate_dict.pop("type")
            formalism_message[aggregator.name]["Energy_Conversion"][device.name] = {**{"energy_minimum": Emin, "energy_maximum": Emax}, **intermediate_dict}

    return formalism_message


def mutualize_formalism_message(formalism_dict: dict) -> dict:
    """
    This function regroups the formalism dict around the typology of energy systems.
    """
    # Preparing the dict
    return_dict = {}
    consumption_dict = {}
    production_dict = {}
    storage_dict = {}
    conversion_dict = {}
    for aggregator_name in formalism_dict.keys():
        inter_dict = {**formalism_dict[aggregator_name]}
        for key in inter_dict.keys():
            consumption_dict = {**consumption_dict, **inter_dict["Energy_Consumption"]}
            production_dict = {**production_dict, **inter_dict["Energy_Production"]}
            storage_dict = {**storage_dict, **inter_dict["Energy_Storage"]}
            conversion_dict = {**conversion_dict, **inter_dict["Energy_Conversion"]}

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
            return_dict = {
                "Energy_Consumption": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
                                       'flexibility': min(flexibility), 'interruptibility': min(interruptibility),
                                       'coming_volume': sum(coming_volume)}}
            energy_min.clear()
            energy_max.clear()
            flexibility.clear()
            interruptibility.clear()
            coming_volume.clear()
        else:
            return_dict = {**return_dict, **{
                "Energy_Production": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
                                      'flexibility': min(flexibility), 'interruptibility': min(interruptibility),
                                      'coming_volume': sum(coming_volume)}}
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
        "Energy_Storage": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
                           'state_of_charge': sum(state_of_charge) / len(state_of_charge),
                           'capacity': sum(capacity) / len(capacity),
                           'self_discharge_rate': sum(self_discharge_rate) / len(self_discharge_rate),
                           'efficiency': sum(efficiency) / len(efficiency)}}
                   }
    # Energy conversion associated dict of values
    energy_min = []
    energy_max = []
    efficiency = []

    for key in conversion_dict:
        for subkey in conversion_dict[key]:
            if subkey == 'energy_minimum':
                energy_min.append(conversion_dict[key][subkey])
            elif subkey == 'energy_maximum':
                energy_max.append(conversion_dict[key][subkey])
            else:
                efficiency.append(conversion_dict[key][subkey])

    return_dict = {**return_dict, **{"Energy_Conversion": {'energy_minimum': sum(energy_min),
                                                           'energy_maximum': sum(energy_max)}}}
    # with the following one can also get the average energy conversion efficiency (redundant for us)

    # return_dict = {**return_dict, **{
    #     "Energy_Conversion": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
    #                           'efficiency': sum(efficiency) / len(efficiency)}}}

    return return_dict


# ##########################################################################################
# Descending interface/top_down_phase utilities
# ##########################################################################################
def from_tensor_to_dict(actions: np.ndarray, aggregators: list, agent: "Agent") -> dict:
    """
    This method is used to translate the actions taken by the A-C method into results understood by Peacefulness.
    The decision is to be stored.
    The return dict is under the format: {'Aggregator_1': {'Energy_Consumption': , 'Energy_Production': ...}, ...}
    """
    list_of_columns = []
    number_of_aggregators, number_of_actions = actions.shape

    if number_of_aggregators != len(aggregators):
        raise Exception("The number of actions taken by the RL does not correspond to the number of aggregators in the MEG")

    # Getting relevant info from the peacefulness_grid class considered for the RL agent
    agent_grid_topology = agent.grid.get_topology  # the return of the get_topology method
    agent_storage_devices = agent.grid.get_storage  # the return of the get_storage method

    # Finding the columns related to energy exchanges
    if len(agent_grid_topology) != 0:
        exchange_options = Counter(item for tup in agent_grid_topology for item in tup[:2])
        exchange_list = []
        for index in range(exchange_options.most_common(1)[0][1]):
            name = "Energy_Exchange_{}".format(index + 1)
            exchange_list.append(name)
        number_of_exchanges = exchange_options.most_common(1)[0][1]
    else:
        number_of_exchanges = 0

    # Finding the other columns
    condition = number_of_actions - number_of_exchanges
    if condition == 3:  # presence of energy consumers, production and storage
        list_of_columns.extend(["Energy_Consumption", "Energy_Production", "Energy_Storage"])
    elif condition == 2:  # presence of either energy consumers/production, consumers/storage or production/storage
        if max(agent_storage_devices.values()) == 0:  # presence of only energy consumers & production
            list_of_columns.extend(["Energy_Consumption", "Energy_Production"])
        else:
            if actions[0][0] < 0:  # presence of only energy production & storage
                list_of_columns.extend(["Energy_Production", "Energy_Storage"])
            else:  # presence of only energy consumers & storage
                list_of_columns.extend(["Energy_Consumption", "Energy_Storage"])
    elif condition == 1:  # presence of either energy consumers or energy production or energy storage
        if max(agent_storage_devices.values()) != 0:  # presence of only energy storage
            list_of_columns.extend(["Energy_Storage"])
        else:
            if actions[0][0] < 0:  # presence of only energy production
                list_of_columns.extend(["Energy_Production"])
            else:  # presence of only energy consumers
                list_of_columns.extend(["Energy_Consumption"])
    elif condition == 0:  # we only manage the energy exchanges between aggregators
        print("Attention, the MEG in question consists of only energy exchangers aggregators !")

    list_of_columns.extend(exchange_list)

    # First we get a dataframe from the actions tensor or vector
    actions_to_dataframe = pd.DataFrame(
                                        data=actions,
                                        index=aggregators,
                                        columns=list_of_columns
                                        )
    # We then get a dict from the dataframe
    actions_dict = actions_to_dataframe.to_dict()

    # Inverting the dict - to get the aggregators.names as keys.
    resulting_dict = {
        key: {k: v[key] for k, v in actions_dict.items()}
        for key in actions_dict[next(iter(actions_dict))].keys()
    }

    return resulting_dict


def extract_decision(decision_message: dict, aggregator: "Aggregator") -> list:
    """
    From the decisions taken by the RL agent concerning the whole multi-energy grid, we extract the decision related to the current aggregator.
    """
    consumption = {}
    production = {}
    storage = {}
    exchange = {}

    for element in decision_message.keys():  # TODO prices, at least for now, the RL agent needs the energy prices as input information, but its actions don't impact the prices
        if element == aggregator.name:
            dummy_dict = decision_message[element]
            if "Energy_Consumption" in dummy_dict:
                consumption = decision_message[element]["Energy_Consumption"]
                dummy_dict.pop("Energy_Consumption")
            if "Energy_Production" in dummy_dict:
                production = decision_message[element]["Energy_Production"]
                dummy_dict.pop("Energy_Production")
            if "Energy_Storage" in dummy_dict:
                storage = decision_message[element]["Energy_Storage"]
                dummy_dict.pop("Energy_Storage")
            exchange = dummy_dict.values()

    return [consumption, production, storage, exchange]
