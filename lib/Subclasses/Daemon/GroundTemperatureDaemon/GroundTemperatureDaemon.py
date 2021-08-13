# this daemon is designed to calculate a very unaccurate dynamic temperature of the cold water in housings during a year.
from json import load
from datetime import datetime
from src.common.Daemon import Daemon
from src.tools.ReadingFunctions import get_1_values_per_month


class GroundTemperatureDaemon(Daemon):

    def __init__(self, parameters, filename="lib/Subclasses/Daemon/GroundTemperatureDaemon/TemperatureProfiles.json"):
        self._location = parameters["location"]  # the location corresponding to the data

        name = "ground_temperature_in_" + self._location
        super().__init__(name, 1, parameters, filename)

        file = open(filename, "r")
        data = load(file)[self._location]
        file.close()

        self._temperatures = data["temperatures"]
        self._format = data["format"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"1/month": get_1_values_per_month}  # 1 representative temperature for each month
        self._get_ground_temperature = self._files_formats[self._format]

        # initialization of the value
        self._catalog.add(f"{self._location}.ground_temperature", self._get_ground_temperature(self._temperatures, self._catalog))

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self._location}.ground_temperature", self._get_ground_temperature(self._temperatures, self._catalog))

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def location(self):
        return self._location


