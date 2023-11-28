# this daemon is designed to calculate a very unaccurate dynamic temperature of the cold water in housings during a year.
from lib.Subclasses.Daemon.DataReadingDaemon.DataReadingDaemon import DataReadingDaemon


class ColdWaterTemperatureDaemon(DataReadingDaemon):

    def __init__(self, parameters, filename="lib/Subclasses/Daemon/ColdWaterTemperatureDaemon/TemperatureProfiles.json"):

        name = "cold_water_temperature_in_"
        super().__init__(name, 1, parameters, filename)

        self._managed_keys = [("temperatures", f"{self._location}.cold_water_temperature", "intensive")]

        self._initialize_managed_keys()


