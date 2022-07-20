# This subclass of device represent electrochemical batteries
from src.common.DeviceMainClasses import Storage


class ElectricalBattery(Storage):

    def __init__(self, name, contracts, agent, aggregator, profiles, parameters, filename="lib/Subclasses/Device/ElectricalBattery/ElectricalBattery.json"):
        super().__init__(name, contracts, agent, filename, aggregator, profiles, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profile):
        super()._read_data_profiles(profile)
        time_step = self._catalog.get("time_step")
        data_device = self._read_technical_data(profile["device"])  # parsing the data

        self._degradation_rate = (1 - data_device["degradation_rate"]) ** time_step

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _degradation_of_energy_stored(self):  # a class-specific function reducing the energy stored over time
        energy_stored = self._catalog.get(f"{self.name}.energy_stored")
        energy_stored = energy_stored * self._degradation_rate

        return energy_stored


