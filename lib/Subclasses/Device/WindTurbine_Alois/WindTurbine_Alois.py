# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice


class WindTurbine_Alois(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib\Subclasses\Device\WindTurbine_Alois\WindTurbine_Alois.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._location = parameters["location"]  # the location of the device, in relation with the meteorological data

        self._rugosity = parameters["rugosity"]  # the resistance of the type of field

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()
        self._efficiency = None

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        self._efficiency = data_device["usage_profile"]["efficiency"]  # efficiency
        self._max_power = data_device["usage_profile"]["max_power"]  # max power
        self._surface = data_device["usage_profile"]["surface"]

        self._U_cut_bot = data_device["usage_profile"]["U_cut_bot"]
        self._U_cut_top = data_device["usage_profile"]["U_cut_top"]
        self._U_nom = data_device["usage_profile"]["U_nom"]

        self._Cp = data_device["usage_profile"]["Cp"]

        self._height = data_device["usage_profile"]["height"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        wind_ref = self._catalog.get(f"{self._location}.wind_value")  # wind speed in m.s-1

        height_ref = self._catalog.get(f"{self._location}.height_ref")

        temperature_ref = self._catalog.get(f"{self._location}.current_outdoor_temperature") + 273.15

        temperature = temperature_ref - 0.0065 * self._height

        pressure = 101325 * (temperature / temperature_ref)**5.259

        air_density = pressure / (temperature * 8.314/(29*10**(-3)))  # air density in kg.m-3

        if self._rugosity == "flat":
            gamma = 0.1
        if self._rugosity == "trees":
            gamma = 0.25

        wind = wind_ref * (self._height / height_ref)**gamma

        if (wind <= self._U_cut_bot) or (wind >= self._U_cut_top):
            energy_received = 0

        elif (wind > self._U_cut_bot) and (wind <= self._U_nom):
            energy_received = 1/2 * air_density * self._Cp * self._surface * wind**3 * self._efficiency * (wind**3 - self._U_cut_bot**3)/(self._U_nom**3 - self._U_cut_bot**3) / 1000

        elif (wind > self._U_nom) and (wind <= self._U_cut_top):
            energy_received = 1 / 2 * air_density * self._Cp * self._surface * wind ** 3 * self._efficiency / 1000

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - min(energy_received, self._max_power)  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


