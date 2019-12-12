# device representing a photovoltaic panel
from common.DeviceMainClasses import NonControllableDevice
from math import sin, pi
from tools.UserClassesDictionary import user_classes_dictionary


class PV(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, "usr/DevicesProfiles/PV.json", clusters, user_profile_name, usage_profile_name)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        for line in self._user_profile:
            solar_prod = sin((line[0] - 8.5) * pi / 9) * line[1]
            line[1] = max(0, solar_prod)


user_classes_dictionary[f"{PV.__name__}"] = PV





