from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class VacuumCleaner(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/VacuumCleaner.json", user_profile_name, usage_profile_name)


user_classes_dictionary[f"{VacuumCleaner.__name__}"] = VacuumCleaner

