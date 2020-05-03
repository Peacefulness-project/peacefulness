# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice


class WindTurbine(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, parameters):
        super().__init__(name, contracts, agent, aggregators, "lib/Subclasses/Device/WindTurbine/WindTurbine.json", user_profile_name, usage_profile_name, parameters)

        self._location = parameters["location"]  # the location of the device, in relation with the meteorological data

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        pass

    def _read_data_profiles(self):
        self._usage_profile = dict()
        self._efficiency = None

        [data_user, data_device] = self._read_consumption_data()  # getting back the profiles

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # usage profile
        self._usage_profile[data_device["usage_profile"]["nature"]] = None

        self._efficiency = data_device["usage_profile"]["efficiency"]  # efficiency
        self._max_power = data_device["usage_profile"]["max_power"]  # max power
        self._surface = data_device["usage_profile"]["surface"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = {nature.name: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self.natures}  # consumption that will be asked eventually

        wind = self._catalog.get(f"{self._location}.wind_value")  # wind speed in m.s-1
        air_density = 1.17  # air density in kg.m-3

        energy_received = 1/2 * air_density * self._surface * wind**3 / 1000  # power received in kw

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - min(energy_received * self._efficiency, self._max_power)  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


