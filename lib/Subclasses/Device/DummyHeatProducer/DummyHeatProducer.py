# Imports
from src.common.DeviceMainClasses import NonControllableDevice


class DummyHeatProducer(NonControllableDevice):
    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/DummyHeatProducer/DummyHeatProducer.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step  # the maximum power this device can produce
        self._catalog.add(f"{self.name}.heat_dissipated", None)  # heat dissipated through the by-pass valve to the ambiance

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()
        self._efficiency = None

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        # time_step = self._catalog.get("time_step")
        # self._max_power = data_device["usage_profile"]["max_power"] * time_step  # max power

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - self._max_power  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog
        self._catalog.set(f"{self.name}.heat_dissipated", 0.0)

    def react(self):
        super().react()
        for nature in self.natures:
            energy_wanted = self.get_energy_wanted(nature)
            energy_accorded = self.get_energy_accorded(nature)
            self._catalog.set(f"{self.name}.heat_dissipated", abs(energy_wanted["energy_maximum"]) - abs(energy_accorded["quantity"]))

