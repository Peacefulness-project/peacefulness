# the mother class of forecasters, objects giving clues to strategies on what will happen next
from typing import Callable, List, Dict

from src.tools.GlobalWorld import get_world

empty_prediction = {
    "rigid_consumption": {
        "low_estimation": [],
        "high_estimation": [],
        "confidence_level": []
    },
    "rigid_production": {
        "low_estimation": [],
        "high_estimation": [],
        "confidence_level": []
    }
}


class Forecaster:
    def __init__(self, name: str, aggregator: "Aggregator", data_daemon_list: List["DataReadingDaemon"]):
        self._name = name
        self._aggregator = aggregator
        self._daemons = data_daemon_list

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # the catalog in which some data are stored

        self._create_predictions = self._build_aggregator_description()

        world.register_forecaster(self)  # register the _forecaster into world dedicated dictionary

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _build_aggregator_description(self) -> Callable:  # collect the information necessary from the aggregator and create the forecasting function accordingly
        def dummy_predictions():
            return empty_prediction

        return dummy_predictions

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update_forecast(self, t: int):  # return actualised predictios when called
        predictions = self._create_predictions()

        return predictions

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def name(self):
        return self._name

    @property
    def catalog(self):
        return self._catalog

    @property
    def aggregator(self):
        return self._aggregator

