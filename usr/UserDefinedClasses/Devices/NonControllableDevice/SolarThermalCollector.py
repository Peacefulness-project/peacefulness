# A device representing solar thermal collectors
from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class SolarThermalCollector(NonControllableDevice):

    def __init__(self, name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters):
        super().__init__(name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters)

        self._a0 = parameters["a0"]
        self._a1 = parameters["a1"]
        self._a2 = parameters["a2"]
        self._fluid_temperature = parameters["fluid_temperature"]

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self._usage_profile}  # consumption that will be asked eventually

        irradiation = self._catalog.get("irradiation_value")
        temperature = self._catalog.get("current_outdoor_temperature")

        energy_produced = self._a0 - self._a1 / irradiation * (self._fluid_temperature - temperature) - self._a2 / irradiation * (self._fluid_temperature - temperature) ** 2

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_nominal"] = energy_produced  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_maximum"] = energy_produced  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


user_classes_dictionary[f"{SolarThermalCollector.__name__}"] = SolarThermalCollector
