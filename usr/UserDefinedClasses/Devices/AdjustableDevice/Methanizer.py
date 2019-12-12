from common.DeviceMainClasses import AdjustableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Methanizer(AdjustableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/Methanizer.json", user_profile_name, usage_profile_name)


user_classes_dictionary[f"{Methanizer.__name__}"] = Methanizer

