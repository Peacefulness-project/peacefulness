# This subclass of device represent underground geothermal storage
# Current packages
from src.common.DeviceMainClasses import Storage


class UndergroundThermalStorage(Storage):

    def __init__(self, name, contracts, agent, aggregator, profiles, parameters, filename="lib/Subclasses/Device/UndergroundThermalStorage/UndergroundThermalStorage.json"):
        parameters["capacity"] = 0
        self._location = parameters["ground_temperature_daemon"]
        parameters["initial_SOC"] = 0  # dummy value to fit the mother class signature
        self._initial_storage_temperature = parameters["initial_storage_temperature"]

        super().__init__(name, contracts, agent, filename, aggregator, profiles, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profile):
        self._location = self._catalog.daemons[self._location].location  # the location of the device, in relation with the meteorological data

        time_step = self._catalog.get("time_step")
        data_device = self._read_technical_data(profile["device"])  # parsing the data

        # setting
        self._efficiency = {"charge": data_device["charge"]["efficiency"], "discharge": data_device["discharge"]["efficiency"]}  # efficiency
        self._exchanger_conductance = data_device["exchanger_conductance"]

        # tank characteristics
        self._thermal_conductivity = data_device["storage_volumic_thermal_capacity"]  # m3
        self._volume = data_device["volume"]  # m3

        # fluid characteristics
        self._heat_transfer_fluid_capacity = data_device["heat_transfer_fluid_capacity"]  # kWh.K-1.kg-1
        self._thermal_capacity = data_device["heat_transfer_fluid_capacity"]  # kWh.K-1.kg-1
        self._network_temperature = data_device["network_temperature"] + 273.15  # K, TODO: le remplacer par un démon ?

        self._heat_loss_factor = data_device["heat_loss_factor"]  # -
        self._storage_depth = data_device["storage_depth"]  # m

        # the two following temperatures give the relation between energy stored and temperature of the storage
        self._min_temperature = data_device["minimum_temperature"] + 273.15  # K, the temperature corresponding to the minimum energy to unload
        self._max_temperature = data_device["maximum_temperature"] + 273.15  # K, the temperature corresponding to the maximum storable energy

        # energy equivalence
        self._min_energy = self._min_temperature * self._thermal_capacity * self._volume  # energy corresponding to the min temperature
        self._max_energy = self._max_temperature * self._thermal_capacity * self._volume  # energy corresponding to the max temperature
        self._capacity = self._max_energy  # energy_corresponding to the maximum usable energy
        self._catalog.add(f"{self.name}.energy_stored", self._temperature_to_energy(self._initial_storage_temperature + 273.15))  # the energy stored at a given time, considered as half charged at the beginning

        self._max_transferable_energy = {"charge": self._charging_power,
                                         "discharge": self._discharging_power}

        self._charge_nature = data_device["charge"]["nature"]
        self._discharge_nature = data_device["discharge"]["nature"]
        self._ground_temperature = data_device["ground_temperature"] + 273.15  # K

    def _energy_to_temperature(self, energy):  # conversion from energy to temperature
        temperature = energy / self._max_energy * self._max_temperature
        return temperature

    def _temperature_to_energy(self, temperature):  # conversion from temperature to energy
        energy = temperature * self._thermal_capacity * self._volume
        return energy

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _degradation_of_energy_stored(self):  # a class-specific function reducing the energy stored over time
        # the device has to send information in energy but calculation with temperatures are needed to calculate the degradation
        energy_stored = self._catalog.get(f"{self.name}.energy_stored")
        storage_temperature = self._energy_to_temperature(energy_stored)  # conversion of stored energy to temperature of the storage
        # ground_temperature = self._catalog.get(f"{self._location}.ground_temperature")
        time_step = self._catalog.get("time_step")

        storage_temperature = storage_temperature - (self._thermal_conductivity * (storage_temperature - self._ground_temperature) * self._heat_loss_factor * self._storage_depth / 2 * time_step) / (self._volume * self._thermal_capacity)  # calculation of the loss of temperature
        # storage temperature is considered constant in the heat transfer calculation
        self._state_of_charge = (self._temperature_to_energy(storage_temperature) - self._min_energy) / self._capacity
        return self._temperature_to_energy(storage_temperature)  # actualisation of the energy stored

    def _charging_power(self):
        energy_stored = self._catalog.get(f"{self.name}.energy_stored")
        storage_temperature = self._energy_to_temperature(energy_stored)  # conversion of stored energy to temperature of the storage
        time_step = self._catalog.get("time_step")
        energy_flow = max(0, self._exchanger_conductance * (self._max_temperature - storage_temperature) * time_step)
        return energy_flow

    def _discharging_power(self):
        energy_stored = self._catalog.get(f"{self.name}.energy_stored")
        storage_temperature = self._energy_to_temperature(energy_stored)  # conversion of stored energy to temperature of the storage
        time_step = self._catalog.get("time_step")
        energy_flow = max(0, self._exchanger_conductance * (storage_temperature - self._network_temperature) * time_step)
        return energy_flow


