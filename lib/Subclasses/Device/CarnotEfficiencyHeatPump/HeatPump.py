# This subclass of Converter is supposed to represent a heat pump with a static efficiency from the Carnot efficiency.
from src.common.DeviceMainClasses import Converter


class HeatPump(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregator, profiles, parameters=None, filename="lib/Subclasses/Device/HeatPump/HeatPump.json"):
        super().__init__(name, contracts, agent, filename, upstream_aggregator, downstream_aggregator, profiles, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._isentropic_efficiency = data_device["isentropic_efficiency"]  # the efficiency of the converter for each nature of energy
        def _efficiency(Thot: float, Tcold: float):
            efficiency = self._isentropic_efficiency * 1 / (1 - Tcold/Thot)

            return efficiency

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        # downstream side
        for aggregator in self ._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted[nature_name]["energy_minimum"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = - self._energy_physical_limits["maximum_energy"] * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

        # upstream side
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted[nature_name]["energy_minimum"] = self._energy_physical_limits["minimum_energy"] / self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = self._energy_physical_limits["minimum_energy"] / self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = self._energy_physical_limits["maximum_energy"] / self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def second_update(self):  # a method used to harmonize aggregator's decisions concerning multi-energy devices
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        # determination of the energy consumed/produced
        energy_wanted_downstream = []
        energy_available_upstream = []
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted_downstream.append(-self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"] / self._efficiency[nature_name])  # the energy asked by the downstream aggregator
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_available_upstream.append(self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"] / self._efficiency[nature_name])  # the energy accorded by the upstream aggregator

        limit_energy_upstream = min(energy_available_upstream)
        limit_energy_downstream = min(energy_wanted_downstream)
        raw_energy_transformed = min(limit_energy_upstream, limit_energy_downstream)

        # downstream side
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]

            # resetting the demand
            energy_wanted[nature_name]["energy_minimum"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["price"] = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["price"]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"] = - raw_energy_transformed * self._efficiency[nature_name]
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

        # upstream side
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]

            # resetting the demand
            energy_wanted[nature_name]["energy_minimum"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["price"] = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["price"]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"] = raw_energy_transformed * self._efficiency[nature_name]
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

