# In this file, utilities and helper functions are defined for the Peacefulness to gym env.
# Imports
from math import cos, sin
from typing import Dict, List
from copy import deepcopy
from collections import deque
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

def correct_path(input_path: str):
    output_path = input_path.replace(".py", "")
    return output_path.replace("/", ".")

def modify_path(input_path: str):
    output_path = input_path.replace("\\", "/")
    return output_path

def truncate_left(s, word):
    idx = s.find(word)
    return s[idx:] if idx != -1 else s

def truncate_right(s, word):
    idx = s.find(word)
    return s[:idx] if idx != 0 else s


def find_my_aggregators(list_of_independent_aggregators, agent_ID=None) -> list:
    """
    This function is used to identify the aggregators managed by the Gym strategy.
    In the multi-agent configuration, the ID of the RL agent is also provided to define its scope.
    """
    corrected_list = []
    for aggregator in list_of_independent_aggregators:
        if not agent_ID:
            if aggregator.strategy.name == "gym_Strategy":
                corrected_list.append(aggregator)
        else:
            if aggregator.strategy.name == agent_ID:
                corrected_list.append(aggregator)
        corrected_list = [*corrected_list, *find_my_aggregators(aggregator.subaggregators, agent_ID)]

    return corrected_list


def group_components(catalog: "Catalog", agent_ID=None):
    """
    This function is used to communicate the information message to the RL agent (necessary to construct St).
    """
    formalism_message = {}  # here we retrieve the values of the formalism variables
    prediction_message = {}  # here we retrieve the predictions on rigid energy consumption and production
    prices = {}  # here we retrieve the values of energy prices
    conversions = {}  # here we retrieve the energy exchanges through energy conversion systems
    direct_exchanges = {}  # here we retrieve the energy exchanges without energy conversion systems

    # Distinction between single agent RL and multi-agent configuration
    if not agent_ID:
        ref_name = "gym_Strategy"
    else:
        ref_name = agent_ID

    # Getting the state of the multi-energy grid
    for aggregator in catalog.get(f"{ref_name}.strategy_scope"):
        formalism_message[aggregator.name] = catalog.get(f"{aggregator.name}.{ref_name}.formalism_message")

        # TODO patchwork solution - changing observation size breaks the RLlib loop (hydro-electricity)
        if "flexibility" not in formalism_message[aggregator.name]["Energy_Production"]:
            formalism_message[aggregator.name]["Energy_Production"]["flexibility"] = 0.0
        if "interruptibility" not in formalism_message[aggregator.name]["Energy_Production"]:
            formalism_message[aggregator.name]["Energy_Production"]["interruptibility"] = 0.0
        if "coming_volume" not in formalism_message[aggregator.name]["Energy_Production"]:
            formalism_message[aggregator.name]["Energy_Production"]["coming_volume"] = 0.0

        # TODO patchwork solution - changing observation size breaks the RLlib loop (heat demand during off-season)
        if len(formalism_message[aggregator.name]["Energy_Consumption"]) == 0:
            formalism_message[aggregator.name]["Energy_Consumption"]["energy_minimum"] = 0.0
            formalism_message[aggregator.name]["Energy_Consumption"]["energy_maximum"] = 0.0
            formalism_message[aggregator.name]["Energy_Consumption"]["flexibility"] = 0.0
            formalism_message[aggregator.name]["Energy_Consumption"]["interruptibility"] = 0.0
            formalism_message[aggregator.name]["Energy_Consumption"]["coming_volume"] = 0.0

        # TODO patchwork solution - changing observation size breaks the RLlib loop (heat demand during off-season + storage must be charged)
        if "flexibility" not in formalism_message[aggregator.name]["Energy_Consumption"]:
            formalism_message[aggregator.name]["Energy_Consumption"]["flexibility"] = 0.0
        if "interruptibility" not in formalism_message[aggregator.name]["Energy_Consumption"]:
            formalism_message[aggregator.name]["Energy_Consumption"]["interruptibility"] = 0.0
        if "coming_volume" not in formalism_message[aggregator.name]["Energy_Consumption"]:
            formalism_message[aggregator.name]["Energy_Consumption"]["coming_volume"] = 0.0

        if aggregator.forecaster:
            prediction_message[aggregator.name] = catalog.get(f"{aggregator.name}.{ref_name}.forecasting_message")
        prices[aggregator.name] = catalog.get(f"{aggregator.name}.{ref_name}.energy_prices")
        conversions[aggregator.name] = catalog.get(f"{aggregator.name}.{ref_name}.converter_message")
        if f"{aggregator.name}.{ref_name}.direct_energy_exchanges" in catalog.keys:
            exchanges = catalog.get(f"{aggregator.name}.{ref_name}.direct_energy_exchanges")
            for subaggregator in aggregator.subaggregators:
                if subaggregator.name in exchanges.keys():
                    direct_exchanges[aggregator.name] = {subaggregator.name: exchanges[subaggregator.name]}
            if aggregator.superior and aggregator.superior.nature == aggregator.nature:
                direct_exchanges[aggregator.superior.name] = {aggregator.name: exchanges[aggregator.name]}

    # Normalization based on the length simulated OR cyclical time with cos/sin
    # relevant_time = catalog.get("simulation_time")
    current_time = catalog.get("simulation_time")
    last_time = catalog.get("time_limit")
    relevant_time = [last_time, current_time]

    return relevant_time, formalism_message, prediction_message, prices, direct_exchanges, conversions


