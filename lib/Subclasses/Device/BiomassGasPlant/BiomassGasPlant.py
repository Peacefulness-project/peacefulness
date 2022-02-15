# device representing a photovoltaic panel
from src.common.DeviceMainClasses import NonControllableDevice


class BiomassPlant(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/BiomassPlant/BiomassGasPlant.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step  # max power
        self._energy_stock = parameters["charge"]

        self._catalog.add(f"{self.name}.exergy_in", 0)
        self._catalog.add(f"{self.name}.exergy_out", 0)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()

        # usage profile
        self._efficiency = data_device["usage_profile"]["efficiency"]
        self._period = data_device["usage_profile"]["period"] / self._catalog.get("time_step")
        self._nature = data_device["usage_profile"]["nature"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        min_production, max_production = self._production_limits()
        energy_wanted[self._nature]["energy_minimum"] = min_production  # energy produced by the device
        energy_wanted[self._nature]["energy_nominal"] = min_production  # energy produced by the device
        energy_wanted[self._nature]["energy_maximum"] = max_production  # energy produced by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

        # # exergy calculation
        # reference_temperature = self._catalog.get(f"{self._outdoor_temperature_location}.reference_temperature")
        #
        # exergy_in = list()
        # for nature in energy_wanted:
        #     exergy_in.append(energy_received * (1 - reference_temperature/self._fluid_temperature))
        # exergy_in = sum(exergy_in)
        #
        # exergy_out = exergy_in * efficiency
        #
        # self._catalog.set(f"{self.name}.exergy_in", exergy_in)
        # self._catalog.set(f"{self.name}.exergy_out", exergy_out)

    def react(self):
        super().react()

        self._energy_stock -= self._catalog.get(f"{self.name}.{self._nature}.energy_accorded") * self._efficiency

    def _production_limits(self):
        """
        This method returns the minimum and maximum production possible for the plant taking into account its technical constraints.

        :return: min_production, max_production
        """
        min_production = 0
        max_production = - max(self._max_power, self._energy_stock / self._efficiency)
        # the value is negative because it is produced

        return min_production, max_production


