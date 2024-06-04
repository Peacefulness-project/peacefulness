# In this file, we define a utility method to extract the information message from all the devices under an aggregator.
# We assume that devices are only visible to the aggregator which is directly managing them.
# As such, a superior aggregator is blind towards the devices managed by its subaggregators.
# We also extract the forecasting predictions of each subaggregator.

# Imports
from src.common.Aggregator import Aggregator


def my_devices(aggregator: "Aggregator"):
    """
    This method is used under the assumption that the devices managed by subaggregators aren't directly controlled by the superior aggregator.
    """
    prediction_message = []
    prediction_message.append({aggregator.name: aggregator.strategy.call_to_forecast()})  # the prediction message

    formalism_message = [{}]
    for device in aggregator.devices:
        formalism_message.append(device._create_message())  # the formalism message

    subaggregator_list = aggregator.subaggregators
    for subaggregator in subaggregator_list:
        my_devices(subaggregator)  # recursion

    return formalism_message, prediction_message