def return_correct_dict(normalization_parameters: Dict, agent_ID: str):
    """
    This function is used in case of multi-agent configuration.
    If the normalization parameters are given globally (the same for all the agents) or agent-specific.
    """
    to_return = {}
    if normalization_parameters:
        for key, values in normalization_parameters.items():
            if isinstance(values, dict):  # {"RL_agent": {"energy_minimum": , "energy_maximum": , "price_minimum": , "price_maximum": }, ...}
                to_return = normalization_parameters[agent_ID]
                break
            else:  # {"energy_minimum": , "energy_maximum": , "price_minimum": , "price_maximum": }
                to_return = normalization_parameters
                break

    return to_return


def construct_state(observation_dict: Dict, normalization_parameters: Dict={}):
    """
    This function is used to construct the observation vector (St).
    """
    return_list = []

    # Time feature
    if isinstance(observation_dict["iteration"], list):  # Normalization with the length of simulation
        if normalization_parameters == {}:
            return_list.append(observation_dict["iteration"][1])
        else:
            return_list.append(observation_dict["iteration"][1] / observation_dict["iteration"][0])
    else:  # We get cyclical time
        return_list.extend([sin(observation_dict["iteration"]), cos(observation_dict["iteration"])])

    # The other features
    internal_features = []
    external_features = []
    direct_exchanges = deepcopy(observation_dict["interconnection"])
    copy_of_conversions = process_conversions(observation_dict["conversion"])
    for aggregator in observation_dict["interior"]:
        # Initialization
        formalism = []
        forecast = []
        prices = []
        interconnection = []
        # Formalism variables related to consumers, producers and storage
        for typology in observation_dict["interior"][aggregator]:
            formalism.extend(observation_dict["interior"][aggregator][typology].values())
        if normalization_parameters != {}:
            for index in range(len(formalism)):
                # if index != 2 and index != 3 and index != 7 and index != 8 and index != 12 and index != 14 and index != 15:  # flexibility and manoeuvrability are also normalized
                if index != 12 and index != 14 and index != 15:  # only SOC, delta and eta are not normalized
                    formalism[index] = normalize_features(formalism[index], normalization_parameters["energy_minimum"], normalization_parameters["energy_maximum"])
        internal_features.extend(formalism)

        # Forecasting values for rigid consumers and producers
        if aggregator in observation_dict["forecast"]:
            depth = observation_dict["forecast"][aggregator]["depth"]
            observation_dict["forecast"][aggregator].pop("depth")
            for prediction in observation_dict["forecast"][aggregator]:  # rigid consumption and rigid production
                for value in observation_dict["forecast"][aggregator][prediction].values():  # low_estimation, high_estimation, confidence_level
                    if isinstance(value, list):
                        forecast.extend(value)
                    else:
                        forecast.append(value)
            if normalization_parameters != {}:
                for index in range(2 * depth):  # 1 loop to normalize both rigid consumptions and rigid productions
                    forecast[index] = normalize_features(forecast[index], normalization_parameters["energy_minimum"], normalization_parameters["energy_maximum"])
                    forecast[index + 3 * depth] = normalize_features(forecast[index + 3 * depth], normalization_parameters["energy_minimum"], normalization_parameters["energy_maximum"])
            internal_features.extend(forecast)

        # Energy prices for buying and selling
        if aggregator in observation_dict["prices"]:
            for value in observation_dict["prices"][aggregator].values():
                prices.append(value)
            if normalization_parameters != {}:
                for index in range(len(prices)):
                    prices[index] = normalize_features(prices[index], normalization_parameters["price_minimum"], normalization_parameters["price_maximum"])
            internal_features.extend(prices)

        # Interconnections between grids
        if aggregator in direct_exchanges:
            for subaggregator in direct_exchanges[aggregator]:
                interconnection.append(direct_exchanges[aggregator][subaggregator]["energy_minimum"])
                interconnection.append(direct_exchanges[aggregator][subaggregator]["energy_maximum"])
                interconnection.append(direct_exchanges[aggregator][subaggregator]["efficiency"])
            direct_exchanges.pop(aggregator)
        else:
            for superior in direct_exchanges:
                if aggregator in direct_exchanges[superior]:
                    interconnection.append(direct_exchanges[superior][aggregator]["energy_minimum"])
                    interconnection.append(direct_exchanges[superior][aggregator]["energy_maximum"])
                    interconnection.append(direct_exchanges[superior][aggregator]["efficiency"])
                direct_exchanges[superior].pop(aggregator)
        if normalization_parameters != {}:
            interconnection = normal_interconnection(interconnection, normalization_parameters["energy_minimum"], normalization_parameters["energy_maximum"])
        external_features.extend(interconnection)

        # Energy conversion systems
        to_be_removed = []
        for exchange in copy_of_conversions:  # list of tuples = [(exchanging_aggs, Emin, Emax, efficiency), ...]
            conversions = []
            if aggregator in exchange[0]:
                conversions.append(*exchange[1])
                conversions.append(*exchange[2])
                if normalization_parameters != {}:
                    for index in range(len(conversions)):
                        conversions[index] = normalize_features(conversions[index], normalization_parameters["energy_minimum"], normalization_parameters["energy_maximum"])
                conversions.append(*exchange[3])
                to_be_removed.append(copy_of_conversions.index(exchange))
            external_features.extend(conversions)
        copy_of_conversions = [tup for index, tup in enumerate(copy_of_conversions) if index not in to_be_removed]

        return_list.extend(internal_features)
        return_list.extend(external_features)

    return return_list


