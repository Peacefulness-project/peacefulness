# this daemon is designed to manage the price of a given energy for sellers or buyers
from json import load
from src.common.Daemon import Daemon


class IrradiationDaemon(Daemon):

    def __init__(self, parameters, period=1):
        self._location = parameters["location"]

        name = "solar_irradiation_in_" + self._location
        super().__init__(name, period, parameters)

        # getting the data for the chosen location
        file = open("lib/Subclasses/Daemon/IrradiationDaemon/IrradiationProfiles.json", "r")
        data = load(file)[self._location]
        file.close()

        self._total_irradiation_values = data["total_irradiation"]
        self._direct_normal_irradiation_values = data["direct_normal_irradiation"]
        self._format = data["format"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"each_hour/month": self._get_each_hour_per_month,  # every hours in a month
                               "day/month": self._get_1_day_per_month  # 1 day in a month
                               }
        self._get_irradiation = self._files_formats[self._format]

        # setting initial values
        irradiation = self._get_irradiation()
        self._catalog.add(f"{self._location}.total_irradiation_value", irradiation["total"])  # setting the initial value of previous irradiation
        self._catalog.add(f"{self._location}.direct_normal_irradiation_value", irradiation["direct"])

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):
        irradiation = self._get_irradiation()
        self._catalog.set(f"{self._location}.total_irradiation_value", irradiation["total"])  # setting the initial value of previous irradiation
        self._catalog.set(f"{self._location}.direct_normal_irradiation_value", irradiation["direct"])

    # ##########################################################################################
    # Reading functions
    # ##########################################################################################

    def _get_each_hour_per_month(self):  # this methods is here to get the irradiation when the format is 1 day/month
        month = self._catalog.get("physical_time").month  # the month corresponding to the irradiation
        day = self._catalog.get("physical_time").day - 1  # the "- 1" is necessary because python indexation begins at 0 and day at 1
        hour = self._catalog.get("physical_time").hour

        irradiation = {}
        irradiation["total"] = self._total_irradiation_values[str(month)][24 * day + hour]  # the value of irradiation at the current hour for the current day for the current month
        irradiation["direct"] = self._direct_normal_irradiation_values[str(month)][24 * day + hour]

        return irradiation

    def _get_1_day_per_month(self):  # this methods is here to get the irradiation when the format is 1 day/month
        current_hour = self._catalog.get("physical_time").hour  # the current hour of the day
        current_month = str(self._catalog.get("physical_time").month)  # the current month in the year

        irradiation = {}
        irradiation["total"] = self._total_irradiation_values[current_month][current_hour]  # the value of irradiation at the current hour for the current day for the current month
        irradiation["direct"] = self._direct_normal_irradiation_values[current_month][current_hour]

        return irradiation  # return the appropriate irradiation for the current moment
