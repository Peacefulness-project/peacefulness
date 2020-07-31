from src.common.DeviceMainClasses import ShiftableDevice


class Dishwasher(ShiftableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, filename="lib/Subclasses/Device/Dishwasher/Dishwasher.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles)