def normalize_features(feature, min_val, max_val):
    """
    This is a helper function used to normalize the features at the environment-level.
    In contrast, agent-level normalization is made using VecNormalize from Stable Baselines 3.
    """
    if min_val <= feature <= max_val:
        norm_feature = ((feature - min_val) / (max_val - min_val)) * 2 - 1
    elif feature < min_val:
        norm_feature = - 1.0
    elif feature > max_val:
        norm_feature = 1.0
    else:
        raise Exception("Normalization error !")

    return norm_feature


def scale_up_feature(feature, min_val, max_val):
    """
    This is a helper function used to scale up actions.
    By default, actions are normalized between -1 and 1 interval.
    """
    # if -1.0 <= feature <= 1.0:
    #     scaled_feature = min_val + (max_val - min_val) * ((feature + 1) / 2)
    # else:
    #     raise Exception("Scale-up error !")
    scaled_feature = min_val + (max_val - min_val) * ((feature + 1) / 2)

    return scaled_feature


def normalize_my_rewards(reward, norm_dict):
    return ((reward - norm_dict["energy_minimum"]) / (norm_dict["energy_maximum"] - norm_dict["energy_minimum"])) * 2 - 1


def normal_interconnection(raw_list, min_val, max_val):
    """
    This is a helper function used to normalize the interconnection energy exchange between aggregators (without the intermediary of energy conversion systems).
    """
    norm_list = []
    for i in range(0, len(raw_list), 3):
        Emin, Emax, eta = raw_list[i:i+3]
        norm_Emin = normalize_features(Emin, min_val, max_val)
        norm_Emax = normalize_features(Emax, min_val, max_val)
        norm_list.extend([norm_Emin, norm_Emax, eta])
    return norm_list


def process_conversions(conversion):
    """
    This is a helper function used to reverse the dictionary of energy conversion systems.
    Then a list of tuples is made for each energy exchange conducted with an energy conversion system.
    """
    my_list = []
    reverse_dict = {}
    for element in conversion:  # aggregators names
        for key in conversion[element]["Energy_Conversion"]:  # (energy conversion systems names)
            if key in reverse_dict:
                reverse_dict[key].append(element)
            else:
                reverse_dict[key] = [element]  # {"converter_1_name": ["aggregator_1", "aggregator_2", ...], ...}

    Emin = []
    Emax = []
    efficiency = []
    # reverse dict is a dict where keys are names of energy conversion systems and values are the list of names of aggregators connected through them
    for key, value in reverse_dict.items():
        exchanging_aggregators = [*value]  # names of aggregators managing the energy conversion system
        for element in exchanging_aggregators:
            Emin.append(conversion[element]["Energy_Conversion"][key]['energy_minimum'])
            Emax.append(conversion[element]["Energy_Conversion"][key]['energy_maximum'])
            device_efficiency = conversion[element]["Energy_Conversion"][key]['efficiency']
            if not isinstance(device_efficiency, dict):
                efficiency.append(device_efficiency)
            else:
                efficiency.append(list(device_efficiency.values()))
        exchanging_aggregators.append(key)
        my_list.append(deepcopy((exchanging_aggregators, Emin, Emax, efficiency)))
        Emin.clear()
        Emax.clear()
        efficiency.clear()

    return my_list


def get_correct_action_dict(agent_dict: Dict):
    """
    This method is used to get a dict of actions for each agent as follows : {"RLagent_ID": {"interior":{"aggregator": , ... }, "exchanges": }, ...}.
    :param agent_dict: A dict as follows {"RLagent_ID": {"aggregator": (obs_size, action_size), ..., "nb_exchanges": }, ...}.
    """
    act_dict = {}
    for agent in agent_dict:
        act_dict[agent] = {"interior": {}}
        for key in agent_dict[agent]:
            if key != "exchanges":
               act_dict[agent]["interior"] = {**act_dict[agent]["interior"], **{key: agent_dict[agent][key][1]}}
            else:
               act_dict[agent] = {**act_dict[agent], **{key: agent_dict[agent][key]}}
    return act_dict


