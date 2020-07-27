# this daemon is designed to manage the flow of a given river
from json import load
from src.common.Daemon import Daemon


class WaterFlowDaemon(Daemon):

    def __init__(self, parameters, period=1):
        self._location = parameters["location"]  # the location corresponding to the data

        name = "water_flow_in_" + self._location
        super().__init__(name, period, parameters)

        # getting the data for the chosen location
        if "datafile" in parameters:  # if the user has chosen another datafile
            file = open(parameters["datafile"], "r")
        else:
            file = open("lib\Subclasses\Daemon\WaterFlowDaemon\WaterFlowProfiles.json", "r")
        data = load(file)[self._location]
        file.close()

        self._format = data["format"]
        self._flow_values = data["flow"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"each_hour/month": self._get_each_hour_per_month}  # every hours in a month

        self._get_water_flow = self._files_formats[self._format]

        # setting initial values
        self._catalog.add(f"{self._location}.flow_value", self._get_water_flow())

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self._location}.flow_value", self._get_water_flow())

    # ##########################################################################################
    # Reading functions
    # ##########################################################################################

    def _get_each_hour_per_month(self):  # this methods is here to get all wind speed for each hour
        month = self._catalog.get("physical_time").month  # the month corresponding to the wind speed
        day = self._catalog.get("physical_time").day - 1  # the "- 1" is necessary because python indexation begins at 0 and day at 1
        hour = self._catalog.get("physical_time").hour

        flow_values = self._flow_values[str(month)][24 * day + hour]
        return flow_values