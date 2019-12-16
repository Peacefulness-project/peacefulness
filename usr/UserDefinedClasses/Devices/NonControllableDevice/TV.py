from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class TV(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/TV.json", user_profile_name, usage_profile_name, parameters)


user_classes_dictionary[f"{TV.__name__}"] = TV

