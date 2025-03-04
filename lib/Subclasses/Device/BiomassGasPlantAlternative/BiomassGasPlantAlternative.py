# device representing either a biomass or waste boiler or plant.
from src.common.DeviceMainClasses import AdjustableDevice
from math import ceil, floor


class BiomassGasPlantAlternative(AdjustableDevice):

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/BiomassGasPlantAlternative/BiomassGasPlantAlternative.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step  # max power (kWh)
        self._recharge_quantity = parameters["recharge_quantity"]  # fuel quantity recharged at each period (kg)
        self._autonomy = parameters["autonomy"] / time_step  # the time period during which the plant operates without recharging (timesteps)
        self.cold_startup_flag = False
        self.cold_startup = {"time_step": [1, 2, 3, 4, 5], "energy": [0.015119328903383002, 0.1195973380807878, 0.31337064873887166, 0.9197118707001486, 1]}
        self.warm_startup_flag = False
        self.warm_startup = {"time_step": [1, 2], "energy": [0.7473570931988995, 1]}
        self._log = {"time_step": [], "energy": [], "state": []}
        self._check_quantities()  # checking the proposed sizing

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
        for index in range(len(self.cold_startup["energy"])):
            self.cold_startup["energy"][index] *= self._max_power
        for index in range(len(self.warm_startup["energy"])):
            self.warm_startup["energy"][index] *= self._max_power

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually
        min_production = 0.0

        if len(self._log["state"]) > 0:
            if self._log["state"][-1] == "idle" or self._log["state"][-1] == "shut_down":
                max_production = - 0.01 * self._max_power
                coming_volume = - 0.01 * self._max_power

            elif self._log["state"][-1] == "nominal_state":
                max_production = - self._max_power
                coming_volume = - 5 * self._max_power
        else:
            max_production = - 0.01 * self._max_power
            coming_volume = - 0.01 * self._max_power

        if self.cold_startup_flag:  # a cold startup is triggered
            coming_volume = 0.0
            inside_flag, nearest_value = check_distance(self.cold_startup["energy"], - self._log["energy"][-1])
            if inside_flag:  # a standard cold start-up
                coldStartUpIndex = self.cold_startup["energy"].index(nearest_value)
                if coldStartUpIndex < len(self.cold_startup["energy"]) - 1:
                    max_production = - self.cold_startup["energy"][coldStartUpIndex + 1]
                    for index in range(coldStartUpIndex + 1, len(self.cold_startup["energy"])):
                        coming_volume -= self.cold_startup["energy"][index]
                    remaining_steps = 5 - (len(self.cold_startup["energy"]) - 1 - coldStartUpIndex)
                    if remaining_steps > 0:
                        for index in range(remaining_steps):
                            coming_volume -= self._max_power
                else:
                    max_production = - self._max_power
                    coming_volume = - 5 * self._max_power
            else:  # Energy accorded doesn't correspond to the cold start-up curve
                print(f"in case of cold start up {- self._log["energy"][-1]}")
                corresponding_time = get_timestep_of_data(self._coldStartUp, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
                upper_timestep = ceil(corresponding_time)
                if not upper_timestep > max(self._coldStartUp["time"]):
                    max_production = - get_data_at_timestep(self._coldStartUp, upper_timestep) * self._max_power
                    coldStartUpIndex = self.cold_startup["time_step"].index(upper_timestep)
                    for index in range(coldStartUpIndex, len(self.cold_startup["energy"])):
                        coming_volume -= self.cold_startup["energy"][index]
                    remaining_steps = 5 - (len(self.cold_startup["energy"]) - coldStartUpIndex)
                    if remaining_steps > 0:
                        for index in range(remaining_steps):
                            coming_volume -= self._max_power
                else:
                    max_production = - self._max_power
                    coming_volume = - 5 * self._max_power

        elif self.warm_startup_flag:  # a warm startup is triggered
            coming_volume = 0.0
            inside_flag, nearest_value = check_distance(self.warm_startup["energy"], - self._log["energy"][-1])
            if inside_flag:  # a standard warm start-up
                warmStartUpIndex = self.warm_startup["energy"].index(nearest_value)
                if warmStartUpIndex < len(self.warm_startup["energy"]) - 1:
                    max_production = - self.warm_startup["energy"][warmStartUpIndex + 1]
                    for index in range(warmStartUpIndex + 1, len(self.warm_startup["energy"])):
                        coming_volume -= self.warm_startup["energy"][index]
                    remaining_steps = 5 - (len(self.warm_startup["energy"]) - 1 - warmStartUpIndex)
                    if remaining_steps > 0:
                        for index in range(remaining_steps):
                            coming_volume -= self._max_power
                else:
                    max_production = - self._max_power
                    coming_volume = - 5 * self._max_power
            else:  # Energy accorded doesn't correspond to the warm start-up curve
                print(f"in case of warm start up {- self._log["energy"][-1]}")
                corresponding_time = get_timestep_of_data(self._warmStartUp, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
                upper_timestep = ceil(corresponding_time)
                if not upper_timestep > max(self._warmStartUp["time"]):
                    max_production = - get_data_at_timestep(self._warmStartUp, upper_timestep) * self._max_power
                    warmStartUpIndex = self.warm_startup["time_step"].index(upper_timestep)
                    for index in range(warmStartUpIndex, len(self.warm_startup["energy"])):
                        coming_volume -= self.warm_startup["energy"][index]
                    remaining_steps = 5 - (len(self.warm_startup["energy"]) - warmStartUpIndex)
                    if remaining_steps > 0:
                        for index in range(remaining_steps):
                            coming_volume -= self._max_power
                else:
                    max_production = - self._max_power
                    coming_volume = - 5 * self._max_power

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
        self._log["time_step"].append(self._catalog.get("simulation_time"))
        for nature in self.natures:
            self._log["energy"].append(self.get_energy_accorded_quantity(nature))
            if self._log["energy"][-1] == 0:  # if no energy was accorded (no production)
                self.cold_startup_flag = False
                self.warm_startup_flag = False
                if len(self._log["energy"]) < 2:  # first start up
                    self._log["state"].append("idle")
                else:
                    if self._log["energy"][-2] == 0:  # at least 2 time steps since shut-down
                        self._log["state"].append("idle")
                    else:  # the biomass plant was just shut-down for one time step
                        self._log["state"].append("shut_down")

            elif self._log["energy"][-1] == - self._max_power:  # the biomass plant generates nominal energy
                self._log["state"].append("nominal_state")
                self.cold_startup_flag = False
                self.warm_startup_flag = False

            else:  # the biomass plant generates energy during the dynamic phase
                if len(self._log['state']) > 0:
                    if self._log['state'][-1] == "nominal_state":  # adjusting the generated power from the nominal state
                        if abs(self._log["energy"][-1]) <= 0.3 * self._max_power:  # a cold startup is needed
                            self._log["state"].append("cold_startup")
                            self.cold_startup_flag = True
                            self.warm_startup_flag = False
                        else:  # a warm startup is needed
                            self._log["state"].append("warm_startup")
                            self.cold_startup_flag = False
                            self.warm_startup_flag = True

                    elif self._log['state'][-1] == "cold_startup" or self._log['state'][-1] == "idle":  # conditions to perform a cold startup
                        self._log["state"].append("cold_startup")
                        self.cold_startup_flag = True
                        self.warm_startup_flag = False

                    elif self._log['state'][-1] == "warm_startup" or self._log['state'][-1] == "shut_down":  # conditions to perform a warm startup
                        self._log["state"].append("warm_startup")
                        self.cold_startup_flag = False
                        self.warm_startup_flag = True
                else:
                    self._log["state"].append("cold_startup")
                    self.cold_startup_flag = True
                    self.warm_startup_flag = False


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


def get_timestep_of_data(df: dict, out_power: float, max_power: float):
    """
    Give back the time step corresponding to the value of %Pth using interpolation (if it doesn't already exist in the data).
    """
    out_power /= max_power
    out_power *= 100
    # Check if the timestep exists in the DataFrame
    if out_power in df['power']:
        return df['time'][df['power'].index(out_power)]
    else:
        # If out_power does not exist, interpolate between the nearest values
        lower_data = max((d for d in df["power"] if d < out_power), default=None)
        upper_data = min((d for d in df["power"] if d > out_power), default=None)
        # Check if lower and upper timesteps exist
        if not lower_data or not upper_data:
            raise ValueError(f"Power {out_power} is out of bounds for interpolation.")
        # Get corresponding data for lower and upper timesteps
        lower_timestep = df['time'][df['power'].index(lower_data)]
        upper_timestep = df['time'][df['power'].index(upper_data)]
        # Perform linear interpolation
        interpolated_value = lower_timestep + (upper_timestep - lower_timestep) * (out_power - lower_data) / (upper_data - lower_data)
        return interpolated_value


def check_distance(myList: list, myElement, precision: float=1e-6):
    myFlag = False
    my_element = None
    if myElement in myList:
        myFlag = True
        my_element = myElement
    else:
        for element in myList:
            if abs(element - myElement) < precision:
                myFlag = True
                my_element = element
                break
    return myFlag, my_element
