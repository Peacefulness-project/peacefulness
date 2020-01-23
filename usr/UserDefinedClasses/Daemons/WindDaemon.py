# this daemon is designed to manage the price of a given energy for sellers or buyers
from common.Daemon import Daemon
from tools.UserClassesDictionary import user_classes_dictionary


class WindDaemon(Daemon):

    def __init__(self, location, period=0):
        name = location + "_wind_manager"
        super().__init__(name, period, {"location": location})

        self._location = location

    def _user_register(self):

        self._wind_values = {1: [7.6384, 7.8848, 8.008, 8.1928, 8.1928, 8.2544, 8.316, 8.2544, 8.316, 8.1312, 7.8232, 7.392, 7.2688, 7.1456, 7.084, 7.1456, 7.392, 7.6384, 7.7616, 7.8232, 7.7, 7.5152, 7.7, 7.8232],
                             2: [7.2688, 7.5152, 7.5768, 7.392, 7.2688, 7.2072, 6.9608, 6.8992, 6.8992, 6.6528, 6.3448, 6.4064, 6.4064, 6.5912, 6.8376, 6.9608, 6.9608, 7.2072, 7.2688, 7.2688, 7.2688, 7.2688, 7.392, 7.392],
                             3: [7.3304, 6.8992, 6.8992, 6.8376, 6.8376, 7.0224, 7.084, 7.084, 6.6528, 6.16, 6.16, 6.4064, 6.5912, 6.7144, 6.776, 6.8376, 6.8376, 7.0224, 7.3304, 7.3304, 7.2688, 7.0224, 7.1456, 7.2688],
                             4: [6.8992, 6.7144, 6.776, 6.7144, 6.5912, 6.5296, 6.6528, 6.6528, 5.9752, 5.7904, 5.7904, 5.7288, 5.852, 5.9136, 6.0368, 6.0368, 6.0984, 6.2216, 6.4064, 6.776, 6.9608, 6.8992, 6.5912, 6.3448],
                             5: [6.8376, 6.776, 6.776, 6.6528, 6.5296, 6.5296, 6.0368, 5.2976, 4.8664, 4.8664, 5.0512, 5.236, 5.3592, 5.6672, 5.9136, 6.2216, 6.3448, 6.3448, 6.5912, 7.1456, 7.5768, 7.4536, 7.2072, 7.1456],
                             6: [6.3448, 6.2216, 6.0984, 5.9136, 5.7288, 5.544, 5.1128, 4.2504, 3.9424, 3.9424, 4.004, 4.2504, 4.5584, 4.7432, 4.928, 5.0512, 5.1744, 5.4824, 5.7904, 6.2216, 6.776, 6.8376, 6.468, 6.468],
                             7: [6.3448, 6.2216, 6.0368, 5.6672, 5.544, 5.4824, 5.1744, 4.4968, 4.1888, 4.1888, 4.2504, 4.3736, 4.4968, 4.6816, 4.928, 5.236, 5.2976, 5.236, 5.3592, 5.7288, 5.9136, 6.0984, 6.2832, 5.9136],
                             8: [5.9136, 5.852, 5.6056, 5.544, 5.4824, 5.3592, 4.9896, 4.4968, 4.0656, 4.004, 3.9424, 4.004, 4.004, 4.0656, 4.1888, 4.3736, 4.5584, 4.6816, 5.1128, 5.6672, 5.7288, 5.544, 5.544, 5.544],
                             9: [5.852, 5.6672, 5.4824, 5.2976, 5.0512, 4.8048, 4.7432, 4.8048, 4.3736, 3.7576, 3.696, 3.8192, 3.9424, 4.1888, 4.4352, 4.6816, 4.8048, 4.9896, 5.2976, 5.6056, 5.852, 5.9136, 5.7904, 5.7904],
                             10: [5.3592, 5.0512, 5.1128, 4.928, 4.6816, 4.5584, 4.5584, 4.8664, 4.8664, 4.3736, 4.0656, 3.8192, 3.8192, 4.1272, 4.4352, 4.4968, 4.928, 5.236, 5.4824, 5.6672, 5.7904, 5.9136, 6.0368, 6.2832],
                             11: [6.5912, 6.5296, 6.8992, 7.1456, 7.084, 7.1456, 7.2072, 7.2688, 7.3304, 7.4536, 6.8992, 6.6528, 6.7144, 7.084, 7.084, 7.2072, 7.3304, 7.3304, 7.2688, 7.1456, 7.084, 7.1456, 7.084, 6.9608],
                             12: [6.8992, 7.0224, 7.3304, 7.4536, 7.392, 7.2688, 7.2072, 7.2688, 7.2688, 7.2072, 6.8992, 6.468, 6.2216, 6.2832, 6.468, 6.6528, 6.7144, 6.8376, 7.0224, 7.0224, 7.2072, 7.392, 7.5768, 7.5768]
                             }  # wind in m.s-1

        month = self._catalog.get("physical_time").month
        hour = self._catalog.get("physical_time").hour

        wind = self._wind_values[month][hour]  # the value of wind at the current hour for the current day for the current month

        self._catalog.add(f"{self._location}_wind_value", wind)

    def _process(self):

        month = self._catalog.get("physical_time").month
        hour = self._catalog.get("physical_time").hour

        wind = self._wind_values[month][hour]  # the value of wind at the current hour for the current day for the current month

        self._catalog.set(f"{self._location}_wind_value", wind)


user_classes_dictionary[f"{WindDaemon.__name__}"] = WindDaemon