def distribute_my_action(action: List, catalog: "Catalog", action_info: Dict, agent_ID=None, red_dof_dict=None):
    """
    This function is used in the step method to distribute the RL agent's action to each corresponding aggregator.
    """
    # Distinction between single agent RL and multi-agent configuration
    if not agent_ID:
        ref_name = "gym_Strategy"
    else:
        ref_name = agent_ID

    # In case we remove 1-degree of freedom (1 less action) per aggregator
    interior_dofr = {}
    direct_exterior_dofr_dict = {}
    direct_exterior_dofr = 0
    conversion_exterior_dofr_dict = {}
    conversion_exterior_dofr = 0
    if red_dof_dict is not None:
        for agg, deg in red_dof_dict.items():
            if "Exchange" in deg:  # the action removed from the action space of the concerned RLagent is exchange with outside
                direct_exterior_dofr_dict[agg] = 1
                direct_exterior_dofr += 1
            elif "Conversion" in deg:
                conversion_exterior_dofr_dict[agg] = 1
                conversion_exterior_dofr += 1
            else:  # the removed action is internal (consumption, production or storage)
                interior_dofr[agg] = 1

    # Initialization
    raw_state = deepcopy(catalog.get(f"{ref_name}.raw_state"))
    managed_aggregators = catalog.get(f"{ref_name}.strategy_scope")
    nb_exchange_actions = action_info["exchanges"] - direct_exterior_dofr - conversion_exterior_dofr  # we remove the number of "removed" exterior actions from original length

    # internal actions
    internal_actions = action[:-nb_exchange_actions]  if nb_exchange_actions != 0 else action[:]  # corresponding to the length of "removed" internal actions
    interior_dict = {}
    index = 0
    for agg, nb_interior in action_info["interior"].items():
        if agg in interior_dofr:  # we check if for this aggregator the "removed" action is internal (consumption, production or storage)
            to_remove = 1
        else:
            to_remove = 0
        chunk = internal_actions[index: index + nb_interior - to_remove]
        interior_dict[agg] = chunk
        index += nb_interior
    if f"{ref_name}.interior_decision" not in catalog.keys:  # {"aggregator_name": [Econ_norm, Eprod_norm, Esto_norm], ...}
        catalog.add(f"{ref_name}.interior_decision", interior_dict)  # normalized actions (interior)
    else:  # the length corresponds correctly to the case where we remove one degree of freedom w.r.t internal actions
        catalog.set(f"{ref_name}.interior_decision", interior_dict)

    # external actions
    external_actions = action[-nb_exchange_actions:] if nb_exchange_actions != 0 else []
    exchanges_dict = {}
    external_dict = {agg.name: 0 for agg in managed_aggregators}
    for agg in external_dict:
        # First interconnections (direct energy exchange without use of energy conversion systems)
        if agg in raw_state["interconnection"]:
            external_dict[agg] += len(raw_state["interconnection"][agg])
            raw_state["interconnection"].pop(agg)
        else:
            key_to_remove = []
            for sup in raw_state["interconnection"]:
                if agg in raw_state["interconnection"][sup]:
                    external_dict[agg] += 1
                    key_to_remove.append(sup)
            for sup in key_to_remove:
                raw_state["interconnection"][sup].pop(agg)

        if f"{agg}.net_number_of_direct_energy_exchanges" not in catalog.keys:  # useful to get the downstream action for converters
            catalog.add(f"{agg}.net_number_of_direct_energy_exchanges", external_dict[agg] - direct_exterior_dofr)
        else:
            catalog.set(f"{agg}.net_number_of_direct_energy_exchanges", external_dict[agg] - direct_exterior_dofr)

        # Then energy exchanges using energy conversion systems
        if agg in raw_state["conversion"]:
            external_dict[agg] += len(raw_state["conversion"][agg]["Energy_Conversion"])
    index = 0
    for agg, nb_exchanges in external_dict.items():
        if agg in direct_exterior_dofr_dict or agg in conversion_exterior_dofr_dict:  # we check if for this aggregator the "removed" action is external (exchange)
            to_remove = 1
        else:
            to_remove = 0
        chunk = external_actions[index: index + nb_exchanges - to_remove]
        exchanges_dict[agg] = chunk
        index += nb_exchanges
    if f"{ref_name}.exterior_decision" not in catalog.keys:  # {"aggregator_name": [Eexch_1-norm, Eexch_2-norm, ...], ...}
        catalog.add(f"{ref_name}.exterior_decision", exchanges_dict)  # normalized actions (exterior)
    else:  # the length corresponds correctly to the case where we remove one degree of freedom w.r.t external actions
        catalog.set(f"{ref_name}.exterior_decision", exchanges_dict)


def implement_my_interior_decision(agentID: str, catalog: "Catalog", aggregator: "Aggregator", red_dof_flag=False):
    """
    This function is used inside the top_down_phase method of the gym strategy.
    We use it to scale-up the normalized at and return the dict of the internal actions.
    """
    # Initialization
    returned_list = []
    typologies = ["Energy_Consumption", "Energy_Production", "Energy_Storage"]
    raw_state = catalog.get(f"{agentID}.raw_state")
    interior_decision = catalog.get(f"{agentID}.interior_decision")

    # In case, we remove one action per aggregator
    idx_removed = None
    if red_dof_flag:  # Otherwise we get a catalog Exception error
        reduced_action = catalog.get(f"Action removed for {aggregator.name}")
    else:
        reduced_action = None
    if reduced_action is not None and reduced_action in typologies:
        idx_removed = typologies.index(reduced_action)
        typologies.remove(reduced_action)

    # We retrieve the normalized actions.
    norm_decision = deque(interior_decision[aggregator.name])

    # Then, we scale them up.
    for typ in typologies:
        if len(raw_state["interior"][aggregator.name][typ]) > 0:
            returned_list.append(scale_up_feature(norm_decision.popleft(), raw_state["interior"][aggregator.name][typ]["energy_minimum"], raw_state["interior"][aggregator.name][typ]["energy_maximum"]))

    # Final check
    if len(returned_list) < 3:
        if idx_removed is not None:
            returned_list.insert(idx_removed, 0.0)
        else:
            returned_list.append(0.0)
    if len(returned_list) > 3:
        raise Exception("Error in defining the interior actions !")

    return returned_list


