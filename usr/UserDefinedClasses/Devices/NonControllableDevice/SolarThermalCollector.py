# A device representing solar thermal collectors
from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class SolarThermalCollector(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/SolarThermalCollector.json", user_profile_name, usage_profile_name)

        self._a0 = None
        self._a1 = None
        self._a2 = None
        self._fluid_temperature = None

        self._location = None

    def _user_register(self):
        self._catalog.add(f"{self.name}_exergy", 0)

    def _get_consumption(self):
        [data_user, data_device] = self._read_consumption_data()  # getting back the profiles

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # usage profile
        self._a0 = data_device["usage_profile"]["a0"]
        self._a1 = data_device["usage_profile"]["a1"]
        self._a2 = data_device["usage_profile"]["a2"]
        self._fluid_temperature = data_device["fluid_temperature"]

        # location
        self._location = data_user["location"]

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = {nature.name: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self.natures}  # consumption that will be asked eventually

        irradiation = self._catalog.get(f"{self._location}_irradiation_value")
        temperature = self._catalog.get("current_outdoor_temperature")

        energy_produced = self._a0 * irradiation - self._a1 * (self._fluid_temperature - temperature) - self._a2 * (self._fluid_temperature - temperature) ** 2

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_nominal"] = energy_produced  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_maximum"] = energy_produced  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

        self._catalog.get("reference_temperature")


user_classes_dictionary[f"{SolarThermalCollector.__name__}"] = SolarThermalCollector
