# this daemon is designed to manage the flow of a given river, in m3.s-1
from json import load
from src.common.Daemon import Daemon
from src.tools.ReadingFunctions import get_each_hour_per_month


class WaterFlowDaemon(Daemon):

    def __init__(self, parameters, period=1, filename="lib/Subclasses/Daemon/WaterFlowDaemon/WaterFlowProfiles.json"):
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
        time_step = self._catalog.get("time_step")

        if time_step == 1:  # if the time step !=1, it is necessary to adapt the value
            self._catalog.set(f"{self._location}.flow_value", self._get_water_flow(self._flow_values, self._catalog))
        elif time_step < 1:  # if the time step is > 1 hour, values are divided
            water_flow_value = self._get_water_flow(self._flow_values, self._catalog) * time_step

            self._catalog.set(f"{self._location}.flow_value", water_flow_value)

        elif time_step > 1:  # if the time step is > 1 hour, values are summed
            water_flow_value = 0
            for j in range(int(time_step)):
                water_flow_value += self._get_water_flow(self._flow_values, self._catalog, -j)

            self._catalog.set(f"{self._location}.flow_value", water_flow_value)

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def location(self):
        return self._location
