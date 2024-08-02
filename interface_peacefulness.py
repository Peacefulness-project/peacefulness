# In this file, we will link peacefulness data to the Actor-Critic code

# Ascending phase :
# - from devices we should export the message which contains the formalism
# - from devices we should also export the wanted energy resulting from the device.update() method
# - from aggregators we should export the forecasting results through the forecaster.update_forecast() method


# Descending phase :
# - we should import the accorded energy to each device

# Sending the results of each observation

# Imports
from src.common.World import World
from src.tools.DRL_Strategy_utilities import *
from os import path
import sys

sys.path.append(path.abspath("C:/Users/y23hallo/PycharmProjects/Management_Strategy"))

# from support.Methodes.a3c import A3C_agent


def ascending_interface(world: "World", agent: "A3C_agent"):
    """
    This method is used to communicate the information message to the A-C method.
    """
    formalism_message = {}  # here we retrieve the values of the formalism variables
    prediction_message = {}  # here we retrieve the predictions on rigid energy consumption and production
    prices = {}  # here we retrieve the values of energy prices
    conversions = {}
    direct_exchanges = {}

    # Getting the state of the multi-energy grid
    for aggregator_name in world.catalog.aggregators.keys():
        formalism_message[aggregator_name] = world.catalog.get(f"{aggregator_name}.DRL_Strategy.formalism_message")
        prediction_message[aggregator_name] = world.catalog.get(f"{aggregator_name}.DRL_Strategy.forecasting_message")
        prices[aggregator_name] = world.catalog.get(f"{aggregator_name}.DRL_Strategy.energy_prices")
        conversions[aggregator_name] = world.catalog.get(f"{aggregator_name}.DRL_Strategy.converter_message")
        direct_exchanges[aggregator_name] = world.catalog.get(f"{aggregator_name}.DRL_Strategy.direct_energy_exchanges")

    # To be noted, that the topology of energy exchanges within the MEG is already determined
    agent.update_state(formalism_message, prediction_message, prices, direct_exchanges, conversions)


def descending_interface(world: "World", agent: "A3C_agent"):
    """
    This method is used to retrieve the energy dispatch decision from the A-C method.
    """
    aggregator_list = []
    for aggregator_name in world.catalog.aggregators.keys():
        aggregator_list.append(aggregator_name)

    decision = agent.act()  # TODO il faut s'assurer qu'il s'agit bien d'un vecteur/tenseur numpy

    # Translating the RL agent actions into a decision that can be understood by Peacefulness (a dict format)
    decision_message = from_tensor_to_dict(decision, aggregator_list, agent)
    # Storing the RL agent decision in the world's catalog
    world.catalog.add(f"DRL_Strategy.decision_message", decision_message)
