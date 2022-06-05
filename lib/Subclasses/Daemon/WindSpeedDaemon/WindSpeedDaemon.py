# this daemon is designed to manage the price of a given energy for sellers or buyers
from json import load
from numpy import mean

from src.common.Daemon import Daemon
from src.tools.ReadingFunctions import get_each_hour_per_month, get_1_day_per_month, get_non_periodic_values


class WindSpeedDaemon(Daemon):

    def __init__(self, parameters, filename="lib/Subclasses/Daemon/WindSpeedDaemon/WindSpeedProfiles.json"):
        self._location = parameters["location"]  # the location corresponding to the data

        name = "wind_speed_in_" + self._location
        super().__init__(name, 1, parameters, filename)

        # getting the data for the chosen location
        file = open(filename, "r")
        data = load(file)[self._location]
        file.close()

        self._format = data["format"]
        self._wind_values = data["wind_speed"]
        self._height_ref = data["height_ref"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"each_hour/month": get_each_hour_per_month,  # every hours in a month
                               "1/month": get_1_day_per_month,  # 1 representative day, hour by hour, for each month
                               "non_periodic": get_non_periodic_values,  # each value is associated to a precise datetime, which must match the ones encountered in the simulation
                               }
        self._get_wind_speed = self._files_formats[self._format]

        # setting initial values
        self._catalog.add(f"{self._location}.wind_value", self._get_wind_speed(self._wind_values, self._catalog))
        self._catalog.add(f"{self._location}.height_ref", self._height_ref)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        time_step = self._catalog.get("time_step")

        if time_step <= 1:
            self._catalog.set(f"{self._location}.wind_value", self._get_wind_speed(self._wind_values, self._catalog))
        elif time_step > 1:
            values_to_be_averaged = []
            for j in range(int(time_step)):
                values_to_be_averaged.append(self._get_wind_speed(self._wind_values, self._catalog, -j))
            self._catalog.set(f"{self._location}.wind_value", mean(values_to_be_averaged))

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def location(self):
        return self._location


