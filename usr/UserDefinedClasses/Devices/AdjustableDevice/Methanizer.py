from common.DeviceMainClasses import AdjustableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Methanizer(AdjustableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/Methanizer.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)


user_classes_dictionary[f"{Methanizer.__name__}"] = Methanizer

