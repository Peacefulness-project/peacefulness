# this daemon is designed to calculate a very unaccurate dynamic temperature of the cold water in housings during a year.
from json import load
from datetime import datetime
from src.common.Daemon import Daemon


class ColdWaterDaemon(Daemon):

    def __init__(self, world, name, parameters, period=1):
        super().__init__(world, name, period, parameters)

        self._location = parameters["location"]  # the location corresponding to the data

        # getting the data for the chosen location
        file = open("lib/Subclasses/Daemon/ColdWaterDaemon/TemperatureProfiles.json", "r")
        data = load(file)[self._location]
        file.close()

        self._temperatures = data["temperatures"]
        self._format = data["format"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"1/month": self._get_1_temperature_per_month}  # 1 representative temperature for each month
        self._get_water_temperature = self._files_formats[self._format]

        # initialization of the value
        self._catalog.add(f"{self._location}.cold_water_temperature", self._get_water_temperature())

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self._location}.cold_water_temperature", self._get_water_temperature())

    # ##########################################################################################
    # Reading functions
    # ##########################################################################################

    def _get_1_temperature_per_month(self):  # this methods is here to get the temperature when the format is 1 day/month
        month = self._catalog.get("physical_time").month  # the month corresponding to the temperature
        water_temperature = self._temperatures[str(month)]

        return water_temperature

