from src.common.DeviceMainClasses import ShiftableDevice


class WashingMachine(ShiftableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/WashingMachine/WashingMachine.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)



