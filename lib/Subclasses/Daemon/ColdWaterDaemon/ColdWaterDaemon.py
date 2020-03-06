# this daemon is designed to calculate a very unaccurate dynamic temperature of the cold water in housings during a year.
# according to a report of ADEME (french institute working on the energetic transition), the min temperature is 9°C (we choose February) and the max is 21°C in August
# knowing that, we built a linear function going from 9 to 21 to get one temperature per month

from src.common.Daemon import Daemon


class ColdWaterDaemon(Daemon):

    def __init__(self, name, period):
        super().__init__(name, period)

    def _user_register(self):

        # calculate the initial temperature
        month = (self._catalog.get("physical_time").month - 2) % 12  # the number of the month, delayed to be centered on August, the warmest month
        # January is 11, February is 0, March is 1 and so on...

        water_temperature = 21 - 2 * abs(6 - month)  # the value, in °C, of the cold water in housings

        self._catalog.add("cold_water_temperature", water_temperature)

    def _process(self):
        # calculate the ongoing temperature
        month = (self._catalog.get("physical_time").month - 2) % 12  # the number of the month, delayed to be centered on August, the warmest month
        # January is 11, February is 0, March is 1 and so on...

        water_temperature = 21 - 2 * abs(6 - month)  # the value, in °C, of the cold water in housings

        self._catalog.set("cold_water_temperature", water_temperature)