def implement_my_exchange_decision(agentID: str, catalog: "Catalog", aggregator: "Aggregator", red_dof_flag=False):
    """
    This function is used inside the top_down_phase method of the gym strategy.
    We use it to scale-up the normalized at and return the dict of Eexch.
    """
    # Initialization
    exchange_dict = {}
    raw_state = catalog.get(f"{agentID}.raw_state")
    exchange_decision = catalog.get(f"{agentID}.exterior_decision")  # normalized actions with length reduced if action reduction

    # In case, we remove one action per aggregator
    exchange_to_remove = 0
    conversion_to_remove = 0
    if red_dof_flag:  # Otherwise we get a catalog Exception error
        reduced_action = catalog.get(f"Action removed for {aggregator.name}")
        if "Exchange" in reduced_action:
            exchange_to_remove = 1
        elif "Conversion" in reduced_action:
            conversion_to_remove = 1
    else:
        reduced_action = None

    # First, we retrieve the normalized actions.
    nb_direct_exchanges = 0
    nb_conversion_actions = 0
    if aggregator.name in raw_state["conversion"]:
        nb_conversion_actions += len(raw_state["conversion"][aggregator.name]["Energy_Conversion"])
        list_of_converters = list(raw_state["conversion"][aggregator.name]["Energy_Conversion"].keys())
    nb_conversion_actions -= conversion_to_remove
    if aggregator.subaggregators:
        for subaggregator in aggregator.subaggregators:
            if aggregator.nature == subaggregator.nature:
                nb_direct_exchanges += 1
    if aggregator.superior and aggregator.superior.nature == aggregator.nature:
        nb_direct_exchanges += 1
    nb_direct_exchanges -= exchange_to_remove

    direct_exchanges = []
    conversions = []

    if aggregator.name in exchange_decision:
        if nb_conversion_actions != 0:  # in case where agents/aggregators decide on both ends of energy conversion systems
            direct_exchanges.extend(exchange_decision[aggregator.name][:nb_direct_exchanges])
            conversions.extend(exchange_decision[aggregator.name][nb_direct_exchanges:])
            # if len(exchange_decision[aggregator.name]) == nb_direct_exchanges + nb_conversion_actions:  # the aggregator is upstream w.r.t energy converters
            #     direct_exchanges.extend(exchange_decision[aggregator.name][:nb_direct_exchanges])
            #     conversions.extend(exchange_decision[aggregator.name][nb_direct_exchanges:])
            # else:  # if a degree of freedom is removed
            #     direct_exchanges.extend(exchange_decision[aggregator.name][:nb_direct_exchanges])
            #     conversions.extend(complete_conversion_norm_action(catalog, agentID, list_of_converters, exchange_decision[aggregator.name][nb_direct_exchanges:]))
        else:
            direct_exchanges.extend(exchange_decision[aggregator.name])
        direct_exchanges = deque(direct_exchanges)  # length corresponding to the removed exchanges
        conversions = deque(conversions)  # length corresponding to the removed conversions

    # Then, we scale-up 'at'.
    idx_exch = 1
    if aggregator.name in raw_state["interconnection"]:
        for sub in raw_state["interconnection"][aggregator.name]:
            if reduced_action is not None:
                if exchange_to_remove > 0 and str(idx_exch) in reduced_action:
                    scaled_up_action = 0.0
                else:
                    scaled_up_action = scale_up_feature(direct_exchanges.popleft(), raw_state["interconnection"][aggregator.name][sub]["energy_minimum"], raw_state["interconnection"][aggregator.name][sub]["energy_maximum"])
                idx_exch += 1
            else:
                scaled_up_action = scale_up_feature(direct_exchanges.popleft(), raw_state["interconnection"][aggregator.name][sub]["energy_minimum"], raw_state["interconnection"][aggregator.name][sub]["energy_maximum"])
            exchange_dict = {**exchange_dict, **{tuple([aggregator.name, sub]): scaled_up_action}}
    else:
        for superior in raw_state["interconnection"]:
            if aggregator.name in raw_state["interconnection"][superior]:
                if reduced_action is not None:
                    if exchange_to_remove > 0 and str(idx_exch) in reduced_action:
                        scaled_up_action = 0.0
                    else:
                        scaled_up_action = scale_up_feature(direct_exchanges.popleft(), raw_state["interconnection"][superior][aggregator.name]["energy_minimum"], raw_state["interconnection"][superior][aggregator.name]["energy_maximum"])
                    idx_exch += 1
                else:
                    scaled_up_action = scale_up_feature(direct_exchanges.popleft(), raw_state["interconnection"][superior][aggregator.name]["energy_minimum"], raw_state["interconnection"][superior][aggregator.name]["energy_maximum"])
                exchange_dict = {**exchange_dict, **{tuple([superior, aggregator.name]): scaled_up_action}}

    conversion_list = process_conversions(raw_state["conversion"])
    idx_cv = 1 + len(exchange_dict)
    for exchange in conversion_list:
        if aggregator.name in exchange[0]:
            my_index = exchange[0].index(aggregator.name)
            if reduced_action is not None:
                if conversion_to_remove > 0 and str(idx_cv) in reduced_action:
                    scaled_up_action = 0.0
                else:
                    scaled_up_action = scale_up_feature(conversions.popleft(), exchange[1][my_index], exchange[2][my_index])
                idx_cv += 1
            else:
                scaled_up_action = scale_up_feature(conversions.popleft(), exchange[1][my_index], exchange[2][my_index])
            exchange_dict = {**exchange_dict, **{tuple(exchange[0]): scaled_up_action}}

    return exchange_dict


