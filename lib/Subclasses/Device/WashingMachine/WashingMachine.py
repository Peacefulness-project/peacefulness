from src.common.DeviceMainClasses import ShiftableDevice


class WashingMachine(ShiftableDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, aggregators, "lib/Subclasses/Device/WashingMachine/WashingMachine.json", user_profile_name, usage_profile_name, parameters)



