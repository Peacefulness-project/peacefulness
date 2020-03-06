from src.common.DeviceMainClasses import NonControllableDevice


class Light(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, clusters, "lib/Subclasses/Device/Light/Light.json", user_profile_name, usage_profile_name, parameters)




