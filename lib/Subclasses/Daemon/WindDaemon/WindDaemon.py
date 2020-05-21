# this daemon is designed to manage the price of a given energy for sellers or buyers
from json import load
from src.common.Daemon import Daemon


class WindDaemon(Daemon):

    def __init__(self, parameters, period=1):
        self._location = parameters["location"]  # the location corresponding to the data

        name = "win_speed_in_" + self._location
        super().__init__(name, period, parameters)

        # getting the data for the chosen location
        if "datafile" in parameters:  # if the user has chosen another datafile
            file = open(parameters["datafile"], "r")
        else:
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
        hour = (self._catalog.get("physical_time").hour+1) % 24
        return self._wind_values[str(month)][hour]



