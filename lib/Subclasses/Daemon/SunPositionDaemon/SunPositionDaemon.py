# this daemon is designed to atualize the value of the sun position in the sky.
from lib.Subclasses.Daemon.DataReadingDaemon.DataReadingDaemon import DataReadingDaemon


class SunPositionDaemon(DataReadingDaemon):

    def __init__(self, parameters, period=1, filename="lib/Subclasses/Daemon/SunPositionDaemon/SunPositionProfiles.json"):
        name = "sun_position_in_"
        super().__init__(name, period, parameters, filename)

        self._managed_keys = [("azimut", f"{self.location}.azimut", "intensive"),
                              ("sun_height", f"{self.location}.sun_height", "intensive"),
                              ]

        self._initialize_managed_keys()




