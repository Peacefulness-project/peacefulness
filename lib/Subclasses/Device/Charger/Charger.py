from src.common.DeviceMainClasses import ChargerDevice


class Charger(ChargerDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/Charger/Charger.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters=None)


