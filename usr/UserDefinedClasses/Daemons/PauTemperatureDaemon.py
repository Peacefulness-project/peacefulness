# this daemon is designed to manage teh temperature in the system
# Here, it is very basic as it supposes that temperature is uniform and constant
from common.Daemon import Daemon
from math import pi, cos, exp
from tools.UserClassesDictionary import user_classes_dictionary


class PauTemperatureDaemon(Daemon):

    def __init__(self, name, period):
        super().__init__(name, period)

        self._agent_list = None

        self._temperatures = {  # temperatures in the city of Pau in France
            1: [6, 5.8, 5.7, 5.7, 5.6, 5.5, 5.4, 5.2, 5.8, 6.3, 6.8, 8.1, 9.3, 10.6, 10.7, 10.9, 11.1, 10.2, 9.3, 8.4, 7.8, 7.1, 6.5, 6.3],
            2: [6.42, 6.02, 5.77, 5.53, 5.29, 5.08, 4.88, 4.67, 5.72, 6.76, 7.8, 8.99, 10.17, 11.35, 11.63, 11.91, 12.19, 11.23, 10.38, 9.32, 8.58, 7.84, 7.1, 6.76],
            3: [8.64, 8.12, 7.81, 7.5, 7.19, 6.94, 6.7, 6.45, 8.05, 9.64, 11.24, 12.21, 13.18, 14.15, 14.48, 14.81, 15.13, 14.28, 13.43, 12.58, 11.56, 10.54, 9.52, 9.08],
            4: [11.66, 10.94, 10.61, 10.27, 9.94, 9.85, 9.77, 9.68, 11.45, 13.23, 15, 15.79, 16.59, 17.38, 17.65, 17.92, 18.18, 17.5, 16.81, 16.13, 15.087, 14.01, 12.95, 12.3],
            5: [14.76, 13.98, 13.64, 13.31, 12.97, 13.1, 13.23, 13.36, 14.75, 16.15, 17.55, 18.27, 19, 19.72, 20.03, 20.34, 20.65, 20.19, 19.72, 19.26, 18.21, 17.116, 16.11, 15.43],
            6: [18.13, 17.18, 16.78, 16.39, 15.99, 16.15, 16.3, 16.46, 17.8, 19.13, 20.46, 21.33, 22.2, 23.07, 23.46, 23.85, 24.24, 23.76, 23.28, 22.8, 21.76, 20.72, 19.68, 18.91],
            7: [19.75, 19.39, 19.02, 18.66, 18.64, 18.61, 18.59, 19.82, 21.05, 22.27, 23.28, 24.28, 25.28, 25.76, 26.24, 26.72, 26.31, 25.9, 25.49, 24.44, 23.38, 22.32, 21.48, 20.63],
            8: [19.69, 19.29, 18.9, 18.5, 18.33, 18.15, 17.98, 19.35, 20.72, 22.09, 23.08, 24.07, 25.07, 25.55, 26.03, 26.51, 25.96, 25.4, 24.84, 23.83, 22.82, 21.81, 21.09, 20.36],
            9: [17.75, 17.34, 16.93, 16.52, 16.26, 16, 15.75, 17.26, 18.78, 20.3, 21.22, 22.13, 23.05, 23.41, 23.78, 24.14, 23.49, 22.84, 22.19, 21.21, 20.22, 19.24, 18.71, 18.19],
            10: [14.44, 14.12, 13.8, 13.48, 13.28, 13.09, 12.89, 14.35, 15.81, 17.27, 18.23, 19.19, 20.16, 20.31, 20.47, 20.62, 19.69, 18.75, 17.81, 16.98, 16.15, 15.31, 14.98, 14.65],
            11: [9.7, 9.53, 9.36, 9.19, 9, 8.81, 8.62, 9.61, 10.6, 11.59, 12.55, 13.52, 14.48, 14.52, 14.56, 14.6, 13.73, 12.85, 11.98, 11.32, 10.66, 10, 9.83, 9.66],
            12: [6.02, 5.9, 5.78, 5.66, 5.55, 5.43, 5.31, 5.97, 6.62, 7.28, 8.68, 10.08, 11.48, 11.55, 11.61, 11.68, 10.69, 9.7, 8.71, 8.02, 7.34, 6.65, 6.44, 6.23]
        }

        self._reference_temperatures = {  # reference temperature for the exergy calculation for each month
            1: 5.2,
            2: 4.67,
            3: 6.45,
            4: 9.68,
            5: 12.97,
            6: 15.99,
            7: 18.59,
            8: 17.98,
            9: 15.75,
            10: 12.89,
            11: 8.62,
            12: 5.31
        }

    def _user_register(self):
        # get back the list of agents needing temperature calculation
        self._agent_list = self._catalog.get("agents_with_temperature_devices")  # here are stored agent names, their thermal inertia and their G coefficient
        self._catalog.remove("agents_with_temperature_devices")  # the entry is not useful anymore in the catalog, so it is deleted


        current_hour = self._catalog.get("physical_time").hour  # the current hour of the day
        current_month = self._catalog.get("physical_time").month  # the current month in the year

        # create external temperatures
        self._catalog.add(f"current_outdoor_temperature", self._temperatures[current_month][current_hour])
        self._catalog.add(f"previous_outdoor_temperature", self._temperatures[current_month][current_hour])

        # set initial indoor temperatures to the outdoor initial temperature
        for agent_name in self._agent_list:
            self._catalog.set(f"{agent_name}.previous_indoor_temperature", 17)
            self._catalog.set(f"{agent_name}.current_indoor_temperature", 17)

        self._catalog.add(f"reference_temperature", self._reference_temperatures[current_month])  # reference temperature used for the calculation of exergy

    def _process(self):

        # outdoor temperature update
        current_hour = self._catalog.get("physical_time").hour  # the current hour of the day
        current_month = self._catalog.get("physical_time").month  # the current month in the year

        current_outdoor_temperature = self._catalog.get("current_outdoor_temperature")
        self._catalog.set(f"previous_outdoor_temperature", current_outdoor_temperature)  # updating the previous temperature

        self._catalog.set(f"current_outdoor_temperature", self._temperatures[current_month][current_hour])

        self._catalog.set(f"reference_temperature", self._reference_temperatures[current_month])  # reference temperature used for the calculation of exergy


user_classes_dictionary[f"{PauTemperatureDaemon.__name__}"] = PauTemperatureDaemon

