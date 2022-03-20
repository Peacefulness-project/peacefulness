# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice


class BiomassGasPlant(NonControllableDevice):

    LHV_CH4 = 50.1 / 3.6

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/BiomassGasPlant/BiomassGasPlant.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step  # max power
        self._recharge = parameters["waste_recharge"]  # in kg
        self._period = parameters["recharge_period"] / self._catalog.get("time_step")
        self._waste_quantity = 0  # the waste stock
        self._storage_capacity = parameters["storage_capacity"]  # the maximum energy storable in the tank, in kWh
        self._energy_stock = self._storage_capacity / 2  # the current quantity of gas
        self._next_prod = []

        self._catalog.add(f"{self.name}.exergy_in", 0)
        self._catalog.add(f"{self.name}.exergy_out", 0)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None
        self._waste_type = data_device["waste_type"]
        self._conversion_rate = data_device["conversion_rate"]
        self._waste_to_gas_time = data_device["waste_to_gas_time"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        current_time = self._catalog.get("simulation_time")
        if current_time % self._period== 0:
            self._next_prod.append([current_time, self._recharge])
            self._waste_quantity += self._recharge

        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        gas_production = self._calculate_gas_production()
        min_production, max_production = self._production_limits(gas_production)
        self._waste_quantity -= gas_production / self._conversion_rate  # quantity of waste remaining
        self._energy_stock += gas_production
        for nature in self.natures:
            energy_wanted[nature.name]["energy_minimum"] = min_production  # energy produced by the device
            energy_wanted[nature.name]["energy_nominal"] = min_production  # energy produced by the device
            energy_wanted[nature.name]["energy_maximum"] = max_production  # energy produced by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):
        super().react()

        for nature in self.natures:
            self._energy_stock += self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]

    def _production_limits(self, gas_production):
        """
        This method returns the minimum and maximum production possible for the plant taking into account its technical constraints.

        :return: min_production, max_production
        """
        available_storage = self._storage_capacity - self._energy_stock
        min_production = - max(gas_production - available_storage, 0)
        max_production = - min(self._max_power, self._energy_stock + gas_production)
        # the value is negative because it is produced

        return min_production, max_production

    def _calculate_gas_production(self):
        if self._next_prod != []:
            if self._catalog.get("simulation_time") == self._next_prod[0][0]:  # batch process
                gas_production = self._next_prod[0][1] * self._conversion_rate
                self._next_prod.pop(0)
        else:
            gas_production = 0

        return gas_production




