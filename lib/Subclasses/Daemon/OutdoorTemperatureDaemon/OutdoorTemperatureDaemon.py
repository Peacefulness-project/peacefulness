# this daemon is designed to manage teh temperature in the system
# Here, it is very basic as it supposes that temperature is uniform and constant
from json import load
from datetime import datetime
from src.common.Daemon import Daemon
from src.tools.ReadingFunction import get_1_day_per_month, get_365_days


class OutdoorTemperatureDaemon(Daemon):

    def __init__(self, parameters, period=1, filename="lib/Subclasses/Daemon/OutdoorTemperatureDaemon/TemperatureProfiles.json"):
        self._location = parameters["location"]  # the location corresponding to the data

        name = "outdoor_temperature_in_" + self._location
        super().__init__(name, period, parameters, filename)

        self._agent_list = None  # all the agents concerned with outdoor temperature

        # getting the data for the chosen location
        file = open(filename, "r")
        data = load(file)[self._location]
        file.close()

        self._temperatures = data["temperatures"]
        self._exergy_reference_temperatures = data["exergy_reference_temperatures"]
        self._format = data["format"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"day/month": get_1_day_per_month,  # 1 representative day, hour by hour, for each month
                               "365days": get_365_days}  # every days in a year, hour by hour
        self._get_outdoor_temperature = self._files_formats[self._format]

        # setting initial values
        self._catalog.add(f"{self._location}.previous_outdoor_temperature", self._get_outdoor_temperature(self._temperatures,self._catalog))  # setting the initial value of previous temperature
        self._catalog.add(f"{self._location}.current_outdoor_temperature", self._get_outdoor_temperature(self._temperatures,self._catalog))  # setting the initial value of current temperature
        self._catalog.add(f"{self._location}.reference_temperature", self._get_exergy_reference_temperature())  # setting the initial value of reference temperature for exergy

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):
        current_outdoor_temperature = self._catalog.get(f"{self._location}.current_outdoor_temperature")
        self._catalog.set(f"{self._location}.previous_outdoor_temperature", current_outdoor_temperature)  # updating the previous temperature

        self._catalog.set(f"{self._location}.current_outdoor_temperature", self._get_outdoor_temperature(self._temperatures,self._catalog))

        self._catalog.set(f"{self._location}.reference_temperature", self._get_exergy_reference_temperature())  # reference temperature used for the calculation of exergy

    # ##########################################################################################
    # Reading functions
    # ##########################################################################################

    def _get_exergy_reference_temperature(self):
        current_month = str(self._catalog.get("physical_time").month)  # the current month in the year

        return self._exergy_reference_temperatures[current_month]  # return the appropriate reference temperature for the the ongoing month

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def location(self):
        return self._location


