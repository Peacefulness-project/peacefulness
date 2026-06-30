# This subclass of Converter is supposed to represent a district heating network.
# It is useful to represent the information about the DHN flexibility.

# Imports
from src.common.Device import Device
from src.common.Messages import MessagesManager
import numpy as np
from math import floor, pi
from copy import deepcopy
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import round_custom


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
        self.T_set = parameters["set_T°"]
        temperature_daemon = self._catalog.daemons[parameters["outdoor_temperature_daemon"]]
        self._location = temperature_daemon.location
        self._water_volume = pi * (parameters["pipe_diameter"] ** 2) * parameters["network_length"] / 4
        self._cp = 1.1628  # chaleur specifique kWh/°k.m^3
        self._nominal_power = parameters["rng_generator"](self._water_volume * self._cp * parameters["delta_T"])
        self._flexible_energy = 0.0
        self._energy_to_restitute = 0.0
        self.t0 = None
        self._catalog.add(f"{self.name}.flexibility_offset", 0.0)

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
            if self.t0 and self._flexible_energy < self._nominal_power:  # going from T°_set -> T°_min (priority to EMG)
                energy_wanted[nature_name]["energy_minimum"] = 0.0  # energy needed for all natures used by the device
                energy_wanted[nature_name]["energy_nominal"] = 0.0  # energy needed for all natures used by the device
                energy_wanted[nature_name]["energy_maximum"] = self._water_volume * self._cp * (self.T_set - self._catalog.get(f"{self._location}.current_outdoor_temperature"))
                energy_wanted[nature_name]["flexibility"] = [1]
                energy_wanted[nature_name]["interruptibility"] = 1
                energy_wanted[nature_name]["coming_volume"] = self._nominal_power - self._flexible_energy
                # print(f"during descent flexibility -> {current_time}")

                energy_wanted[nature_name]["priority"] = self.device_aggregators[0].superior.name

            elif self.t0 and self._flexible_energy >= self._nominal_power:  # going back from T°_min -> T°_set (priority to DHN)
                energy_wanted[nature_name]["energy_minimum"] = self._water_volume * self._cp * (self.T_set - self._catalog.get(f"{self._location}.current_outdoor_temperature"))
                energy_wanted[nature_name]["energy_nominal"] = self._water_volume * self._cp * (self.T_set - self._catalog.get(f"{self._location}.current_outdoor_temperature"))
                energy_wanted[nature_name]["energy_maximum"] = self._water_volume * self._cp * (self.T_set - self._catalog.get(f"{self._location}.current_outdoor_temperature"))
                energy_wanted[nature_name]["flexibility"] = [1]
                energy_wanted[nature_name]["interruptibility"] = 1
                energy_wanted[nature_name]["coming_volume"] = self._nominal_power - self._energy_to_restitute
                # print(f"during ascent -> {current_time}")

                energy_wanted[nature_name]["priority"] = self.device_aggregators[0].name

            elif not self.t0:
                energy_wanted[nature_name]["energy_minimum"] = 0.0  # energy needed for all natures used by the device
                energy_wanted[nature_name]["energy_nominal"] = 0.0  # energy needed for all natures used by the device
                energy_wanted[nature_name]["energy_maximum"] = 0.0
                energy_wanted[nature_name]["flexibility"] = [1]
                energy_wanted[nature_name]["interruptibility"] = 1
                energy_wanted[nature_name]["coming_volume"] = 0.0
                # print(f"nominal state -> {current_time}")

                energy_wanted[nature_name]["priority"] = self.device_aggregators[0].superior.name
            # print(energy_wanted)
            # TODO maybe à enlever et laisser juste la priorité en fonction de l'Energy_flexible ?
            # if not self.t0:
            #     energy_wanted[nature_name]["priority"] = self.device_aggregators[0].superior.name
            # elif current_time <= self.t0 + self._tau_1:
            #     energy_wanted[nature_name]["priority"] = self.device_aggregators[0].superior.name
            # else:
            #     energy_wanted[nature_name]["priority"] = self.device_aggregators[0].name
            # print(f"who is prior at {current_time} : {energy_wanted[nature_name]["priority"]}")

        # if f"{self.name}.priority_tau" in self._catalog.keys:
        #     self._catalog.set(f"{self.name}.priority_tau", self._tau_1 - self._switch)
        # else:
        #     self._catalog.add(f"{self.name}.priority_tau", self._tau_1 - self._switch)


        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog
        # print(energy_wanted['LTH']["priority"])


    def react(self):
        super().react()  # actions needed for all the devices

        # updating the partial loads and flexibility of the network
        current_time = self._catalog.get("simulation_time")
        aggregators = self.device_aggregators
        for aggregator in aggregators:
            # evaluating the flexibility of the heat network (parametrized by tau_1)
            energy_supply = self._catalog.get(f"{aggregator.name}.energy_bought")
            self.loads_log.append(energy_supply["inside"] / self._nominal_power)  # partial supplied load
            self._tau_1 = min(
                np.interp(self.loads_log[-1], self._diameter["partial_loads"], self._diameter["tau_1"]),
                np.interp(self.loads_log[-1], self._length["partial_loads"], self._length["tau_1"])
            )
            self._tau_1 = round_custom(self._tau_1 / 3600)

            if self._tau_1 <= self._switch and not self.t0:  # signal of DHN flexibility use
                self.t0 = current_time
                # print(f"T_set not maintained -> {self._tau_1, self._switch} at time {self.t0}")

            # todo final way
            if self.t0:
                energy_given = self.get_energy_accorded_quantity(aggregator.nature)
                # print(f"previously given -> {energy_given}")
                energy_wanted_by_DHN = self.get_energy_wanted_max(aggregator.nature)
                # print(f"energy asked -> {energy_wanted_by_DHN}")
                # print(f"nom power -> {self._nominal_power}")
                if self._flexible_energy < self._nominal_power:
                    self._flexible_energy += energy_wanted_by_DHN - energy_given
                    # print(f"flex E -> {self._flexible_energy}")
                else:  # if T°_min is reached
                    # print(f"flexibility finished at {current_time}")
                    self._energy_to_restitute += energy_wanted_by_DHN
                    # print(f"rest E -> {self._energy_to_restitute}")
                # DHN got back to its nominal set T°
                if self._flexible_energy >= self._nominal_power and self._energy_to_restitute >= self._nominal_power:
                    # print(f"DHN got back to nominal -> {current_time}")
                    self.t0 = None
                    self._flexible_energy = 0.0
                    self._energy_to_restitute = 0.0
                    flex_offset = max(self._flexible_energy - self._energy_to_restitute, 0.0)
                    self._catalog.set(f"{self.name}.flexibility_offset", flex_offset / self._nominal_power)


    @property
    def get_flexibility(self):
        return self._tau_1

    @property
    def get_switch(self):
        return self._switch



