# This subclass of Converter is supposed to represent a heat pump. Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.Converter import Converter


class HeatPump(Converter):

    def __init__(self, world, name, contract, agent, upstream_aggregator, downstream_aggregator, technical_profile_name):
        super().__init__(world, name, contract, agent, "lib/Subclasses/Converter/HeatPump/HeatPump.json", upstream_aggregator, downstream_aggregator, technical_profile_name)

        self._energy_physical_limits = {"minimum_energy": 0, "maximum_energy": self._capacity}

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _get_technical_data(self):
        technical_data = self._read_technical_data()

        self._efficiency = technical_data["efficiency"]  # the efficiency of the converter
        self._capacity = technical_data["capacity"]  # the maximum capacity of the converter

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update_converter(self):
        energy_minimum = - self._energy_physical_limits["minimum_energy"]  # the physical minimum of energy this converter has to consume
        energy_maximum = - self._energy_physical_limits["maximum_energy"]  # the physical maximum of energy this converter can consume
        energy_nominal = - self._capacity

        self._catalog.set(f"{self.name}.{self.natures['downstream'].name}.energy_wanted", {"energy_minimum": energy_minimum, "energy_nominal": energy_nominal, "energy_maximum": energy_maximum, "price": None})

    def update(self):
        energy_nominal = self._catalog.get(f"{self.name}.{self.natures['downstream'].name}.energy_accorded") / self._efficiency  # the energy asked by the downstream aggregator to the upstream one
        energy_minimum = self._energy_physical_limits["minimum_energy"] / self._efficiency  # the physical minimum of energy this converter has to consume
        energy_maximum = self._energy_physical_limits["maximum_energy"] / self._efficiency  # the physical maximum of energy this converter can consume

        self._catalog.set(f"{self.name}.{self.natures['upstream'].name}.energy_wanted", {"energy_minimum": energy_minimum, "energy_nominal": energy_nominal, "energy_maximum": energy_maximum, "price": None})







