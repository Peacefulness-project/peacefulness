# A device representing solar thermal collectors
from src.common.DeviceMainClasses import NonControllableDevice


class SolarThermalCollector(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, technical_profile, parameters, filename="lib/Subclasses/Device/SolarThermalCollector/SolarThermalCollector.json"):
        super().__init__(name, contracts, agent, aggregators, filename, None, technical_profile, parameters)

        self._catalog.add(f"{self.name}_exergy_in", 0)
        self._catalog.add(f"{self.name}_exergy_out", 0)

        self._location = parameters["location"]  # the location of the device, in relation with the meteorological data
        self._panels = parameters["panels"]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, user_profile, technical_profile):
        data_device = self._read_technical_data(technical_profile)  # parsing the data

        self._technical_profile = dict()

        # panels surface
        self._surface_pan = data_device["usage_profile"]["surface_pan"]

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None
        self._a0 = data_device["usage_profile"]["a0"]
        self._a1 = data_device["usage_profile"]["a1"]
        self._a2 = data_device["usage_profile"]["a2"]
        self._fluid_temperature = data_device["fluid_temperature"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        irradiation = self._catalog.get(f"{self._location}.direct_normal_irradiation_value") / 1000  # the value is divided by 1000 to transfrom w into kW
        temperature = self._catalog.get(f"{self._location}.current_outdoor_temperature")

        efficiency = max(self._a0 * irradiation - self._a1 / (self._fluid_temperature - temperature) - self._a2 / (self._fluid_temperature - temperature) ** 2, 0)  # the efficiency cannot be negative

        energy_received = self._panels * self._surface_pan * irradiation

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = - energy_received * efficiency  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_nominal"] = - energy_received * efficiency  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_maximum"] = - energy_received * efficiency  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

        reference_temperature = self._catalog.get(f"{self._location}.reference_temperature")

        exergy_in = list()
        for nature in energy_wanted:
            exergy_in.append(energy_received * (1 - reference_temperature/self._fluid_temperature))
        exergy_in = sum(exergy_in)

        exergy_out = exergy_in * efficiency

        self._catalog.set(f"{self.name}_exergy_in", exergy_in)
        self._catalog.set(f"{self.name}_exergy_out", exergy_out)


