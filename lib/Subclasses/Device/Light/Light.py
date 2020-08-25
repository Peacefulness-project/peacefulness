from src.common.DeviceMainClasses import NonControllableDevice


class Light(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/Light/Light.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)




