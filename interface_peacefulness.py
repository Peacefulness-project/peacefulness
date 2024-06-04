# In this file, we will link peacefulness data to the Actor-Critic code

# Ascending phase :
# - from devices we should export the message which contains the formalism
# - from devices we should also export the wanted energy resulting from the device.update() method
# - from aggregators we should export the forecasting results through the forecaster.update_forecast() method


# Descending phase :
# - we should import the accorded energy to each device

# Imports
from src.common.World import World
from src.tools.all_devices import *
import sys


def ascending_interface(world: "World"):
    """
    This recursive method is used to communicate the information message to the A-C method.
    """
    prices = {}
    formalism_message = {}
    prediction_message = {}

    independent_aggregators = world._identify_independent_aggregators()

    for aggregator in independent_aggregators:
        # Getting the formalism message from the devices directly managed by the aggregator
        formalism_message[aggregator.name], prediction_message[aggregator.name] = my_devices(aggregator)

        # Getting the price information
        prices[aggregator.name] = aggregator.strategy._limit_prices()

    # Sending the information message to the method
    path_to_interface = "C:/Users/y23hallo/PycharmProjects/Management_Strategy/Peacefulness_cases/Utilities/strategy_interface.py"
    pass_state = open(path_to_interface).read()
    sys.argv = ["pass_state", formalism_message, prediction_message, prices]
    exec(pass_state)


def exogen_instruction(world: "World"):
    """
    Here we define the instructions to World.
    """


