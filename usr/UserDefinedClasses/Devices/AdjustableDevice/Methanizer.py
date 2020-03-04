from common.DeviceMainClasses import AdjustableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Methanizer(AdjustableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, aggregators, "usr/DevicesProfiles/Methanizer.json", user_profile_name, usage_profile_name, parameters)


user_classes_dictionary[f"{Methanizer.__name__}"] = Methanizer

