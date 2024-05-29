# this _forecaster knows
# it creates noise around the real value according to a function (in argment) for n tm steps (in argument too)
from src.common.Forecaster import *  # brings also some elements from the "typing" module
from src.common.World import World

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


class BasicForecaster(Forecaster):
    def __init__(self, name: str, aggregator: "Aggregator", noise_function: Callable, forecast_depth: int):
        self._name = name
        self._aggregator = aggregator

        world = World.ref_world  # get automatically the world defined for this case
        self._catalog = world.catalog  # the catalog in which some data are stored
        world.register_forecaster(self)  # register the _forecaster into world dedicated dictionary

        self._noise_function = noise_function
        self._depth = forecast_depth

        self._description_treatment_typed_functions = {
                                                       "background": self._background_forecast_modeling,
                                                       "dam": self._dam_forecast_modeling,
                                                       "PV": self._PV_forecast_modeling,
                                                       "WT": self._WT_forecast_modeling,
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
            device_description = device.description(self.aggregator.nature.name)
            if device_description:  # non-forecastable devices return None, enabling to discard them
                device_type = device_description["type"]
                predictions_functions_list.append(self._description_treatment_typed_functions[device_type](device_description))  # treatment adapted to the device type

        def noised_predictor(t: int):
            # very precise prediction
            precise_prediction = {"consumption": [0 for _ in range(self._depth)],
                                  "production": [0 for _ in range(self._depth)]}
            for prediction_function in predictions_functions_list:
                precise_prediction = prediction_function(precise_prediction, t)

            # addition of noise
            prediction = empty_prediction
            for i in range(self._depth):
                prediction["rigid_consumption"] = self._noise_function(precise_prediction["consumption"][i], i)
                prediction["rigid_production"] = self._noise_function(precise_prediction["production"][i], i)

            return prediction

        return noised_predictor

    # ##########################################################################################
    # specific treatment for each device type

    # ##########################################################################################
    # consumption

    def _background_forecast_modeling(self, description: Dict):
        technical_profile = description["technical_profile"]
        moment = description["moment"]

        def background_predictor(prediction: Dict) -> Dict:
            consumption_prediction = prediction["consumption"]
            for i in range(len(prediction)):
                consumption_prediction[i] += technical_profile[moment]
            prediction["consumption"] = consumption_prediction

            return prediction

        return background_predictor

    # ##########################################################################################
    # production

    def _dam_forecast_modeling(self, description: Dict):
        water_density = 1
        max_power = description["max_power"]
        location = description["location"]
        max_efficiency = description["max_efficiency"]
        relative_efficiency = description["relative_efficiency"]
        relative_min_flow = description["relative_min_flow"]
        height = description["height"]

        reserved_flow = self._catalog.get(f"{location}.reserved_flow")
        max_flow = self._catalog.get(f"{location}.max_flow") * (1 - reserved_flow)

        def dam_predictor(prediction: Dict) -> Dict:
            production_prediction = prediction["production"]
            flows = self.catalog.get(f"consult_function.WaterFlowDaemon.{location}")(self._depth)["flow"]
            for i in range(len(production_prediction)):
                # finding the adapted efficiency
                power_available = flows[i] * water_density * height * 9.81 / 1000
                j = 0
                while power_available / max_power > relative_min_flow[j] and j < len(relative_min_flow)-1:
                    j += 1
                coeff_efficiency = relative_efficiency[j]
                efficiency = max_efficiency * coeff_efficiency

                if flows > relative_min_flow * max_flow:
                    energy_received = water_density * 9.81 * flows * height / 1000  # conversion of water flow, in m3.s-1, to kWh
                else:
                    energy_received = 0
                production_prediction[i] += min(max_power, energy_received * efficiency)
            prediction["production"] = production_prediction

            return prediction

        return dam_predictor

    def _PV_forecast_modeling(self, description: Dict):
        surface = description["surface"]
        location = description["location"]
        efficiency = description["efficiency"]

        def PV_predictor(prediction: Dict) -> Dict:
            production_prediction = prediction["production"]
            irradiation = self.catalog.get(f"consult_function.IrradiationDaemon.{location}")(self._depth)["total_irradiation_value"]
            for i in range(len(production_prediction)):
                energy_received = surface * irradiation / 1000  # as irradiation is in W, it is transformed in kW
                production_prediction[i] += energy_received * efficiency
            prediction["production"] = production_prediction
            return production_prediction

        return PV_predictor

    def _ST_forecast_modelling(self, description: Dict):
        surface = description["surface"]
        location = description["location"]
        fluid_temperature = description["fluid_temperature"]
        a0 = description["a0"]
        a1 = description["a1"]
        a2 = description["a2"]

        def ST_predictor(prediction: Dict) -> Dict:
            production_prediction = prediction["production"]
            irradiation = self._catalog.get(f"consult_function.IrradiationDaemon.{location}")(self._depth)["total_irradiation_value"]
            temperature = self._catalog.get(f"consult_function.OutdoorTemperatureDaemon.{location}")(self._depth)["current_outdoor_temperature"]
            for i in range(len(production_prediction)):
                efficiency = max(a0 * irradiation - a1 / (fluid_temperature - temperature) - a2 / (fluid_temperature - temperature) ** 2, 0) / 1000  # the efficiency cannot be negative
                energy_received = surface * irradiation
                production_prediction[i] += energy_received * efficiency  # energy needed for all natures used by the device
            prediction["production"] = production_prediction

            return production_prediction

        return ST_predictor

    def _WT_forecast_modeling(self, description: Dict):
        air_density = 1.17  # air density in kg.m-3
        surface = description["surface"]
        location = description["location"]
        efficiency = description["efficiency"]
        max_power = description["max_power"]

        def WT_predictor(prediction: Dict) -> Dict:
            production_prediction = prediction["production"]
            wind = self.catalog.get(f"consult_function.WinsSpeedDaemon.{location}")(self._depth)  # wind speed in m.s-1
            for i in range(len(production_prediction)):
                energy_received = 1 / 2 * air_density * surface * wind[i] ** 3 / 1000  # power received in kw
                production_prediction[i] += min(energy_received * efficiency, max_power)
            prediction["production"] = production_prediction
            return production_prediction

        return WT_predictor






