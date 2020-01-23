from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Hob(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/Hob.json", user_profile_name, usage_profile_name, parameters)


user_classes_dictionary[f"{Hob.__name__}"] = Hob

