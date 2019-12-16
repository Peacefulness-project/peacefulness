from common.DeviceMainClasses import ShiftableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Dishwasher(ShiftableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/Dishwasher.json", user_profile_name, usage_profile_name, parameters)


user_classes_dictionary[f"{Dishwasher.__name__}"] = Dishwasher


