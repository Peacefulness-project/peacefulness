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
        self._buffer = {}

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
        self._cold_startup_time = data_device["cold_startup_time"]  # the needed time to ramp-up fresh (time-steps)

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
            print(f"The sizing of the Biomass is not correct, the new fuel recharge quantity is: {self._recharge_quantity}")
        elif self._recharge_quantity > max_bound:
            self._recharge_quantity = max_bound
            print(f"The sizing of the Biomass is not correct, the new fuel recharge quantity is: {self._recharge_quantity}")
        self._fuel_mass_flow_rate = self._recharge_quantity / self._autonomy

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        current_time = self._catalog.get("simulation_time")

        if self.cold_startup_flag:
            startup_time = next(iter(self._buffer.values()))
            if current_time == startup_time + 1:
                min_production = 0.0
                max_production = - 0.1 * self._max_power
            elif current_time == startup_time + 2:
                min_production = 0.0
                max_production = - 0.2 * self._max_power
            elif current_time == startup_time + 3:
                min_production = 0.0
                max_production = - 0.4 * self._max_power
            else:
                min_production = 0.0
                max_production = - self._max_power
        else:
            min_production = 0.0
            max_production = - 0.1 * self._max_power

        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        for nature in self.natures:
            energy_wanted[nature.name]["energy_minimum"] = min_production  # energy produced by the device
            energy_wanted[nature.name]["energy_nominal"] = min_production  # energy produced by the device
            energy_wanted[nature.name]["energy_maximum"] = max_production  # energy produced by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):
        super().react()
        current_time = self._catalog.get("simulation_time")
        for nature in self.natures:
            energy_accorded = self.get_energy_accorded_quantity(nature)
            if not self.cold_startup_flag and energy_accorded != 0.0:
                self._buffer["cold_startup"] = current_time
                self.cold_startup_flag = True
            elif self.cold_startup_flag and energy_accorded == 0.0:
                self._buffer.pop("cold_startup")
                self.cold_startup_flag = False


