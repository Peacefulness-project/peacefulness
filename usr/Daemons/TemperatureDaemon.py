# this daemon is designed to manage teh temperature in the system
# Here, it is very basic as it supposes that temperature is uniform and constant

from common.Daemon import Daemon


class TemperatureDaemon(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)
        self._temperature = parameters
        # self._temperature_min = parameters[0]
        # self._temperature_max = parameters[1]

    def _user_register(self):
        self._catalog.add(f"outdoor_temperature", self._temperature)

    def _process(self):

        current_hour = self._catalog.get("physical_time").hour  # the current hour of the day
        current_month = self._catalog.get("physical_time").month  # the current month in the year