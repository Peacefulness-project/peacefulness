# device representing either a biomass or waste boiler or plant.
from src.common.DeviceMainClasses import AdjustableDevice
from typing import List, Optional
from math import ceil


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
        self._initial_conditions = {"initial_energy": parameters["initial_energy"], "initial_state": self._determine_initial_state(parameters["initial_energy"])}
        self.cold_startup_signal_time = None
        # todo if the original curve is used
        # self.cold_startup = {"time_step": [0, 1, 2, 3, 4, 5], "energy": [0.01, 0.015119328903383002, 0.1195973380807878, 0.31337064873887166, 0.9197118707001486, 1]}
        self.cold_startup = {"time_step": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "energy": [0, 0.01, 0.015119328903383002, 0.1195973380807878, 0.2164839934098297, 0.31337064873887166, 0.5154843893926306, 0.7175981300463896, 0.9197118707001486, 1]}
        
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
        # todo if the original curve is to be used
        # self._coldStartUp = data_device["cold_startup"]  # thermal power evolution during a cold startup

        self._unused_nature_removal()

    def _determine_initial_state(self, initial_power):
        if initial_power == self._max_power:
            return "nominal_state"
        elif initial_power == 0:
            return "idle"
        elif self._max_power > initial_power > 0:
            return "cold_startup"
        else:
            raise Exception("The initial energy specified for the biomass plant is not valid !")

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
            

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually
        current_timestep = self._catalog.get("simulation_time")
        min_production = 0.0

        if current_timestep == 0:  # initial conditions
            self._log["state"].append(self._initial_conditions["initial_state"])
            if self._log["state"][-1] == "cold_startup":
                self._log["energy"].append(- self._initial_conditions["initial_energy"])
                self.cold_startup_signal_time = current_timestep
                
        if self._log["state"][-1] == "idle":
            max_production = - 0.01 * self._max_power
            coming_volume = - 0.01 * self._max_power

        elif self._log["state"][-1] == "nominal_state":
            max_production = - self._max_power
            coming_volume = - 5 * self._max_power

        elif self._log["state"][-1] == "cold_startup":  # a cold startup is triggered
            coming_volume = 0.0
            delta_time = current_timestep - self.cold_startup_signal_time
            if delta_time > 0 and delta_time in self.cold_startup["time_step"]:
                corresponding_max_energy = self.cold_startup["energy"][self.cold_startup["time_step"].index(delta_time - 1)]
                if - self._log["energy"][-1] == corresponding_max_energy:  # a standard cold start-up (E_accorded == corresponding max_production at timestep 'i')
                    max_production = - self.cold_startup["energy"][self.cold_startup["time_step"].index(delta_time)]
                    for index in range(self.cold_startup["time_step"].index(delta_time), 5 + self.cold_startup["time_step"].index(delta_time)):
                        if index <= len(self.cold_startup["energy"]) - 1:
                            coming_volume -= self.cold_startup["energy"][index]
                        else:
                            coming_volume -= self._max_power
                else:  # in the previous time step the energy accorded was less than the one corresponding to the standard curve
                    corresponding_time, corresponding_power = get_timestep_of_data(self.cold_startup, - self._log["energy"][-1], self._max_power)
                    next_timestep = corresponding_time + self._catalog.get("time_step")
                    if not next_timestep > max(self.cold_startup["time_step"]):
                        max_production = - get_data_at_timestep(self.cold_startup, next_timestep)
                        coldStartUpIndex = find_nearest_point(self.cold_startup["time_step"], ceil(next_timestep))
                        for index in range(coldStartUpIndex, 5 + coldStartUpIndex):
                            if index <= len(self.cold_startup["energy"]) - 1:
                                coming_volume -= self.cold_startup["energy"][index]
                            else:
                                coming_volume -= self._max_power
                    else:
                        max_production = - self._max_power
                        coming_volume = - 5 * self._max_power
            else:
                if self._log['energy'][-1] == - self._max_power:
                    max_production = - self._max_power
                    coming_volume = - 5 * self._max_power
                else:
                    corresponding_time, corresponding_power = get_timestep_of_data(self.cold_startup, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
                    next_timestep = corresponding_time + self._catalog.get("time_step")
                    if not next_timestep > max(self.cold_startup["time_step"]):
                        max_production = - get_data_at_timestep(self.cold_startup, next_timestep)
                        coldStartUpIndex = find_nearest_point(self.cold_startup["time_step"], ceil(next_timestep))
                        for index in range(coldStartUpIndex, 5 + coldStartUpIndex):
                            if index <= len(self.cold_startup["energy"]) - 1:
                                coming_volume -= self.cold_startup["energy"][index]
                            else:
                                coming_volume -= self._max_power
                    else:
                        max_production = - self._max_power
                        coming_volume = - 5 * self._max_power
                        
        else:
            raise Exception("State assignment to the log dict attribute is not correct !")

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

        if self._log["time_step"][-1] == 0:  # initial conditions
            self._log["state"] = []
            self._log["energy"] = []
            self.cold_startup_signal_time = None

        for nature in self.natures:
            self._log["energy"].append(self.get_energy_accorded_quantity(nature))
            if self._log["energy"][-1] == 0:  # if no energy was accorded (no production)
                self._log["state"].append("idle")
                self.cold_startup_signal_time = None

            elif self._log["energy"][-1] == - self._max_power:  # the biomass plant generates nominal energy
                self._log["state"].append("nominal_state")
                self.cold_startup_signal_time = None

            else:  # the biomass plant generates energy during the dynamic phase
                self._log["state"].append("cold_startup")
                if self.cold_startup_signal_time is None:
                    self.cold_startup_signal_time = self._catalog.get("simulation_time")
    
    @property
    def last_energy(self):  # useful for the rule-based strategy in the ramping-up management case
        return self._log["energy"][-1]
    

def get_data_at_timestep(df: dict, timestep: int):
    """
    Give back the value of %Pth as a function of the timestep using interpolation (if it doesn't already exist in the data).
    """
    # Check if the timestep exists in the DataFrame
    if timestep in df['time_step']:
        return df['energy'][df['time_step'].index(timestep)]
    else:
        # If timestep does not exist, interpolate between the nearest timesteps
        lower_timestep = max((t for t in df["time_step"] if t < timestep), default=None)
        upper_timestep = min((t for t in df["time_step"] if t > timestep), default=None)

        # Check if lower and upper timesteps exist
        if lower_timestep is None or upper_timestep is None:
            raise ValueError(f"Timestep {timestep} is out of bounds for interpolation.")

        # Get corresponding data for lower and upper timesteps
        lower_data = df['energy'][df['time_step'].index(lower_timestep)]
        upper_data = df['energy'][df['time_step'].index(upper_timestep)]

        # Perform linear interpolation
        interpolated_value = lower_data + (upper_data - lower_data) * (timestep - lower_timestep) / (upper_timestep - lower_timestep)
        # interpolated_value /= 100  # todo if the original curve is used
        
        return interpolated_value


def get_timestep_of_data(df: dict, out_power: float, max_power: float):
    """
    Give back the time step corresponding to the value of %Pth using interpolation (if it doesn't already exist in the data).
    """
    # todo if the original curve is used
    # out_power /= max_power
    # out_power *= 100
    # Check if the timestep exists in the DataFrame
    if out_power in df['energy']:
        return df['time_step'][df['energy'].index(out_power)], out_power
    else:
        # If out_power does not exist, interpolate between the nearest values
        lower_data = max((d for d in df["energy"] if d < out_power), default=None)
        upper_data = min((d for d in df["energy"] if d > out_power), default=None)
        # Check if lower and upper timesteps exist
        if lower_data is None or upper_data is None:
            raise ValueError(f"Power {out_power} is out of bounds for interpolation.")
        # Get corresponding data for lower and upper timesteps
        lower_timestep = df['time_step'][df['energy'].index(lower_data)]
        upper_timestep = df['time_step'][df['energy'].index(upper_data)]
        # Perform linear interpolation
        interpolated_value = lower_timestep + (upper_timestep - lower_timestep) * (out_power - lower_data) / (upper_data - lower_data)
        return interpolated_value, out_power


def check_distance(myList: list, myElement, precision: float=1e-2):
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


def find_nearest_point(time_list: List, time_point: int) -> Optional[int]:
    if time_point in time_list:
        return time_list.index(time_point)
    else:
        while time_point <= max(time_list):
            time_point += 1
            if time_point in time_list:
                return time_list.index(time_point)
    return None
