# This subclass of Converter is supposed to represent a heat pump. Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter
from numpy import interp


class ModifiedHeatPump(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregator, profiles, parameters=None, filename="lib/Subclasses/Device/ModifiedHeatPump/ModifiedHeatPump.json"):
        super().__init__(name, contracts, agent, filename, upstream_aggregator, downstream_aggregator, profiles, parameters)

        outdoor_temperature_daemon = self._catalog.daemons[parameters["outdoor_temperature_daemon"]]
        self._outdoor_location = outdoor_temperature_daemon.location  # the location of the device, in relation with the meteorological data
        ground_temperature_daemon = self._catalog.daemons[parameters["ground_temperature_daemon"]]
        self._ground_location = ground_temperature_daemon.location  # the location of the device, in relation with the meteorological data
        # self._elec_capacity = parameters["capacity"]  # kW
        self._efficiency = {"LVE": 1, "LTH": self._instant_efficiency}
        self._catalog.set(f"{self.name}.LTH.efficiency", self._instant_efficiency)


    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._source = data_device["Source"]
        self._working_temp_range = data_device["Temperature_range"]
        self._reference_cop = data_device["COP"]

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    @property
    def _instant_efficiency(self):
        if self._source == "Air":
            outdoor_temperature = self._catalog.get(f"{self._outdoor_location}.current_outdoor_temperature")
            efficiency = interp(outdoor_temperature, self._working_temp_range, self._reference_cop)
        else:
            ground_temperature = self._catalog.get(f"{self._ground_location}.ground_temperature")
            efficiency = interp(ground_temperature, self._working_temp_range, self._reference_cop)
        return efficiency

    def update(self):
        self._efficiency = {"LVE": 1, "LTH": self._instant_efficiency}
        super().update()

