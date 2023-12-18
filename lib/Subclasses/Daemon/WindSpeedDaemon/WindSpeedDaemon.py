# this daemon is designed to manage the price of a given energy for sellers or buyers
from lib.Subclasses.Daemon.DataReadingDaemon.DataReadingDaemon import DataReadingDaemon


class WindSpeedDaemon(DataReadingDaemon):

    def __init__(self, parameters, filename="lib/Subclasses/Daemon/WindSpeedDaemon/WindSpeedProfiles.json"):
        name = "wind_speed_in_"
        super().__init__(name, 1, parameters, filename)

        # non updated values
        self._catalog.add(f"{self._location}.height_ref", self._data["height_ref"])  # m

        # updated values
        self._managed_keys = [("wind_speed", f"{self.location}.wind_value", "intensive")]  # m.s-1
        self._initialize_managed_keys()


