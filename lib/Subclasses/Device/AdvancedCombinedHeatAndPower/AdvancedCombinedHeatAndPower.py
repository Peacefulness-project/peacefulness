# This subclass of Converter is supposed to represent a combined heat and power device. Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter
from src.tools.Utilities import into_list


class AdvancedCombinedHeatAndPower(Converter):

    def __init__(self, name, contracts, agent,
                 upstream_aggregators_list, downstream_aggregators_list,
                 profiles, parameters):
        upstream_aggregators_list = into_list(upstream_aggregators_list)
        downstream_aggregators_list = into_list(downstream_aggregators_list)
        super().__init__(name, contracts, agent, upstream_aggregators_list + downstream_aggregators_list,
                         "lib/Subclasses/Device/AdvancedCombinedHeatAndPower/AdvancedCombinedHeatAndPower.json",
                         profiles, parameters)

        contracts = {contract.nature.name: contract for contract in contracts}
        self._upstream_aggregators_list = [{"name": aggregator.name, "nature": aggregator.nature.name, "contract": contracts[aggregator.nature.name]} for aggregator in upstream_aggregators_list]  # list of aggregators involved in the production of energy. The order is not important.
        self._downstream_aggregators_list = [{"name": aggregator.name, "nature": aggregator.nature.name, "contract": contracts[aggregator.nature.name]} for aggregator in downstream_aggregators_list]  # list of aggregators involved in the consumption of energy. The order is important: the first aggregator defines the final quantity of energy

        time_step = self._catalog.get("time_step")
        # TODO: mettre les paramètres adéquats
        self._energy_physical_limits = {"minimum_energy": 0, "maximum_energy": parameters["max_power"] * time_step}

        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            self._catalog.add(f"{self.name}.{nature_name}.efficiency", None)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        # TODO: mettre les bons paramètres
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._efficiency = data_device["efficiency"]  # the efficiency of the converter for each nature of energy

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    # TODO: implémenter le calcul
    def _efficiency(self, ):

    def update(self):  # method updating needs of the devices before the supervision
        # TODO: adapter les arguments du self._efficiency
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        # downstream side
        for aggregator in self ._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted[nature_name]["energy_minimum"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency()  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency()  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = - self._energy_physical_limits["maximum_energy"] * self._efficiency()  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["efficiency"] = self._efficiency()

        # upstream side
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted[nature_name]["energy_minimum"] = self._energy_physical_limits["minimum_energy"] / self._efficiency()  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = self._energy_physical_limits["minimum_energy"] / self._efficiency()  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = self._energy_physical_limits["maximum_energy"] / self._efficiency()  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["efficiency"] = self._efficiency()

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def second_update(self):  # a method used to harmonize aggregator's decisions concerning multi-energy devices
        # TODO: adapter les arguments du self._efficiency
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        # determination of the energy consumed/produced
        energy_wanted_downstream = []
        energy_available_upstream = []
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted_downstream.append(-self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"] / self._efficiency())  # the energy asked by the downstream aggregator
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_available_upstream.append(self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"] / self._efficiency())  # the energy accorded by the upstream aggregator

        limit_energy_upstream = min(energy_available_upstream)
        limit_energy_downstream = min(energy_wanted_downstream)
        raw_energy_transformed = min(limit_energy_upstream, limit_energy_downstream)

        # downstream side
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]

            # resetting the demand
            energy_wanted[nature_name]["energy_minimum"] = - raw_energy_transformed * self._efficiency()  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = - raw_energy_transformed * self._efficiency()  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = - raw_energy_transformed * self._efficiency()  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["price"] = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["price"]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name]["efficiency"] = self._efficiency()

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"] = - raw_energy_transformed * self._efficiency()
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

        # upstream side
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]

            # resetting the demand
            energy_wanted[nature_name]["energy_minimum"] = raw_energy_transformed * self._efficiency()  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = raw_energy_transformed * self._efficiency()  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = raw_energy_transformed * self._efficiency()  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["price"] = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["price"]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"] = raw_energy_transformed * self._efficiency()
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

    def react(self):
        super().react()  # actions needed for all the devices

        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            self._catalog.set(f"{self.name}.{nature_name}.efficiency", self._efficiency())



