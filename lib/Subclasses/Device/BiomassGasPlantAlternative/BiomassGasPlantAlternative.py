# device representing either a biomass or waste boiler or plant.
from src.common.DeviceMainClasses import AdjustableDevice


class BiomassGasPlantAlternative(AdjustableDevice):

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/BiomassGasPlantAlternative/BiomassGasPlantAlternative.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step  # max power (kWh)
        self._recharge_quantity = parameters["recharge_quantity"]  # fuel quantity recharged at each period (kg)
        self._autonomy = parameters["autonomy"] / self._catalog.get("time_step")  # the time period during which the plant operates without recharging (timesteps)
        self._check_quantities()  # checking the proposed sizing
        self.cold_startup_flag = False
        self.warm_startup_flag = False
        self._buffer = {"last_stopped": 0}

        self._catalog.add(f"{self.name}.exergy_in", 0)
        self._catalog.add(f"{self.name}.exergy_out", 0)

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None
        self._efficiency = data_device["efficiency"]  # the efficiency of the waste/biomass plant (%)
        self._min_PCI = data_device["min_PCI"]  # the min PCI of the waste/biomass plant (kWh/kg)
        self._max_PCI = data_device["max_PCI"]  # the max PCI of the waste/biomass plant (kWh/kg)
        self._coldStartUp = data_device["cold_startup"]  # thermal power evolution during a cold startup
        self._warmStartUp = data_device["warm_startup"]  # thermal power evolution during a warm startup

        self._unused_nature_removal()

    def _check_quantities(self):
        """
        This method checks whether the indicated recharge quantity corresponds to realistic PCI of biomass/waste.
        It also determines the mass flow rate of the fuel (biomass/waste).
        """
        max_bound = self._max_power * self._autonomy / (self._min_PCI * self._efficiency)
        min_bound = self._max_power * self._autonomy / (self._max_PCI * self._efficiency)
        if self._recharge_quantity < min_bound:
            self._recharge_quantity = min_bound
            # print(f"The sizing of the Biomass is not correct, the new fuel recharge quantity is: {self._recharge_quantity}")
        elif self._recharge_quantity > max_bound:
            self._recharge_quantity = max_bound
            # print(f"The sizing of the Biomass is not correct, the new fuel recharge quantity is: {self._recharge_quantity}")
        self._fuel_mass_flow_rate = self._recharge_quantity / self._autonomy

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        current_time = self._catalog.get("simulation_time")

        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually
        min_production = 0.0
        if self.cold_startup_flag:
            startup_time = self._buffer["cold_startup"]
            if current_time == startup_time + 1:
                max_production = - get_data_at_timestep(self._coldStartUp, 1) * self._max_power
                coming_volume = - (get_data_at_timestep(self._coldStartUp, 1) + get_data_at_timestep(self._coldStartUp, 2) + get_data_at_timestep(self._coldStartUp, 3) + get_data_at_timestep(self._coldStartUp, 4) + 1) * self._max_power
            elif current_time == startup_time + 2:
                max_production = - get_data_at_timestep(self._coldStartUp, 2) * self._max_power
                coming_volume = - (get_data_at_timestep(self._coldStartUp, 2) + get_data_at_timestep(self._coldStartUp, 3) + get_data_at_timestep(self._coldStartUp, 4) + 2) * self._max_power
            elif current_time == startup_time + 3:
                max_production = - get_data_at_timestep(self._coldStartUp, 3) * self._max_power
                coming_volume = - (get_data_at_timestep(self._coldStartUp, 3) + get_data_at_timestep(self._coldStartUp, 4) + 3) * self._max_power
            elif current_time == startup_time + 4:
                max_production = - get_data_at_timestep(self._coldStartUp, 4) * self._max_power
                coming_volume = - (get_data_at_timestep(self._coldStartUp, 4) + 4) * self._max_power
            else:
                max_production = - self._max_power
                coming_volume = - 5 * self._max_power

        elif self.warm_startup_flag:
            startup_time = self._buffer["warm_startup"]
            if current_time == startup_time + 1:
                max_production = - get_data_at_timestep(self._warmStartUp, 1) * self._max_power
                coming_volume = - (get_data_at_timestep(self._warmStartUp, 1) + 4) * self._max_power
            else:
                max_production = - self._max_power
                coming_volume = - 5 * self._max_power

        else:  # idle
            max_production = - 0.01 * self._max_power
            coming_volume = - 0.01 * self._max_power

        for nature in self.natures:
            energy_wanted[nature.name]["energy_minimum"] = min_production  # energy produced by the device
            energy_wanted[nature.name]["energy_nominal"] = min_production  # energy produced by the device
            energy_wanted[nature.name]["energy_maximum"] = max_production  # energy produced by the device
            energy_wanted[nature.name]["coming_volume"] = coming_volume
            energy_wanted[nature.name]["flexibility"] = [1, 1, 1, 1, 1]
            energy_wanted[nature.name]["interruptibility"] = 1
        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):
        super().react()
        current_time = self._catalog.get("simulation_time")
        for nature in self.natures:
            energy_accorded = self.get_energy_accorded_quantity(nature)
            if energy_accorded != 0:
                if current_time - self._buffer["last_stopped"] <= 1 or self.warm_startup_flag:
                    self.warm_startup_flag = True
                    if not "warm_startup" in self._buffer:
                        self._buffer["warm_startup"] = current_time
                else:
                    self.cold_startup_flag = True
                    if not "cold_startup" in self._buffer:
                        self._buffer["cold_startup"] = current_time
                    self._buffer["last_stopped"] = 0
            else:
                if "cold_startup" in self._buffer:
                    self.cold_startup_flag = False
                    self._buffer.pop("cold_startup")
                    self._buffer["last_stopped"] = current_time
                elif "warm_startup" in self._buffer:
                    self.warm_startup_flag = False
                    self._buffer.pop("warm_startup")
                    self._buffer["last_stopped"] = current_time



def get_data_at_timestep(df: dict, timestep: int):
    """
    Give back the value of %Pth as a function of the timestep using interpolation (if it doesn't already exist in the data).
    """
    # Check if the timestep exists in the DataFrame
    if timestep in df['time']:
        return df['power'][df['time'].index(timestep)]
    else:
        # If timestep does not exist, interpolate between the nearest timesteps
        lower_timestep = max((t for t in df["time"] if t < timestep), default=None)
        upper_timestep = min((t for t in df["time"] if t > timestep), default=None)

        # Check if lower and upper timesteps exist
        if not lower_timestep or not upper_timestep:
            raise ValueError(f"Timestep {timestep} is out of bounds for interpolation.")

        # Get corresponding data for lower and upper timesteps
        lower_data = df['power'][df['time'].index(lower_timestep)]
        upper_data = df['power'][df['time'].index(upper_timestep)]

        # Perform linear interpolation
        interpolated_value = lower_data + (upper_data - lower_data) * (timestep - lower_timestep) / (upper_timestep - lower_timestep)
        interpolated_value /= 100
        return interpolated_value

