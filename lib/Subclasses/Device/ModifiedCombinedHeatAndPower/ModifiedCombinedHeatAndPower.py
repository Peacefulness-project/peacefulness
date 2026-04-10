# This subclass of Converter is supposed to represent a combined heat and power device. Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter
from src.tools.Utilities import into_list
from scipy.optimize import root_scalar


class ModifiedCombinedHeatAndPower(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregators_list, downstream_aggregators_list, profiles, parameters):
        upstream_aggregators_list = into_list(upstream_aggregators_list)
        downstream_aggregators_list = into_list(downstream_aggregators_list)
        super().__init__(name, contracts, agent,
                         "lib/Subclasses/Device/ModifiedCombinedHeatAndPower/ModifiedCombinedHeatAndPower.json",
                         upstream_aggregators_list, downstream_aggregators_list,
                         profiles, parameters)
        self.CHP_nominal_power = {"LPG": parameters["max_power"],
                                  "LVE": parameters["max_power"] * self._relative_efficiency(1) * self._nominal_efficiency,
                                  "LTH": parameters["max_power"] * self._ratio_correction(1) * self._heat_power_ratio * self._relative_efficiency(1) * self._nominal_efficiency}
        self._max_efficiency = {"LVE": self._relative_efficiency(1) * self._nominal_efficiency,
                                "LTH": self._ratio_correction(1) * self._heat_power_ratio * self._relative_efficiency(1) * self._nominal_efficiency}

        # contracts = {contract.nature.name: contract for contract in contracts}
        # self._upstream_aggregators_list = [{"name": aggregator.name, "nature": aggregator.nature.name, "contract": contracts[aggregator.nature.name]} for aggregator in upstream_aggregators_list]  # list of aggregators involved in the production of energy. The order is not important.
        # self._downstream_aggregators_list = [{"name": aggregator.name, "nature": aggregator.nature.name, "contract": contracts[aggregator.nature.name]} for aggregator in downstream_aggregators_list]  # list of aggregators involved in the consumption of energy. The order is important: the first aggregator defines the final quantity of energy
        #
        # time_step = self._catalog.get("time_step")
        # self._energy_physical_limits = {"minimum_energy": 0, "maximum_energy": parameters["max_power"] * time_step}
        #
        # for aggregator in self._downstream_aggregators_list:
        #     nature_name = aggregator["nature"]
        #     self._catalog.add(f"{self.name}.{nature_name}.efficiency", None)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._nominal_efficiency = data_device["efficiency"]  # the efficiency of the converter for each nature of energy
        self._heat_power_ratio = data_device["heat_power_ratio"]

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _relative_efficiency(self, partial_load):
        efficiency = 0.06 * partial_load**4 \
                     - 0.12 * partial_load**3 \
                     - 0.15 * partial_load**2 \
                     + 0.45 * partial_load \
                     + 0.1
        return efficiency

    def _ratio_correction(self, partial_load):
        ratio = (4.31 * partial_load**2
                 - 6.71 * partial_load
                 + 4.22)
        return ratio

    def _efficiency(self, nature, energy):
        if nature =='LPG':
            if energy < 0:
                energy = energy * -1
            return 1

        elif nature == 'LTH':
            partial_load = (energy / self.CHP_nominal_power["LPG"])
            if energy:
                rend_thermique = self._ratio_correction(partial_load) * self._heat_power_ratio * self._relative_efficiency(partial_load) * self._nominal_efficiency
            else:  # if the CHP is inactive
                rend_thermique = 1
            return rend_thermique

        elif nature == 'LVE':
            partial_load = (energy / self.CHP_nominal_power["LPG"])
            if energy:
                rend_elec = self._relative_efficiency(partial_load) * self._nominal_efficiency
            else:  # if the CHP is inactive
                rend_elec = 1
            return rend_elec

    def _calculate_gas_ratio(self, y_norm, nature):
        def equation_to_solve(partial_load):
            if nature == "LVE":
                f_x = self._relative_efficiency(partial_load)
            elif nature == "LTH":
                f_x = self._ratio_correction(partial_load) * self._relative_efficiency(partial_load)
            return (partial_load * f_x) - y_norm
        try:
            result = root_scalar(equation_to_solve, bracket=[0, 1], method='brentq')
            return result.root
        except ValueError:
            return 0.0

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually
        # downstream side
        for aggregator in self ._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted[nature_name]["energy_minimum"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency(nature_name, self._energy_physical_limits["minimum_energy"])  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency(nature_name, self._energy_physical_limits["minimum_energy"])  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = - self._energy_physical_limits["maximum_energy"] * self._efficiency(nature_name, self._energy_physical_limits["maximum_energy"] )  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["efficiency"] = self._efficiency(nature_name, self._energy_physical_limits["maximum_energy"] )

        # upstream side
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted[nature_name]["energy_minimum"] = self._energy_physical_limits["minimum_energy"] / self._efficiency(nature_name, self._energy_physical_limits["minimum_energy"])  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = self._energy_physical_limits["minimum_energy"] / self._efficiency(nature_name, self._energy_physical_limits["minimum_energy"])  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = self._energy_physical_limits["maximum_energy"] / self._efficiency(nature_name, self._energy_physical_limits["maximum_energy"])  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["efficiency"] = self._efficiency(nature_name, self._energy_physical_limits["maximum_energy"])

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def second_update(self):  # todo special case for RL since we can't ask a different action during the same state (step)
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        # determination of the energy consumed/produced
        energy_wanted_downstream = {}
        energy_available_upstream = {}
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            gas_ratio = self._calculate_gas_ratio(self._max_efficiency[nature_name] * (-self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"] / self.CHP_nominal_power[nature_name]), nature_name)
            energy_wanted_downstream[nature_name] = gas_ratio * self.CHP_nominal_power["LPG"]  # the energy asked by the downstream aggregator
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_available_upstream[nature_name] = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")["quantity"] / self._nominal_efficiency  # the energy accorded by the upstream aggregator

        tau, switch_signal = self.identify_priority()
        if tau is None:
            limit_energy_upstream = min(energy_available_upstream.values())
            limit_energy_downstream = min(energy_wanted_downstream.values())
            raw_energy_transformed = min(limit_energy_upstream, limit_energy_downstream)
        else:
            if tau < switch_signal:  # priority to the DHN
                raw_energy_transformed = energy_wanted_downstream["LTH"]
            else:  # priority to the EMG
                raw_energy_transformed = energy_wanted_downstream["LVE"]

        # downstream side
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]

            # resetting the demand
            energy_wanted[nature_name]["energy_minimum"] = - raw_energy_transformed * self._efficiency(nature_name,  raw_energy_transformed)  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = - raw_energy_transformed * self._efficiency(nature_name,  raw_energy_transformed)  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = - raw_energy_transformed * self._efficiency(nature_name,  raw_energy_transformed)  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["price"] = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["price"]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name]["efficiency"] = self._efficiency(nature_name, raw_energy_transformed )

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"] = - raw_energy_transformed * self._efficiency(nature_name,  raw_energy_transformed)
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

        # upstream side
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]

            # resetting the demand
            energy_wanted[nature_name]["energy_minimum"] = raw_energy_transformed / self._efficiency(nature_name, raw_energy_transformed)  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = raw_energy_transformed / self._efficiency(nature_name, raw_energy_transformed)  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = raw_energy_transformed / self._efficiency(nature_name, raw_energy_transformed)  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["price"] = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["price"]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name]["efficiency"] = self._efficiency (nature_name, raw_energy_transformed)

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"] = raw_energy_transformed / self._efficiency(nature_name, raw_energy_transformed)
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

    def react(self):
        for nature in self.natures:
            energy_wanted = self.get_energy_wanted(nature)
            energy_accorded = self.get_energy_accorded(nature)
            [energy_accorded, energy_erased, energy_bought, energy_sold, money_earned, money_spent] = \
            self.natures[nature]["contract"].billing(energy_wanted, energy_accorded,
                                                     self.name)  # the contract may adjust things
            self.set_energy_accorded(nature, energy_accorded)
            # print(self.name, energy_accorded)

            # update of the data at the level of the device
            self._catalog.set(f"{self.name}.{nature.name}.energy_erased", energy_erased)  # TODO: à faire comptabiliser par les contrats
            self._catalog.set(f"{self.name}.{nature.name}.energy_bought", energy_bought)
            self._catalog.set(f"{self.name}.{nature.name}.energy_sold", energy_sold)
            self._catalog.set(f"{self.name}.{nature.name}.money_earned", money_earned)
            self._catalog.set(f"{self.name}.{nature.name}.money_spent", money_spent)

        if self._moment is not None:
            self._moment = (self._moment + 1) % self._period  # incrementing the hour in the period

        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            self._catalog.set(f"{self.name}.{nature_name}.efficiency", self._efficiency(nature_name, -self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"]))
            # print(self._catalog.get(f"{self.name}.{nature_name}.efficiency"))



