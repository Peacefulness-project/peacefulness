# This subclass of Converter is supposed to represent a combined heat and power device. Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter


class CombinedHeatAndPower(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregator, profiles, parameters=None, filename="lib/Subclasses/Device/HeatPump/CombinedHeatAndPower.json"):
        super().__init__(name, contracts, agent, filename, upstream_aggregator, downstream_aggregator, profiles, parameters)





