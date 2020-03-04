from common.DeviceMainClasses import ShiftableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class WashingMachine(ShiftableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, aggregators, "usr/DevicesProfiles/WashingMachine.json", user_profile_name, usage_profile_name, parameters)


user_classes_dictionary[f"{WashingMachine.__name__}"] = WashingMachine

