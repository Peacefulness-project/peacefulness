from src.common.DeviceMainClasses import NonControllableDevice


class Light(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile, technical_profile, filename="lib/Subclasses/Device/Light/Light.json"):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile, technical_profile)




