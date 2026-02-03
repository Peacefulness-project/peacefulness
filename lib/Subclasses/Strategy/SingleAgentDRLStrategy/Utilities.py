# In this file, utilities and helper functions are defined for the Peacefulness to gym env.
# Imports
from math import cos, sin
from typing import Dict, List
from copy import deepcopy
from collections import deque


def correct_path(input_path: str):
    output_path = input_path.replace(".py", "")
    return output_path.replace("/", ".")

def modify_path(input_path: str):
    output_path = input_path.replace("\\", "/")
    return output_path

def truncate_left(s, word):
    idx = s.find(word)
    return s[idx:] if idx != -1 else s


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

        # TODO patchwork solution - changing observation size breaks the RLlib loop
        if "flexibility" not in formalism_message[aggregator.name]["Energy_Production"]:
            formalism_message[aggregator.name]["Energy_Production"]["flexibility"] = 0.0
        if "interruptibility" not in formalism_message[aggregator.name]["Energy_Production"]:
            formalism_message[aggregator.name]["Energy_Production"]["interruptibility"] = 0.0
        if "coming_volume" not in formalism_message[aggregator.name]["Energy_Production"]:
            formalism_message[aggregator.name]["Energy_Production"]["coming_volume"] = 0.0


        if aggregator.forecaster:
            prediction_message[aggregator.name] = catalog.get(f"{aggregator.name}.{ref_name}.forecasting_message")
        prices[aggregator.name] = catalog.get(f"{aggregator.name}.{ref_name}.energy_prices")
        conversions[aggregator.name] = catalog.get(f"{aggregator.name}.{ref_name}.converter_message")
        if aggregator.subaggregators:
            direct_exchanges[aggregator.name] = catalog.get(f"{aggregator.name}.{ref_name}.direct_energy_exchanges")
        if aggregator.superior:
            direct_exchanges[aggregator.superior.name] = catalog.get(f"{aggregator.name}.{ref_name}.direct_energy_exchanges")

    # Normalization based on the length simulated OR cyclical time with cos/sin
    relevant_time = catalog.get("simulation_time")
    # current_time = catalog.get("simulation_time")
    # last_time = catalog.get("time_limit")
    # relevant_time = [last_time, current_time]

    return relevant_time, formalism_message, prediction_message, prices, direct_exchanges, conversions


def return_correct_dict(normalization_parameters: Dict, agent_ID: str):
    """
    This function is used in case of multi-agent configuration.
    If the normalization parameters are given globally (the same for all the agents) or agent-specific.
    """
    to_return = {}
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
        norm_feature = (feature - min_val) / (max_val - min_val)
    elif feature < min_val:
        norm_feature = 0.0
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
    if -1.0 <= feature <= 1.0:
        scaled_feature = min_val + (max_val - min_val) * ((feature + 1) / 2)
    else:
        raise Exception("Scale-up error !")

    return scaled_feature


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
        my_list.append((exchanging_aggregators, Emin, Emax, efficiency))
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


def distribute_my_action(action: List, catalog: "Catalog", action_info: Dict, agent_ID=None):
    """
    This function is used in the step method to distribute the RL agent's action to each corresponding aggregator.
    """
    # Distinction between single agent RL and multi-agent configuration
    if not agent_ID:
        ref_name = "gym_Strategy"
    else:
        ref_name = agent_ID

    raw_state = deepcopy(catalog.get(f"{ref_name}.raw_state"))
    managed_aggregators = catalog.get(f"{ref_name}.strategy_scope")
    nb_exchange_actions = action_info["exchanges"]

    # internal actions
    internal_actions = action[:-nb_exchange_actions]
    interior_dict = {}
    index = 0
    for agg, nb_interior in action_info["interior"].items():
        chunk = internal_actions[index: index + nb_interior]
        interior_dict[agg] = chunk
        index += nb_interior
    if f"{ref_name}.interior_decision" not in catalog.keys:  # {"aggregator_name": [Econ_norm, Eprod_norm, Esto_norm], ...}
        catalog.add(f"{ref_name}.interior_decision", interior_dict)  # normalized actions (interior)
    else:
        catalog.set(f"{ref_name}.interior_decision", interior_dict)

    # external actions
    external_actions = action[-nb_exchange_actions:]
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
        # Then energy exchanges using energy conversion systems
        if agg in raw_state["conversion"]:
            external_dict[agg] += len(raw_state["conversion"][agg]["Energy_Conversion"])
    index = 0
    for agg, nb_exchanges in external_dict.items():
        chunk = external_actions[index: index + nb_exchanges]
        exchanges_dict[agg] = chunk
        index += nb_exchanges
    if f"{ref_name}.exterior_decision" not in catalog.keys:  # {"aggregator_name": [Eexch_1-norm, Eexch_2-norm, ...], ...}
        catalog.add(f"{ref_name}.exterior_decision", exchanges_dict)  # normalized actions (exterior)
    else:
        catalog.set(f"{ref_name}.exterior_decision", exchanges_dict)


