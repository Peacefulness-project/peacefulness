# this daemon is designed to manage the price of a given energy for sellers or buyers
from json import load
from src.common.Daemon import Daemon


class IrradiationDaemon(Daemon):

    def __init__(self, world, name, parameters, period=0):
        super().__init__(world, name, period, parameters)

        self._location = parameters["location"]

        # getting the data for the chosen location
        file = open("lib/Subclasses/Daemon/IrradiationDaemon/IrradiationProfiles.json", "r")
        data = load(file)[self._location]
        file.close()

        self._irradiation_values = data["irradiation"]
        self._format = data["format"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"each_hour/month": self._get_each_hour_per_month}  # every hours in a month
        self._get_irradiation = self._files_formats[self._format]

        # setting initial values
        self._catalog.add(f"{self._location}.irradiation_value", self._get_irradiation())  # setting the initial value of previous temperature

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self._location}.irradiation_value", self._get_irradiation())

    # ##########################################################################################
    # Reading functions
    # ##########################################################################################

    def _get_each_hour_per_month(self):  # this methods is here to get the temperature when the format is 1 day/month
        month = self._catalog.get("physical_time").month  # the month corresponding to the temperature
        day = self._catalog.get("physical_time").day - 1  # the "- 1" is necessary because python indexation begins at 0 and day at 1
        hour = self._catalog.get("physical_time").hour

        irradiation = self._irradiation_values[str(month)][24*day+hour]  # the value of irradiation at the current hour for the current day for the current month

        return irradiation


