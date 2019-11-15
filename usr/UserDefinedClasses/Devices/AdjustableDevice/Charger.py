from common.DeviceMainClasses import ChargerDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Charger(ChargerDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/Charger.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)


user_classes_dictionary[f"{Charger.__name__}"] = Charger


