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


def ascending_interface(catalog: "Catalog", agent: "A3C_agent"):
    """
    This method is used to communicate the information message to the A-C method.
    """
    formalism_message = {}  # here we retrieve the values of the formalism variables
    prediction_message = {}  # here we retrieve the predictions on rigid energy consumption and production
    prices = {}  # here we retrieve the values of energy prices
    conversions = {}
    direct_exchanges = {}

    # Getting the state of the multi-energy grid
    for aggregator_name in catalog.aggregators.keys():
        formalism_message[aggregator_name] = catalog.get(f"{aggregator_name}.DRL_Strategy.formalism_message")
        aggregator = catalog.aggregators[aggregator_name]
        if aggregator.forecaster:
            prediction_message[aggregator_name] = catalog.get(f"{aggregator_name}.DRL_Strategy.forecasting_message")
        prices[aggregator_name] = catalog.get(f"{aggregator_name}.DRL_Strategy.energy_prices")
        conversions[aggregator_name] = catalog.get(f"{aggregator_name}.DRL_Strategy.converter_message")
        if aggregator.subaggregators:
            direct_exchanges[aggregator_name] = catalog.get(f"{aggregator_name}.DRL_Strategy.direct_energy_exchanges")
        print(f"working atleast for the first aggregator,aka: {aggregator_name}")

    # To be noted, that the topology of energy exchanges within the MEG is already determined
    agent.update_state(formalism_message, prediction_message, prices, direct_exchanges, conversions)


def descending_interface(catalog: "Catalog", agent: "A3C_agent"):
    """
    This method is used to retrieve the energy dispatch decision from the A-C method.
    """
    aggregator_list = []
    for aggregator_name in catalog.aggregators.keys():
        aggregator_list.append(aggregator_name)

    decision = agent.act()  # TODO il faut s'assurer qu'il s'agit bien d'un vecteur/tenseur numpy

    # Translating the RL agent actions into a decision that can be understood by Peacefulness (a dict format)
    decision_message = from_tensor_to_dict(decision, aggregator_list, agent)
    # Storing the RL agent decision in the world's catalog
    if f"DRL_Strategy.decision_message" not in catalog.keys:
        catalog.add(f"DRL_Strategy.decision_message", decision_message)
    else:
        catalog.set(f"DRL_Strategy.decision_message", decision_message)
    print(f"depuis la descending interface, decision: {catalog.get('DRL_Strategy.decision_message')}")
