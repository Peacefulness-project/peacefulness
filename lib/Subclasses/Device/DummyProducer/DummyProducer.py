# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice


class DummyProducer(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, filename="lib/Subclasses/Device/DummyProducer/DummyProducer.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()
        self._efficiency = None

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        self._max_power = data_device["usage_profile"]["max_power"]  # max power

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - self._max_power  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


