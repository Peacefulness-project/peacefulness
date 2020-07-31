# this daemon is designed to manage the price of a given energy for sellers or buyers
from json import load
from src.common.Daemon import Daemon
from src.tools.ReadingFunction import get_1_day_per_month, get_each_hour_per_month


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
        self._files_formats = {"each_hour/month": get_each_hour_per_month,  # every hours in a month
                               "day/month": get_1_day_per_month  # 1 day in a month
                               }
        self._get_irradiation = self._files_formats[self._format]

        # setting initial values

        self._catalog.add(f"{self._location}.total_irradiation_value", self._get_irradiation(self._total_irradiation_values, self._catalog))  # setting the initial value of previous irradiation
        self._catalog.add(f"{self._location}.direct_normal_irradiation_value", self._get_irradiation(self._direct_normal_irradiation_values, self._catalog))

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):

        self._catalog.set(f"{self._location}.total_irradiation_value", self._get_irradiation(self._total_irradiation_values, self._catalog))  # setting the initial value of previous irradiation
        self._catalog.set(f"{self._location}.direct_normal_irradiation_value", self._get_irradiation(self._total_irradiation_values, self._catalog))

    # ##########################################################################################
    # Reading functions
    # ##########################################################################################

