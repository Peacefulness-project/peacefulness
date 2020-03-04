# This device represents all the devices that are not explicitly described otherwise because one or several of the following reasons:
# - they are rare;
# - they don't consume a lot of energy nor they have an important power demand;
# - patterns of use or of consumption are difficult to model;
# - they are non-controllable, i.e the supervisor has no possibility to interact with them.

from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Background(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, aggregators, "usr/DevicesProfiles/Background.json", user_profile_name, usage_profile_name, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _get_consumption(self):
        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        beginning = self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        consumption_variation = self._catalog.get("gaussian")(1, data_device["consumption_variation"])  # modification of the consumption
        for nature in data_device["usage_profile"]:
            for i in range(len(data_device["usage_profile"][nature]["weekday"])):
                data_device["usage_profile"][nature]["weekday"][i] *= consumption_variation
            for i in range(len(data_device["usage_profile"][nature]["weekend"])):
                data_device["usage_profile"][nature]["weekend"][i] *= consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        # usage profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        self._usage_profile = dict()
        for nature in data_device["usage_profile"]:  # data_usage is then added for each nature used by the device
            self._usage_profile[nature] = list()
            self._usage_profile[nature] = 5 * data_device["usage_profile"][nature]["weekday"] + \
                                          2 * data_device["usage_profile"][nature]["weekend"]

        self._unused_nature_removal()  # remove unused natures

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self._usage_profile.keys()}  # consumption that will be asked eventually

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = self._usage_profile[nature][self._moment]  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_nominal"] = self._usage_profile[nature][self._moment]  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_maximum"] = self._usage_profile[nature][self._moment]  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


user_classes_dictionary[f"{Background.__name__}"] = Background


