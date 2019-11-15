from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Hob(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/Hob.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)


user_classes_dictionary[f"{Hob.__name__}"] = Hob