def implement_my_interior_decision(agentID: str, catalog: "Catalog", aggregator: "Aggregator"):
    """
    This function is used inside the top_down_phase method of the gym strategy.
    We use it to scale-up the normalized at and return the dict of the internal actions.
    """
    # Initialization
    returned_list = []
    typologies = ["Energy_Consumption", "Energy_Production", "Energy_Storage"]
    raw_state = catalog.get(f"{agentID}.raw_state")
    interior_decision = catalog.get(f"{agentID}.interior_decision")

    # We retrieve the normalized actions.
    norm_decision = deque(interior_decision[aggregator.name])

    # Then, we scale them up.
    for typ in typologies:
        if len(raw_state["interior"][aggregator.name][typ]) > 0:
            returned_list.append(scale_up_feature(norm_decision.popleft(), raw_state["interior"][aggregator.name][typ]["energy_minimum"], raw_state["interior"][aggregator.name][typ]["energy_maximum"]))

    # Final check
    while len(returned_list) < 3:
            returned_list.append(0.0)
    if len(returned_list) > 3:
        raise Exception("Error in defining the interior actions !")

    return returned_list


def implement_my_exchange_decision(agentID: str, catalog: "Catalog", aggregator: "Aggregator"):
    """
    This function is used inside the top_down_phase method of the gym strategy.
    We use it to scale-up the normalized at and return the dict of Eexch.
    """
    # Initialization
    exchange_dict = {}
    raw_state = catalog.get(f"{agentID}.raw_state")
    exchange_decision = catalog.get(f"{agentID}.exterior_decision")

    # First, we retrieve the normalized actions.
    nb_conversion_actions = 0
    if aggregator.name in raw_state["conversion"]:
        nb_conversion_actions += len(raw_state["conversion"][aggregator.name]["Energy_Conversion"])
    direct_exchanges = []
    conversions = []

    if aggregator.name in exchange_decision:
        if nb_conversion_actions != 0:
            direct_exchanges.extend(exchange_decision[aggregator.name][:-nb_conversion_actions])
            conversions.extend(exchange_decision[aggregator.name][-nb_conversion_actions:])
        else:
            direct_exchanges.extend(exchange_decision[aggregator.name])
        direct_exchanges = deque(direct_exchanges)
        conversions = deque(conversions)

    # Then, we scale-up 'at'.
    if aggregator.name in raw_state["interconnection"]:
        for sub in raw_state["interconnection"][aggregator.name]:
            scaled_up_action = scale_up_feature(direct_exchanges.popleft(), raw_state["interconnection"][aggregator.name][sub]["energy_minimum"], raw_state["interconnection"][aggregator.name][sub]["energy_maximum"])
            exchange_dict = {**exchange_dict, **{tuple([aggregator.name, sub]): scaled_up_action}}
    else:
        for superior in raw_state["interconnection"]:
            if aggregator.name in raw_state["interconnection"][superior]:
                scaled_up_action = scale_up_feature(direct_exchanges.popleft(), raw_state["interconnection"][superior][aggregator.name]["energy_minimum"], raw_state["interconnection"][superior][aggregator.name]["energy_maximum"])
                exchange_dict = {**exchange_dict, **{tuple([superior, aggregator.name]): scaled_up_action}}

    conversion_list = process_conversions(raw_state["conversion"])
    for exchange in conversion_list:
        if aggregator.name in exchange[0]:
            my_index = exchange[0].index(aggregator.name)
            scaled_up_action = scale_up_feature(conversions.popleft(), exchange[1][my_index], exchange[2][my_index])
            exchange_dict = {**exchange_dict, **{tuple(exchange[0]): scaled_up_action}}

    return exchange_dict


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
