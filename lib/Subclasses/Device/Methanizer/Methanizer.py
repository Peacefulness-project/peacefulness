from src.common.DeviceMainClasses import AdjustableDevice


class Methanizer(AdjustableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, filename="lib/Subclasses/Device/Methanizer/Methanizer.json"):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self):
        self._usage_profile = dict()
        self._efficiency = None

        [data_user, data_device] = self._read_consumption_data()  # getting back the profiles

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # usage profile
        self._usage_profile[data_device["usage_profile"]["nature"]] = None

        self._max_power = data_device["usage_profile"]["max_power"]  # max power

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - self._max_power  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog





