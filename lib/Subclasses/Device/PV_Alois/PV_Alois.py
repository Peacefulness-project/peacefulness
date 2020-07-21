# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice
from math import sin, pi, log10


class PV_Alois(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, parameters, filename="lib/Subclasses/Device/PV_Alois/PV_Alois.json"):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name, parameters)

        self._surface = parameters["surface"]
        self._location = parameters["location"]  # the location of the device, in relation with the meteorological data

        # creation of keys for exergy
        self._catalog.add(f"{self.name}_exergy_in", 0)
        self._catalog.add(f"{self.name}_exergy_out", 0)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self):
        self._usage_profile = dict()

        [data_user, data_device] = self._read_consumption_data()  # getting back the profiles

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # usage profile
        self._usage_profile[data_device["usage_profile"]["nature"]] = None

        # panel efficiency
        self._efficiency_pan = data_device["usage_profile"]["efficiency_pan"]

        # kappa
        self._kappa = data_device["usage_profile"]["kappa"]

        # Normal Operating Cell Temperature (NOCT) Temperature

        self._NOCT_temperature = data_device["usage_profile"]["NOCT_temperature"]

        # Normal Operating Cell Temperature (NOCT) Irradiation

        self._NOCT_irradiation = data_device["usage_profile"]["NOCT_irradiation"]

        # gamma

        self._gamma = data_device["usage_profile"]["gamma"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = {nature.name: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self.natures}  # consumption that will be asked eventually

        irradiation = self._catalog.get(f"{self._location}.total_irradiation_value")

        ambient_temperature = self._catalog.get(f"{self._location}.current_outdoor_temperature") + 273.15

        energy_received = self._surface * irradiation / 1000  # as irradiation is in W, it is transformed in kW

        cell_temperature = ambient_temperature + (self._NOCT_temperature - ambient_temperature) * irradiation / self._NOCT_irradiation
        print(cell_temperature)
        if (irradiation > 0):
            efficiency = self._efficiency_pan * (1 - self._kappa * (cell_temperature - self._NOCT_temperature) + self._gamma * log10( irradiation / self._NOCT_irradiation))

        else:
            efficiency = 0

        print(efficiency)

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = - energy_received * efficiency  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = - energy_received * efficiency  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - energy_received * efficiency  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

        exergy_in = list()
        for nature in energy_wanted:
            exergy_in.append(energy_received)
        exergy_in = sum(exergy_in)

        exergy_out = exergy_in * efficiency

        self._catalog.set(f"{self.name}_exergy_in", exergy_in)
        self._catalog.set(f"{self.name}_exergy_out", exergy_out)







