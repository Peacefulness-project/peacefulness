from src.common.DeviceMainClasses import ChargerDevice


class Charger(ChargerDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "lib/Subclasses/Device/Charger/Charger.json", user_profile_name, usage_profile_name, parameters)


