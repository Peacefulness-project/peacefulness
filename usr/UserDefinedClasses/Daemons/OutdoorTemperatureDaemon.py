# this daemon is designed to manage teh temperature in the system
# Here, it is very basic as it supposes that temperature is uniform and constant
from json import load
from datetime import timedelta, datetime
from common.Daemon import Daemon
from tools.UserClassesDictionary import user_classes_dictionary


class OutdoorTemperatureDaemon(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)

        self._agent_list = None

        self._files_formats = dict()

        file = open(parameters["file"], "r")
        data = load(file)
        file.close()

        self._temperatures = data["temperatures"]

        self._exergy_reference_temperatures = data["exergy_reference_temperatures"]

        self._format = data["format"]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        # getting back the appropriate way of reading the data
        self._files_formats = {"day/month": self._get_temperature_1_day_month,  # 1 representative day, hour by hour, for each month
                               "365days": self._get_temperature_365_days}  # every days in a year, hour by hour
        self._get_outdoor_temperature = self._files_formats[self._format]

        # setting initial values
        self._catalog.add(f"previous_outdoor_temperature", self._get_outdoor_temperature())  # setting the initial value of previous temperature
        self._catalog.add(f"current_outdoor_temperature", self._get_outdoor_temperature())  # setting the initial value of current temperature
        self._catalog.add(f"reference_temperature", self._get_exergy_reference_temperature())  # setting the initial value of reference temperature for exergy

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):
        current_outdoor_temperature = self._catalog.get("current_outdoor_temperature")
        self._catalog.set(f"previous_outdoor_temperature", current_outdoor_temperature)  # updating the previous temperature

        self._catalog.set(f"current_outdoor_temperature", self._get_outdoor_temperature())

        self._catalog.set(f"reference_temperature", self._get_exergy_reference_temperature())  # reference temperature used for the calculation of exergy

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def _get_temperature_1_day_month(self):  # this methods is here to get the temperature when the format is 1 day/month
        current_hour = self._catalog.get("physical_time").hour  # the current hour of the day
        current_month = str(self._catalog.get("physical_time").month)  # the current month in the year
        return self._temperatures[current_month][current_hour]  # return the appropriate outdoor temperature for the current moment

    def _get_temperature_365_days(self):
        moment = self._catalog.get("physical_time")
        year = moment.year
        duration = moment - datetime(year=year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        current_hour = duration.days * 24 + duration.seconds // 3600  # conversion of the duration in hours spent since the beginning of the year

        return self._temperatures[current_hour]

    def _get_exergy_reference_temperature(self):
        current_month = str(self._catalog.get("physical_time").month)  # the current month in the year

        return self._exergy_reference_temperatures[current_month]  # return the appropriate reference temperature for the the ongoing month


user_classes_dictionary[f"{OutdoorTemperatureDaemon.__name__}"] = OutdoorTemperatureDaemon

