from src.common.DeviceMainClasses import ShiftableDevice


class Dishwasher(ShiftableDevice):

    def __init__(self, world, name, contracts, agent, aggregators, user_profile_name, usage_profile_name=None):
        super().__init__(world, name, contracts, agent, aggregators, "lib/Subclasses/Device/Dishwasher/Dishwasher.json", user_profile_name, usage_profile_name)




