# A device representing solar thermal collectors
from src.common.DeviceMainClasses import NonControllableDevice


class SolarThermalCollector(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, parameters):
        super().__init__(name, contracts, agent, aggregators, "lib/Subclasses/Device/SolarThermalCollector/SolarThermalCollector.json", user_profile_name, usage_profile_name, parameters)

        self._a0 = None
        self._a1 = None
        self._a2 = None
        self._fluid_temperature = None

        self._location = None

        self._usage_profile = dict()

        self._surface = parameters["surface"]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        self._catalog.add(f"{self.name}_exergy_in", 0)
        self._catalog.add(f"{self.name}_exergy_out", 0)

    def _get_consumption(self):
        [data_user, data_device] = self._read_consumption_data()  # getting back the profiles

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # usage profile
        self._usage_profile[data_device["usage_profile"]["nature"]] = None
        self._a0 = data_device["usage_profile"]["a0"]
        self._a1 = data_device["usage_profile"]["a1"]
        self._a2 = data_device["usage_profile"]["a2"]
        self._fluid_temperature = data_device["fluid_temperature"]

        # location
        self._location = data_user["location"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = {nature.name: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self.natures}  # consumption that will be asked eventually

        irradiation = self._catalog.get(f"{self._location}_irradiation_value") / 1000  # the value is divided by 1000 to transfrom w into kW
        temperature = self._catalog.get("current_outdoor_temperature")

        efficiency = max(self._a0 * irradiation - self._a1 / (self._fluid_temperature - temperature) - self._a2 / (self._fluid_temperature - temperature) ** 2, 0)  # the efficiency cannot be negative

        energy_received = self._surface * irradiation

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = - energy_received * efficiency  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_nominal"] = - energy_received * efficiency  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_maximum"] = - energy_received * efficiency  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

        reference_temperature = self._catalog.get("reference_temperature")

        exergy_in = list()
        for nature in energy_wanted:
            exergy_in.append(energy_received * (1 - reference_temperature/self._fluid_temperature))
        exergy_in = sum(exergy_in)

        exergy_out = exergy_in * efficiency

        self._catalog.set(f"{self.name}_exergy_in", exergy_in)
        self._catalog.set(f"{self.name}_exergy_out", exergy_out)


