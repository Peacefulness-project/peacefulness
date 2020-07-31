from src.common.DeviceMainClasses import ShiftableDevice


class Dryer(ShiftableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, filename="lib/Subclasses/Device/Dryer/Dryer.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles)



