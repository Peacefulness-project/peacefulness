from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Microwave(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/Microwave.json", user_profile_name, usage_profile_name, parameters)


user_classes_dictionary[f"{Microwave.__name__}"] = Microwave

