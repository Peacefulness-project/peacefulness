# This subclass of Converter is supposed to represent a district heating network.
# It is useful to represent the information about the DHN flexibility.

# Imports
from src.common.Device import Device
from src.common.Messages import MessagesManager
import numpy as np
from math import floor


class DummyHeatNetwork(Device):
    messages_manager = MessagesManager()
    messages_manager.complete_information_message("flexibility", [])  # -, indicates the level of flexibility on the latent concumption or production
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

        self.loads_log = [0.0]
        self._tau_1 = 0
        self._nominal_power = parameters["rng_generator"](parameters["nominal_power"])
        self._switch = parameters["switch"]
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

        for nature_name in energy_wanted:
            energy_wanted[nature_name]["energy_minimum"] = 0.0  # energy needed for all natures used by the device
            energy_wanted[nature_name]["energy_nominal"] = 0.0  # energy needed for all natures used by the device
            energy_wanted[nature_name]["energy_maximum"] = 0.0  # energy needed for all natures used by the device
            energy_wanted[nature_name]["flexibility"] = [1]
            energy_wanted[nature_name]["interruptibility"] = 1
            if len(self.loads_log) >= 2:
                energy_wanted[nature_name]["coming_volume"] = (self._tau_1 - 1) * abs(self.loads_log[-1] - self.loads_log[-2]) if self._tau_1 > 0 else self._tau_1 * abs(self.loads_log[-1] - self.loads_log[-2])
            else:
                energy_wanted[nature_name]["coming_volume"] = (self._tau_1 - 1) * self.loads_log[-1] if self._tau_1 > 0 else self._tau_1 * self.loads_log[-1]

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


    def react(self):
        super().react()  # actions needed for all the devices

        # updating the partial loads and flexibility of the network
        aggregators = self.device_aggregators
        for aggregator in aggregators:
            for subaggregator in aggregator.subaggregators:  # todo patchwork solution (just 1 DHN subaggregator)
                energy_sold = self._catalog.get(f"{subaggregator.name}.energy_bought")
                self.loads_log.append(energy_sold["inside"] / self._nominal_power)
                self._tau_1 = min(
                    np.interp(self.loads_log[-1], self._diameter["partial_loads"], self._diameter["tau_1"]),
                    np.interp(self.loads_log[-1], self._length["partial_loads"], self._length["tau_1"])
                )
                self._tau_1 = floor(self._tau_1 / 3600)

    @property
    def get_flexibility(self):
        return self._tau_1

    @property
    def get_switch(self):
        return self._switch
