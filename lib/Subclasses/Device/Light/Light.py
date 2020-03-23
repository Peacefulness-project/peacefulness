from src.common.DeviceMainClasses import NonControllableDevice


class Light(NonControllableDevice):

    def __init__(self, world, name, contracts, agent, aggregators, user_profile_name, usage_profile_name=None):
        super().__init__(world, name, contracts, agent, aggregators, "lib/Subclasses/Device/Light/Light.json", user_profile_name, usage_profile_name)



