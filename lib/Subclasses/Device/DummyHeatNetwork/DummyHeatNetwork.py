# This subclass of Converter is supposed to represent a district heating network.
# It is useful to represent the information about the DHN flexibility.

# Imports
from src.common.Device import Device
from src.common.Messages import MessagesManager
import numpy as np
from math import floor
from copy import deepcopy


class DummyHeatNetwork(Device):
    messages_manager = MessagesManager()
    messages_manager.complete_information_message("flexibility", [])  # -, indicates the level of flexibility on the latent consumption or production
    messages_manager.complete_information_message("interruptibility", 0)  # -, indicates if the device is interruptible
    messages_manager.complete_information_message("coming_volume", 0)  # kWh, gives an indication on the latent consumption or production
    messages_manager.set_type("standard")
    information_message = messages_manager.create_information_message
    decision_message = messages_manager.create_decision_message
    information_keys = messages_manager.information_keys
    decision_keys = messages_manager.decision_keys

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/DummyHeatNetwork/DummyHeatNetwork.json"):
        self._diameter = parameters["pipe_diameter"]
        self._length = parameters["network_length"]
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self.loads_log = []
        self._tau_1 = parameters["tau_init"]
        self._switch = parameters["switch"]
        self.flexibility_until = max(self._tau_1 - self._switch, 0)
        self._nominal_power = parameters["rng_generator"](parameters["nominal_power"])  # max heat supply power/energy
        self._backpower = parameters["rng_generator"](parameters["flex_power"])  # necessary power to get DHN back to Tset if heat supply is null
        self._necessary_power = deepcopy(self._backpower)
        # temperature_daemon = self._catalog.daemons[parameters["outdoor_temperature_daemon"]]
        # self._location = temperature_daemon.location

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profile):
        data_device = self._read_technical_data(profile["device"])  # parsing the data
        diam_partial_loads = data_device["diameter"][str(self._diameter)]["partial_load"]
        diam_tau1 = data_device["diameter"][str(self._diameter)]["tau_1"]
        len_partial_loads = data_device["length"][str(self._length)]["partial_load"]
        len_tau1 = data_device["length"][str(self._length)]["tau_1"]
        self._diameter = {"partial_loads": diam_partial_loads,
                          "tau_1": diam_tau1}
        self._length = {"partial_loads": len_partial_loads,
                        "tau_1": len_tau1}

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually
        current_time = self._catalog.get("simulation_time")
        for nature_name in energy_wanted:
            if current_time < self.flexibility_until:  # if the DHN offers flexibility
                energy_wanted[nature_name]["energy_minimum"] = 0.0  # energy needed for all natures used by the device
                energy_wanted[nature_name]["energy_nominal"] = 0.0  # energy needed for all natures used by the device
                energy_wanted[nature_name]["energy_maximum"] = self._necessary_power * current_time / self.flexibility_until # energy needed for all natures used by the device
                energy_wanted[nature_name]["flexibility"] = [1]
                energy_wanted[nature_name]["interruptibility"] = 1
                energy_wanted[nature_name]["coming_volume"] = self._necessary_power

            # elif current_time == self.flexibility_until:
            #     energy_wanted[nature_name]["energy_minimum"] = 0.0  # energy needed for all natures used by the device
            #     energy_wanted[nature_name]["energy_nominal"] = self._necessary_power * 0.5  # energy needed for all natures used by the device
            #     energy_wanted[nature_name]["energy_maximum"] = self._necessary_power  # energy needed for all natures used by the device
            #     energy_wanted[nature_name]["flexibility"] = [1]
            #     energy_wanted[nature_name]["interruptibility"] = 1
            #     energy_wanted[nature_name]["coming_volume"] = self._necessary_power * 0.5

            else:
                energy_wanted[nature_name]["energy_minimum"] = self._necessary_power * (current_time - self.flexibility_until) / self.delta_t  # energy needed for all natures used by the device
                energy_wanted[nature_name]["energy_nominal"] = self._necessary_power * (current_time - self.flexibility_until) / self.delta_t  # energy needed for all natures used by the device
                energy_wanted[nature_name]["energy_maximum"] = self._necessary_power * (current_time - self.flexibility_until) / self.delta_t  # energy needed for all natures used by the device
                energy_wanted[nature_name]["flexibility"] = [0]
                energy_wanted[nature_name]["interruptibility"] = 0
                energy_wanted[nature_name]["coming_volume"] = self._necessary_power


            if self._tau_1 < self._switch:
                energy_wanted[nature_name]["priority"] = self.device_aggregators[0].name
            elif self._tau_1 > self._switch:
                energy_wanted[nature_name]["priority"] = self.device_aggregators[0].superior.name
            else:
                energy_wanted[nature_name]["priority"] = "any"


        if f"{self.name}.priority_tau" in self._catalog.keys:
            self._catalog.set(f"{self.name}.priority_tau", self._tau_1 - self._switch)
        else:
            self._catalog.add(f"{self.name}.priority_tau", self._tau_1 - self._switch)


        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


    def react(self):
        super().react()  # actions needed for all the devices

        # updating the partial loads and flexibility of the network
        current_time = self._catalog.get("simulation_time")
        aggregators = self.device_aggregators
        for aggregator in aggregators:
            # energy needed to get the heat network back to its nominal state
            energy_given_to_DHN = self.get_energy_accorded_quantity(aggregator.nature)  # energy accorded to the network
            energy_wanted_by_DHN = self.get_energy_wanted_max(aggregator.nature)

            if current_time < self.flexibility_until:
                self._necessary_power = max(0.0, energy_wanted_by_DHN - energy_given_to_DHN)
            else:
                self._necessary_power = self._backpower

            # evaluating the flexibility of the heat network (parametrized by tau_1)
            energy_sold = self._catalog.get(f"{aggregator.name}.energy_bought")
            self.loads_log.append(energy_sold["inside"] / self._nominal_power)  # partial supplied load
            self._tau_1 = min(
                np.interp(self.loads_log[-1], self._diameter["partial_loads"], self._diameter["tau_1"]),
                np.interp(self.loads_log[-1], self._length["partial_loads"], self._length["tau_1"])
            )
            self._tau_1 = floor(self._tau_1 / 3600)

            # todo old way
            # if self._tau_1 > self._switch:  # thermal inertia of the DHN is enough to retain Tset
            #     new_until = current_time + (self._tau_1 - self._switch)
            #     self.flexibility_until = max(self.flexibility_until, new_until)

            # todo new way
            if self._tau_1 < self._switch:
                self.delta_t = self._tau_1
                self.flexibility_until = current_time + self._tau_1
            else:
                self._necessary_power = 0.0
                


    @property
    def get_flexibility(self):
        return self._tau_1

    @property
    def get_switch(self):
        return self._switch
