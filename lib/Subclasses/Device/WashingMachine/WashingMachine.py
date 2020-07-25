from src.common.DeviceMainClasses import ShiftableDevice


class WashingMachine(ShiftableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile, technical_profile, filename="lib/Subclasses/Device/WashingMachine/WashingMachine.json"):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile, technical_profile)



