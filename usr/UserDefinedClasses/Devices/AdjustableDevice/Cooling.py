from common.DeviceMainClasses import AdjustableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Cooling(AdjustableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/Cooling.json", user_profile_name, usage_profile_name, parameters)


user_classes_dictionary[f"{Cooling.__name__}"] = Cooling