def complete_conversion_norm_action(catalog: "Catalog", agentID: str, list_of_converters: List, rest_of_action: List):
    """
    This function is used to get the decision corresponding to the conversion systems for the downstream aggregator from
    the decision taken in the upstream.
    """
    rest_of_action.reverse()
    existing_agents = deepcopy(catalog.get(f"existing_RL_agents"))
    managed_agg = {}
    for agent in existing_agents:
        agg_list = catalog.get(f"{agent}.strategy_scope")
        managed_agg[agent] = [agg.name for agg in agg_list]

    relevant_decision = []
    for converter_name in list_of_converters:
        converter = catalog.devices[converter_name]
        upstream_agg = [upstream['name'] for upstream in converter._upstream_aggregators_list]
        for agg in upstream_agg:
            for agent in managed_agg:
                if agg in managed_agg[agent] and agent != agentID:
                    other_exterior_decision = catalog.get(f"{agent}.exterior_decision")[agg]
                    other_interval = catalog.get(f"{agent}.raw_state")['conversion'][agg]["Energy_Conversion"]
                    num_direct_exchanges = catalog.get(f"{agg}.net_number_of_direct_energy_exchanges")
                    for idx, key in enumerate(other_interval):  # todo limit (can't apply action reduction to conversions, unless the strategy of the upstream aggregator is executed first) !
                        if key == converter_name:
                            relevant_idx = idx + num_direct_exchanges
                            break
                    if len(other_exterior_decision) == len(other_interval) + num_direct_exchanges:  # no direct exchange or conversion action was removed for the upstream aggregator
                        relevant_decision.append(other_exterior_decision[relevant_idx])
                        # relevant_decision.append(other_exterior_decision[-1])  # todo -1 is a patchwork for the mini-case with 2 dummy converters (o remove if 1 converter only)
                        break
                    else:  # we get the scaled up actions already computed during the strategy run for the upstream aggregator
                        other_scaled_up_exterior_decision = list(catalog.get(f"{agg}.{agent}.exchange_decision").values())[relevant_idx]
                        Emin = other_interval[converter_name]["energy_minimum"]
                        Emax = other_interval[converter_name]["energy_maximum"]
                        relevant_decision.append(2 * ((other_scaled_up_exterior_decision - Emin) / (Emax - Emin)) - 1)
                        break
                elif agg in managed_agg[agent] and agent == agentID:
                    relevant_decision.append(rest_of_action.pop())
                    break

    return relevant_decision


def complete_reduced_action(Econ: float, Eprod: float, Esto: float, Eexch: Dict, catalog: "Catalog", aggregator: "Aggregator"):
    """
    This function is used to complete the reduced decision by computing the removed action/degree of freedom.
    """
    # Initialization
    reduced_action = catalog.get(f"Action removed for {aggregator.name}")
    energy_exchanges = list(Eexch.values())

    # Internal decision
    if reduced_action == "Energy_Consumption":
        Econ = - Eprod - Esto - sum(energy_exchanges)
    elif reduced_action == "Energy_Production":
        Eprod = - Econ - Esto - sum(energy_exchanges)
    elif reduced_action == "Energy_Storage":
        Esto = - Econ - Eprod - sum(energy_exchanges)
    # Energy exchange
    elif "Exchange" in reduced_action or "Conversion" in reduced_action:
        idx_exch = int(reduced_action[-1])
        energy_exchanges[idx_exch - 1] = - Econ - Eprod - Esto - sum(energy_exchanges[:idx_exch - 1]) - sum(energy_exchanges[idx_exch:])
    else:
        raise Exception("The dict of action removal is not correctly defined !")
    Eexch = dict(zip(Eexch.keys(), energy_exchanges))  # rebuilding the Eexch dict

    return Econ, Eprod, Esto, Eexch


