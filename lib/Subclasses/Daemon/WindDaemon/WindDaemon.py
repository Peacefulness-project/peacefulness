# this daemon is designed to manage the price of a given energy for sellers or buyers
from json import load
from src.common.Daemon import Daemon


class WindDaemon(Daemon):

    def __init__(self, name, parameters, period=0):
        super().__init__(name, period, parameters)

        self._location = parameters["location"]  # the location corresponding to the data

        # getting the data for the chosen location
        file = open("lib/Subclasses/Daemon/WindDaemon/WindProfiles.json", "r")
        data = load(file)[self._location]
        file.close()

        self._format = data["format"]
        self._wind_values = data["wind_speed"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"1/month": self._get_temperature_365_days}  # 1 representative day, hour by hour, for each month
        self._get_wind_speed = self._files_formats[self._format]

        # setting initial values
        self._catalog.add(f"{self._location}.wind_value", self._get_wind_speed())

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self._location}.wind_value", self._get_wind_speed())

    # ##########################################################################################
    # Reading functions
    # ##########################################################################################

    def _get_temperature_365_days(self):
        month = self._catalog.get("physical_time").month
        hour = self._catalog.get("physical_time").hour
        return self._wind_values[str(month)][hour]



