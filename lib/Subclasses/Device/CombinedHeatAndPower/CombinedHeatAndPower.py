# This subclass of Converter is supposed to represent a combined heat and power device. Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter


class CombinedHeatAndPower(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregators, profiles, parameters, filename="lib/Subclasses/Device/HeatPump/CombinedHeatAndPower.json"):
        time_step = self._catalog.get("time_step")
        self._max_power = parameters["max_power"] * time_step  # max power

        super().__init__(name, contracts, agent, filename, upstream_aggregator, downstream_aggregators, profiles, parameters)





