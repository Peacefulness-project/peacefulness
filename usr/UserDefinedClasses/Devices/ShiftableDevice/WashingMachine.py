from common.DeviceMainClasses import ShiftableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class WashingMachine(ShiftableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/WashingMachine.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)


user_classes_dictionary[f"{WashingMachine.__name__}"] = WashingMachine

