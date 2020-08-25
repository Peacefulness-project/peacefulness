# this daemon is designed to manage the flow of a given river
from json import load
from src.common.Daemon import Daemon
from src.tools.ReadingFunction import get_1_day_per_month


class SunPositionDaemon(Daemon):

    def __init__(self, parameters, period=1, filename="lib/Subclasses/Daemon/SunPositionDaemon/SunPositionProfiles.json"):
        self._location = parameters["location"]  # the location corresponding to the data

        name = "water_flow_in_" + self._location
        super().__init__(name, period, parameters)

        # getting the data for the chosen location
        file = open(filename, "r")
        data = load(file)[self._location]
        file.close()

        self._format = data["format"]
        self._azimut = data["azimut"]
        self._sun_height = data["sun_height"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"day/month": get_1_day_per_month}  # every hours in a month

        self._get_sun_position = self._files_formats[self._format]

        # setting initial values
        self._catalog.add(f"{self._location}.azimut", self._get_sun_position(self._azimut, self._catalog))
        self._catalog.add(f"{self._location}.sun_height", self._get_sun_position(self._sun_height, self._catalog))

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self._location}.azimut", self._get_sun_position(self._azimut, self._catalog))
        self._catalog.set(f"{self._location}.sun_height", self._get_sun_position(self._sun_height, self._catalog))

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def location(self):
        return self._location


