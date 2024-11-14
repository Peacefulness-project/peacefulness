# This subclass of device represent sensible heat storage
# Current packages
from src.common.DeviceMainClasses import Storage


class LatentHeatStorage(Storage):

    def __init__(self, name, contracts, agent, aggregator, profiles, parameters, filename="lib/Subclasses/Device/LatentHeatStorage/LatentHeatStorage.json"):
        parameters["capacity"] = 0
        parameters["initial_SOC"] = 0
        self._initial_temperature = parameters["initial_temperature"]
        super().__init__(name, contracts, agent, filename, aggregator, profiles, parameters)

        temperature_daemon = self._catalog.daemons[parameters["outdoor_temperature_daemon"]]
        self._location = temperature_daemon.location  # the location of the device, in relation with the meteorological data

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profile):
        time_step = self._catalog.get("time_step")
        data_device = self._read_technical_data(profile["device"])  # parsing the data

        # randomization
        self._randomize_multiplication(data_device["charge"]["efficiency"], data_device["efficiency_variation"])
        self._randomize_multiplication(data_device["discharge"]["efficiency"], data_device["efficiency_variation"])
        self._randomize_multiplication(data_device["charge"]["power"], data_device["power_variation"])
        self._randomize_multiplication(data_device["discharge"]["power"], data_device["power_variation"])
        self._randomize_multiplication(data_device["volume"], data_device["volume_variation"])

        # setting
        self._efficiency = {"charge": data_device["charge"]["efficiency"], "discharge": data_device["discharge"]["efficiency"]}  # efficiency
        self._max_transferable_energy = {"charge": lambda: data_device["charge"]["power"] * time_step,
                                         "discharge": lambda: data_device["discharge"]["power"] * time_step}

        self._charge_nature = data_device["charge"]["nature"]
        self._discharge_nature = data_device["discharge"]["nature"]

        # the two following temperatures give the relation between energy stored and temperature of the storage
        self._min_temperature = data_device["minimum_temperature"]  # the temperature corresponding to the minimum energy to unload
        self._max_temperature = data_device["maximum_temperature"]  # the temperature corresponding to the maximum storable energy
        self._T_solidus = data_device["temperature_solidus"]
        self._T_liquidus = data_device["temperature_liquidus"]
        self._latent_heat = data_device["latent_heat"]

        # tank characteristics
        self._thermal_conductivity = data_device["thermal_conductivity"]
        self._thickness = data_device["thickness"]
        self._mass = data_device["volume"] * data_device["density"]
        self._surface = data_device["surface"]

        # material characteristics
        self._thermal_capacity_liquid = data_device["thermal_capacity_liquid"]
        self._thermal_capacity_solid = data_device["thermal_capacity_solid"]

        # energy equivalence
        self._min_energy = (273.15 + self._min_temperature) * self._mass * self._thermal_capacity_solid  # energy corresponding to the min temperature, when the material is solid
        self._capacity = ((273.15 + self._T_solidus) * self._thermal_capacity_solid + self._latent_heat + (self._T_liquidus + self._max_temperature) * self._thermal_capacity_liquid) * self._mass  # energy corresponding to the max temperature, when the material is liquid
        self._catalog.add(f"{self.name}.energy_stored", self._temperature_to_energy(self._initial_temperature))  # the energy stored at the starting point
        middle_temperature = (self._max_temperature + self._min_temperature) / 2  # temperature corresponding to the initial half-charge
        self._solidus_fraction = max(min((middle_temperature - self._T_solidus) / (self._T_liquidus - self._T_solidus), 0), 1)  # the initial liquid fraction in the storage (if any)

    def _energy_to_temperature(self, energy):  # conversion from energy to temperature
        temperature = (energy - self._min_energy) / (self._capacity - self._min_energy) * (self._max_temperature - self._min_temperature) + self._min_temperature 
        return temperature

    def _temperature_to_energy(self, temperature):  # conversion from temperature to energy
        energy = (temperature - self._min_temperature) / (self._max_temperature - self._min_temperature) * (self._capacity - self._min_energy) + self._min_energy + max(min((temperature - self._T_solidus) / (self._T_liquidus - self._T_solidus), 0), 1) * self._latent_heat
        return energy

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _degradation_of_energy_stored(self):  # a class-specific function reducing the energy stored over time
        # the device has to send information in energy but calculation with temperatures are needed to calculate the degradation
        energy_stored = self._catalog.get(f"{self.name}.energy_stored")
        storage_temperature = self._energy_to_temperature(energy_stored)  # conversion of stored energy to temperature of the storage
        outdoor_temperature = self._catalog.get(f"{self._location}.current_outdoor_temperature")
        time_step = self._catalog.get("time_step")
        heat_loss = self._thermal_conductivity * self._surface * time_step / self._thickness * (outdoor_temperature - storage_temperature)
        return energy_stored + heat_loss  # actualisation of the energy stored






