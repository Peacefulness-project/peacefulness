# This subclass of Converter is supposed to represent a heat pump. Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter
from math import log


class AdvancedHeatPump(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregator, profiles, parameters=None, filename="lib/Subclasses/Device/AdvancedHeatPump/AdvancedHeatPump.json"):
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

        self._network_temperature = data_device["network_temperature"]  # °C
        self._isentropic_efficiency = data_device["isentropic_efficiency"]  # -, the isentropic efficiency of the converter for each nature of energy

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    @property
    def _instant_efficiency(self):
        outdoor_temperature = self._catalog.get(f"{self._outdoor_location}.current_outdoor_temperature")
        return self._isentropic_efficiency * (self._network_temperature + 273.15) / (self._network_temperature - outdoor_temperature)
