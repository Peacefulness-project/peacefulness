# This class represents devices whose main activity is to heat water, like coffee makers or kettles.

from common.DeviceMainClasses import ShiftableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class WaterHeater(ShiftableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/WaterHeater.json", user_profile_name, usage_profile_name)


user_classes_dictionary[f"{WaterHeater.__name__}"] = WaterHeater