def second_ask(aggregator: "Aggregator"):
    # forecast update
    if aggregator._forecaster:
        aggregator._forecaster.update_forecast()

    quantities_and_prices = aggregator._strategy.bottom_up_phase(aggregator)
    if quantities_and_prices and aggregator._contract:
        quantities_and_prices = [aggregator._contract.contract_modification(element, aggregator.name) for element in quantities_and_prices]
        aggregator._catalog.set(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_wanted", quantities_and_prices)


def second_distribute(aggregator: "Aggregator"):
    aggregator._strategy.top_down_phase(aggregator)  # distribute the energy acquired from or sold to the exterior


def recapitulate_decision(catalog: "Catalog", agent_ID=None) -> Dict:
    """
    This helper function is used in the step method to retrieve all the decisions.
    It is useful to compute the immediate reward.
    """
    # Distinction between single agent RL and multi-agent configuration
    if not agent_ID:
        ref_name = "gym_Strategy"
    else:
        ref_name = agent_ID

    return_dict = {}
    managed_aggregators = catalog.get(f"{ref_name}.strategy_scope")
    scope_key = ref_name + f".scope"
    return_dict[scope_key] = []
    for agg in managed_aggregators:
        return_dict[scope_key].append(agg.name)
        interior_decision = catalog.get(f"{agg.name}.{ref_name}.internal_decision")  # list (scaled-up actions)
        external_decision = catalog.get(f"{agg.name}.{ref_name}.exchange_decision")  # dict (scaled-up actions)
        key = agg.name + f".{ref_name}.scaled_up_actions"
        return_dict[key] = [*interior_decision, *list(external_decision.values())]

    return return_dict


def recapitulate_state(catalog: "Catalog", agent_ID=None) -> Dict:
    """
    This helper function is used in the step method to retrieve the energy flow intervals raw state.
    It is useful to compute the immediate reward.
    """
    # Distinction between single agent RL and multi-agent configuration
    if not agent_ID:
        ref_name = "gym_Strategy"
    else:
        ref_name = agent_ID
    raw_state = catalog.get(f"{ref_name}.raw_state")

    # Internal energy flow values
    return_dict  = {}
    for agg in raw_state['interior']:
        key = agg + '.energy_flow_values_intervals'
        return_dict[key] = {"Energy_Consumption": [], "Energy_Production": [], "Energy_Storage": []}
        for tup in raw_state["interior"][agg]:
            if len(raw_state["interior"][agg][tup]) > 0:
                return_dict[key][tup].append(raw_state["interior"][agg][tup]['energy_minimum'])
                return_dict[key][tup].append(raw_state["interior"][agg][tup]['energy_maximum'])

    # External energy flow values (subaggregator ; superior ; conversions)
    for agg in return_dict:
        og_key = truncate_right(agg, '.energy_flow_values_intervals')
        idx = 1
        if og_key in raw_state["interconnection"]:
            for sub in raw_state["interconnection"][og_key]:
                return_dict[agg].update({f"Energy_Exchange_{idx}": [raw_state["interconnection"][og_key][sub]['energy_minimum'],
                                                                    raw_state["interconnection"][og_key][sub]['energy_maximum']]})
                idx += 1
        else:
            for sup in raw_state["interconnection"]:
                if og_key in raw_state["interconnection"][sup]:
                    return_dict[agg].update({f"Energy_Exchange_{idx}": [raw_state["interconnection"][sup][og_key]["energy_minimum"],
                                                                        raw_state["interconnection"][sup][og_key]["energy_maximum"]]})
                    idx += 1
        if len(raw_state["conversion"][og_key]["Energy_Conversion"]) > 0:
            for conv_sys in raw_state["conversion"][og_key]["Energy_Conversion"]:
                return_dict[agg].update({f"Energy_Conversion_{idx}": [raw_state["conversion"][og_key]["Energy_Conversion"][conv_sys]["energy_minimum"],
                                                                      raw_state["conversion"][og_key]["Energy_Conversion"][conv_sys]["energy_maximum"]]})
                idx += 1

    return return_dict


def converters_recap(catalog: "Catalog", agent_ID=None) -> Dict:
    """
    This helper function is used to return a dict of converters offsets.
    """
    return_dict = {f"{agent_ID}.converters_offset": []}  # todo patchwork solution
    for key in catalog.keys:
        if agent_ID in key and "converters_offset" in key:
            return_dict[f"{agent_ID}.converters_offset"].extend(catalog.get(key))

    return return_dict


def export_my_decision_file(decision_dict: Dict, export_path: str, number_of_direct_energy_exchanges: int, number_of_conversions: int):
    """
    This helper function is used to export the decision of the RL agents during inference per aggregator.
    """
    max_len = max(len(decs[0]) for decs in decision_dict.values())
    with open(export_path + ".csv", "w", newline="") as myFile:
        writer = csv.writer(myFile)
        # Dynamic header
        header = ["aggregator"] + ["Energy_Consumption", "Energy_Production", "Energy_Storage"]
        if number_of_direct_energy_exchanges > 0:
            header += [f"Energy_Exchange_{idx + 1}" for idx in range(number_of_direct_energy_exchanges)]
        if number_of_conversions > 0:
            header += [f"Energy_Conversion_{idx + 1}" for idx in range(number_of_direct_energy_exchanges, number_of_direct_energy_exchanges + number_of_conversions)]
        writer.writerow(header)

        for agg, dec_list in decision_dict.items():
            for dec in dec_list:
                padded = dec + [""] * (max_len - len(dec))  # padding to get a corresponding length to header
                writer.writerow([agg] + padded)


def export_my_state_file(state_dict: Dict, export_path: str, number_of_direct_energy_exchanges: int, number_of_conversions: int):
    """
    This helper function is used to export the min/max intervals for energy flow values for each corresponding decision.
    """
    max_len = max(len(typ) for typ in state_dict.values())
    with open(export_path + '.csv', "w", newline="") as myFile:
        writer = csv.writer(myFile)
        # Dynamic header
        header = ["aggregator"] + ["Energy_Consumption", "Energy_Production", "Energy_Storage"]
        if number_of_direct_energy_exchanges > 0:
            header += [f"Energy_Exchange_{idx + 1}" for idx in range(number_of_direct_energy_exchanges)]
        if number_of_conversions > 0:
            header += [f"Energy_Conversion_{idx + 1}" for idx in range(number_of_direct_energy_exchanges, number_of_direct_energy_exchanges + number_of_conversions)]
        writer.writerow(header)

        for agg in state_dict:
            for idx in range(len(state_dict[agg][header[1]])):
                padded = [agg]
                for element in header[1:]:
                    if element not in state_dict[agg]:
                        padded += ["",""]
                    else:
                        padded += state_dict[agg][element][idx] if len(state_dict[agg][element][idx]) > 0 else ["",""]
                writer.writerow(padded)
                padded.clear()


def plot_my_results(minmax_dict: Dict, real_dict: Dict, path_to_export: str):
    """
    :param minmax_dict: Dictionary containing min/max intervals.
    :param real_dict: Dictionary containing actual chosen values.
    """
    # internal_quantities = ["Energy_Consumption", "Energy_Production", "Energy_Storage"]
    # Apply Scientific Style settings locally
    with plt.rc_context({
        'font.family': 'serif',  # Serif fonts are standard for papers
        'font.size': 11,
        'axes.grid': True,
        'grid.alpha': 0.3,  # Light grid
        'grid.linestyle': '--',
        'axes.spines.top': False,  # Remove top border
        'axes.spines.right': False,  # Remove right border
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.edgecolor': 'white'
    }):

        for agg in minmax_dict.keys():
            # Map agent keys
            common_key = truncate_right(agg, ".")

            # --- Configuration ---
            # Map the list indices in 'real_dict' to variable names in 'minmax_dict'
            # Order observed: Consumption, Production, Storage, Exchange
            quantities_to_plot = []  # Energy consumption, production, storage, exchange
            idx_to_remove = None
            for idx, quantity in enumerate(minmax_dict[agg]):
                if any(minmax_dict[agg][quantity]):  # if not empty
                    quantities_to_plot.append(quantity)
                else:
                    idx_to_remove = idx

            # Extract Data
            minmax_data = minmax_dict[agg]
            for k in real_dict:
                if common_key in k:
                    real_data = np.array(real_dict[k])
                    if idx_to_remove is not None:
                        real_data = np.delete(real_data, idx_to_remove, 1)
                    break
            n_steps = len(real_data)
            time_steps = np.arange(n_steps)

            # Create Figure (N variables x 1 column)
            fig, axes = plt.subplots(len(quantities_to_plot), 1, figsize=(8, 10), sharex=True)

            # If only 1 variable, axes is not a list, so we fix that
            if len(quantities_to_plot) == 1: axes = [axes]

            # Plot title
            fig.suptitle(f"{common_key} Energy Profile".capitalize(), fontsize=14, fontweight='bold', y=0.96)

            for i, var_name in enumerate(quantities_to_plot):
                ax = axes[i]

                # 1. Prepare Data
                actual_vals = real_data[:, i]
                interval_raw = minmax_data[var_name]
                # Slice interval data to match the length of real data
                # (MinMax often has N+1 or different horizon length)
                current_intervals = interval_raw[:n_steps]
                lowers = []
                uppers = []
                # Process intervals (handle empty lists for cases like Storage in Comm 2)
                for interval in current_intervals:
                    lowers.append(min(interval))
                    uppers.append(max(interval))

                # 2. Plotting
                # A. Feasible Region (Shaded Band)
                # 'step="post"' fills the area between steps correctly for discrete time
                ax.fill_between(time_steps, lowers, uppers, step='post', color='#6996b3', alpha=0.2, label='Feasible Range')

                # B. Bounds (Thin dotted lines for clarity)
                ax.step(time_steps, lowers, where='post', color='#6996b3', linestyle=':', linewidth=0.8, alpha=0.5)
                ax.step(time_steps, uppers, where='post', color='#6996b3', linestyle=':', linewidth=0.8, alpha=0.5)

                # C. Actual Action (Solid Line + Markers)
                # Markers help identify specific decision points
                ax.step(time_steps, actual_vals, where='post', color='#004c6d', linewidth=1.5, label='RL decision', zorder=5)
                ax.scatter(time_steps, actual_vals, color='#004c6d', s=15, zorder=6)

                # 3. Labeling
                formatted_label = var_name.replace('_', ' ')
                ax.set_ylabel(f"{formatted_label}", fontsize=10)  # Name of the axis

                ax.text(0, 1.02, "[kWh]",  # Unit
                            transform=ax.transAxes,
                            fontsize=10,
                            ha='left',  # Horizontal alignment
                            va='bottom',  # Vertical alignment
                            rotation=0)  # Keep it horizontal

                # Only show legend on the first subplot to avoid clutter
                if i == 0:
                    ax.legend(loc='upper right', fontsize=9)

                # Only show X-axis label on the bottom subplot
                if i == len(quantities_to_plot) - 1:
                    ax.set_xlabel("Time Step - [Hour]", fontsize=12)

            plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
            # plt.show()
            plt.savefig(path_to_export + f"{common_key}.pdf", format='pdf', bbox_inches='tight', pad_inches=0.05)
