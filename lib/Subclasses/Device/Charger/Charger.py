from src.common.DeviceMainClasses import ChargerDevice


class Charger(ChargerDevice):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, filename="lib/Subclasses/Device/Charger/Charger.json"):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name)


