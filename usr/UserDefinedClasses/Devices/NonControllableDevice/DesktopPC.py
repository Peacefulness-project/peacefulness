from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class DesktopPC(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/DesktopPC.json", user_profile_name, usage_profile_name)


user_classes_dictionary[f"{DesktopPC.__name__}"] = DesktopPC
