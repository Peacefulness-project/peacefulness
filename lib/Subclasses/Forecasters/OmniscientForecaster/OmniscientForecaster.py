# this forecaster knows
# it creates noise around the real value according to a function (in argment) for n tm steps (in argument too)
from datetime import timedelta
from typing import Callable, Dict

from src.common.Forecaster import *

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


class OmniscientForecaster(Forecaster):
    def __init__(self, name: str, aggregator: "Aggregator", noise_function: Callable, forecast_depth: timedelta):
        self._name = name
        self._aggregator = aggregator

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # the catalog in which some data are stored
        world.register_forecaster(self)  # register the forecaster into world dedicated dictionary

        self._noise_function = noise_function
        self._depth = forecast_depth

        self._description_treatment_typed_functions = {
                                                       "background": self.background_forecast_modeling,
                                                       "dam": self.dam_forecast_modeling,
                                                       "PV": self.PV_forecast_modeling,
                                                       "WT": self.WT_forecast_modeling,
                                                       }
        self._create_predictions = self._build_aggregator_description()

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _build_aggregator_description(self) -> Callable:  # collect the information necessary from the aggregator and create the forecasting function accordingly
        predictions_functions_list = []  # list of functions called to build a full prediction
        # these functions complete incrementally the 2 fields of predictions

        for device_name in self.aggregator.devices:
            device = self._catalog.devices[device_name]
            device_description = device.description
            if device_description:  # non-forecastable devices return None, enabling to discard them
                device_type = device_description["type"]
                predictions_functions_list.append(self._description_treatment_typed_functions[device_type](device_description))  # treatment adapted to the device type

        def omniscient_noised_predictor(t: int):

            prediction = empty_prediction
            for prediction_function in predictions_functions_list:
                prediction = prediction_function(prediction, t)
            self._noise_function(prediction)

            return prediction

        return omniscient_noised_predictor

    # ##########################################################################################
    # specific treatment for each device type
    def background_forecast_modeling(self):
        pass

    def dam_forecast_modeling(self, description: dict):
        water_density = 1

        def dam_prediction(global_predicition: Dict, t: int):
            reserved_flow = self._catalog.get(f"{description['location']}.reserved_flow")
            flow = self._catalog.get(f"{description['location']}.flow_value") * (1 - reserved_flow)
            max_flow = self._catalog.get(f"{description['location']}.max_flow") * (1 - reserved_flow)

            # finding the adapted efficiency
            power_available = flow * water_density * description["height"] * 9.81 / 1000
            i = 0
            # print(power_available / description._max_power)
            while power_available / description["max_power"] > description._relative_flow[i] and i < len(description._relative_flow)-1:
                i += 1
                # print(i, description._relative_flow[i])
            coeff_efficiency = description._relative_efficiency[i]

            efficiency = description._max_efficiency * coeff_efficiency

            if flow > description._relative_min_flow * max_flow:
                energy_received = water_density * 9.81 * flow * description._height / 1000  # conversion of water flow, in m3.s-1, to kWh
            else:
                energy_received = 0

            rigid_production = global_predicition["rigid_production"]["low_estimation"]

            - min(description._max_power, energy_received * efficiency)

            return global_predicition

        return dam_prediction


    def PV_forecast_modeling(self, description: dict, t: int):
        irradiation = description._catalog.get(f"{description._location}.total_irradiation_value")

        energy_received = description._surface_panel * description._panels * irradiation / 1000  # as irradiation is in W, it is transformed in kW

        - energy_received * description._efficiency


    def WT_forecast_modeling(self, description: dict, t: int):
        wind = description._catalog.get(f"{description._location}.wind_value")  # wind speed in m.s-1
        air_density = 1.17  # air density in kg.m-3

        energy_received = 1 / 2 * air_density * description._surface * wind ** 3 / 1000  # power received in kw
        - min(energy_received * description._efficiency, description._max_power)






