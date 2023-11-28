# this daemon is designed to manage the flow of a given river, in m3.s-1
from lib.Subclasses.Daemon.DataReadingDaemon.DataReadingDaemon import DataReadingDaemon


class WaterFlowDaemon(DataReadingDaemon):
    def __init__(self, parameters, period=1, filename="lib/Subclasses/Daemon/WaterFlowDaemon/WaterFlowProfiles.json"):
        name = "water_flow_in_"
        super().__init__(name, period, parameters, filename)

        # non updated values
        self._catalog.add(f"{self._location}.reserved_flow", self._data["reserved_flow"])
        self._catalog.add(f"{self._location}.max_flow", self._data["max_flow"])

        # updated values
        self._managed_keys = [("flow", f"{self._location}.flow_value", "extensive")]
        self._initialize_managed_keys()


