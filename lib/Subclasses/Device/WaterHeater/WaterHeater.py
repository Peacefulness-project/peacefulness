# This class represents devices whose main activity is to heat water, like coffee makers or kettles.

from src.common.DeviceMainClasses import ShiftableDevice


class WaterHeater(ShiftableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/WaterHeater/WaterHeater.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)




