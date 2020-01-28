from common.DeviceMainClasses import ChargerDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Charger(ChargerDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "usr/DevicesProfiles/Charger.json", user_profile_name, usage_profile_name, parameters)


user_classes_dictionary[f"{Charger.__name__}"] = Charger


