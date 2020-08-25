# this daemon is designed to manage the flow of a given river
from json import load
from src.common.Daemon import Daemon
from src.tools.ReadingFunction import get_each_hour_per_month


class WaterFlowDaemon(Daemon):

    def __init__(self, parameters, period=1, filename="lib\Subclasses\Daemon\WaterFlowDaemon\WaterFlowProfiles.json"):
        self._location = parameters["location"]  # the location corresponding to the data

        name = "water_flow_in_" + self._location
        super().__init__(name, period, parameters, filename)

        # getting the data for the chosen location
        file = open(filename, "r")
        data = load(file)[self._location]
        file.close()

        self._format = data["format"]
        self._flow_values = data["flow"]
        self._reserved_flow = data["reserved_flow"]
        self._max_flow = data["max_flow"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"each_hour/month": get_each_hour_per_month}  # every hours in a month

        self._get_water_flow = self._files_formats[self._format]

        # setting initial values
        self._catalog.add(f"{self._location}.flow_value", self._get_water_flow(self._flow_values, self._catalog))
        self._catalog.add(f"{self._location}.reserved_flow", self._reserved_flow)
        self._catalog.add(f"{self._location}.max_flow", self._max_flow)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self._location}.flow_value", self._get_water_flow(self._flow_values, self._catalog))

    # ##########################################################################################
    # Reading functions
    # ##########################################################################################
