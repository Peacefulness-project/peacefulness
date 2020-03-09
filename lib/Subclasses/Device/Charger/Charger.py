from src.common.DeviceMainClasses import ChargerDevice


class Charger(ChargerDevice):

    def __init__(self, world, name, contracts, agent, aggregators, user_profile_name, usage_profile_name):
        super().__init__(world, name, contracts, agent, aggregators, "lib/Subclasses/Device/Charger/Charger.json", user_profile_name, usage_profile_name)


