# device representing a dummy production unit with a ramping constraint
from src.common.DeviceMainClasses import NonControllableDevice


class DummyRampingProducer(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/DummyRampingProducer/DummyRampingProducer.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step   # the maximum power this device can produce

        self._load_level = parameters["initial_load_level"]  # the level of usage at the previous time step
        self._ramping_speed = parameters["ramping_speed"]  # the flexibility of the device to change its power delivery

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()
        self._efficiency = None

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually
        time_step = self._catalog.get("time_step")

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = - min(0, self._load_level - self._max_power * self._ramping_speed * time_step)  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = - min(0, self._load_level - self._max_power * self._ramping_speed * time_step)  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - min(self._max_power, self._load_level + self._max_power * self._ramping_speed * time_step)  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


