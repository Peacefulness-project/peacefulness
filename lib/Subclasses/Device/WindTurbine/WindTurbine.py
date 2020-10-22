# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice


class WindTurbine(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/WindTurbine/WindTurbine.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        wind_speed_daemon = self._catalog.daemons[parameters["wind_speed_daemon"]]
        self._location = wind_speed_daemon.location  # the location of the device, in relation with the meteorological data

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()
        self._efficiency = None

        # usage profile
        time_step = self._catalog.get("time_step")
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        self._efficiency = data_device["usage_profile"]["efficiency"]  # efficiency
        self._max_power = data_device["usage_profile"]["max_power"] * time_step  # max power
        self._surface = data_device["usage_profile"]["surface"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        wind = self._catalog.get(f"{self._location}.wind_value")  # wind speed in m.s-1
        air_density = 1.17  # air density in kg.m-3

        energy_received = 1/2 * air_density * self._surface * wind**3 / 1000  # power received in kw

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - min(energy_received * self._efficiency, self._max_power)  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


