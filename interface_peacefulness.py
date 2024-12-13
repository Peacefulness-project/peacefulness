# In this file, we will link peacefulness data to the Actor-Critic code

# Ascending phase :
# - from devices we should export the message which contains the formalism
# - from devices we should also export the wanted energy resulting from the device.update() method
# - from aggregators we should export the forecasting results through the forecaster.update_forecast() method


# Descending phase :
# - we should import the accorded energy to each device

# Sending the results of each observation

# Imports
from src.tools.DRL_Strategy_utilities import *
from os import path
import sys

sys.path.append(path.abspath("C:/Users/y23hallo/PycharmProjects/Management_Strategy"))

# from support.Methodes.a3c import A3C_agent


def updating_grid_state(catalog: "Catalog", agent: "A3C_agent"):
    """
    This method is used to communicate the information message to the A-C method.
    """
    formalism_message = {}  # here we retrieve the values of the formalism variables
    prediction_message = {}  # here we retrieve the predictions on rigid energy consumption and production
    prices = {}  # here we retrieve the values of energy prices
    conversions = {}
    direct_exchanges = {}

    # Getting the state of the multi-energy grid
    for aggregator in catalog.get(f"DRL_Strategy.strategy_scope"):
        formalism_message[aggregator.name] = catalog.get(f"{aggregator.name}.DRL_Strategy.formalism_message")
        # aggregator = catalog.aggregators[aggregator_name]
        if aggregator.forecaster:
            prediction_message[aggregator.name] = catalog.get(f"{aggregator.name}.DRL_Strategy.forecasting_message")
        prices[aggregator.name] = catalog.get(f"{aggregator.name}.DRL_Strategy.energy_prices")
        conversions[aggregator.name] = catalog.get(f"{aggregator.name}.DRL_Strategy.converter_message")  # todo rajouter la possibilité de vérifier si le systeme de conversion est deja pris en compte ou non
        if aggregator.subaggregators:  # todo pareil, il faut vérifier si on remonte l'info une seule fois
            direct_exchanges[aggregator.name] = catalog.get(f"{aggregator.name}.DRL_Strategy.direct_energy_exchanges")
        if aggregator.superior:  # todo pareil, il faut vérifier si on remonte l'info une seule fois
            direct_exchanges[aggregator.superior.name] = catalog.get(f"{aggregator.name}.DRL_Strategy.direct_energy_exchanges")
        # print(formalism_message)
        # print(prediction_message)
        # print(prices)
        # print(direct_exchanges)
        # print(conversions)
    # To be noted, that the topology of energy exchanges within the MEG is already determined
    current_time = catalog.get("simulation_time")
    last_time = catalog.get("time_limit")
    relevant_time = [last_time, current_time]
    # print(f"i am the current time: {my_current_time}")
    # print(f"\ni am the formalism message during the ascending interface/call to DRL_Strategy: {formalism_message}")
    # print(f"\ni am the prediction message during the ascending interface/call to DRL_Strategy: {prediction_message}")
    # print(f"\ni am the prices message during the ascending interface/call to DRL_Strategy: {prices}")
    # print(f"\ni am the direct energy exchanges message during the ascending interface/call to DRL_Strategy: {direct_exchanges}")
    # print(f"\ni am the energy exchanges through conversion systems message during the ascending interface/call to DRL_Strategy: {conversions}")
    agent.update_state(relevant_time, formalism_message, prediction_message, prices, direct_exchanges, conversions)


def getting_agent_decision(catalog: "Catalog", agent: "A3C_agent"):
    """
    This method is used to retrieve the energy dispatch decision from the A-C method.
    """
    aggregator_list = []
    for aggregator in catalog.get(f"DRL_Strategy.strategy_scope"):
        aggregator_list.append(aggregator.name)

    device_dict = catalog.devices
    decision = agent.act(device_dict)

    # Translating the RL agent actions into a decision that can be understood by Peacefulness (a dict format)
    decision_message, exchanges_message = from_tensor_to_dict(decision, aggregator_list, agent)
    # print(f"I am the decisions of what happens inside during the descending interface/call from DRL_Strategy : {decision_message}")
    # print(f"I am the decisions related to the outside during the descending interface/call from DRL_Strategy : {exchanges_message}")
    # Storing the RL agent decision in the world's catalog
    if f"DRL_Strategy.decision_message" not in catalog.keys:
        catalog.add(f"DRL_Strategy.decision_message", decision_message)
    else:
        catalog.set(f"DRL_Strategy.decision_message", decision_message)
    if f"DRL_Strategy.exchanges_message" not in catalog.keys:
        catalog.add(f"DRL_Strategy.exchanges_message", exchanges_message)
    else:
        catalog.set(f"DRL_Strategy.exchanges_message", exchanges_message)
