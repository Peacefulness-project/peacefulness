# device representing a photovoltaic panel
from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class GenericProducer(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/WindTurbine.json", user_profile_name, usage_profile_name, None)

        self._usage_profile = dict()

        self._efficiency = None

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        pass

    def _get_consumption(self):
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
        energy_wanted = {nature.name: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self.natures}  # consumption that will be asked eventually

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - self._max_power  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


user_classes_dictionary[f"{GenericProducer.__name__}"] = GenericProducer
