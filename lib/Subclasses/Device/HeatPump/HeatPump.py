# This subclass of Converter is supposed to represent a heat pump. Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter


class HeatPump(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregator, technical_profile_name, filename="lib/Subclasses/Device/HeatPump/HeatPump.json"):
        super().__init__(name, contracts, agent, filename, upstream_aggregator, downstream_aggregator, technical_profile_name)


