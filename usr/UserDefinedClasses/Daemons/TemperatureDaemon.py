# this daemon is designed to manage teh temperature in the system
# Here, it is very basic as it supposes that temperature is uniform and constant

from common.Daemon import Daemon
from math import pi, cos, exp


class TemperatureDaemon(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)
        self._temperature = parameters["temperature"]
        # self._temperature_min = parameters["temperature_min"]
        # self._temperature_max = parameters["temperature_max"]

        self._agent_list = None

    def _user_register(self):
        # create external temperatures
        self._catalog.add(f"current_outdoor_temperature", self._temperature)
        self._catalog.add(f"previous_outdoor_temperature", self._temperature)

        # get back the list of agents needing temperature calculation
        self._agent_list = self._catalog.get("agents_with_temperature_devices")  # here are stored agent names, their thermal inertia and their G coefficient
        self._catalog.remove("agents_with_temperature_devices")  # the entry is not useful anymore in the catalog, so it is deleted

    def _process(self):

        # outdoor temperature update
        current_hour = self._catalog.get("physical_time").hour  # the current hour of the day
        current_month = self._catalog.get("physical_time").month  # the current month in the year

        current_outdoor_temperature = self._catalog.get("current_outdoor_temperature")
        self._catalog.set(f"previous_outdoor_temperature", current_outdoor_temperature)  # updating the previous temperature

        current_outdoor_temperature = - 15 * cos(2*pi*(current_month/12 - 1)) - 5 * cos(2*pi*(current_hour/24 - 1)) + 10
        self._catalog.set(f"current_outdoor_temperature", current_outdoor_temperature)

        # indoor temperature update
        previous_outdoor_temperature = self._catalog.get("previous_outdoor_temperature")
        time_step = self._catalog.get("time_step") * 3600  # the duration of a time step in seconds
        for agent_name in self._agent_list:
            thermal_inertia = self._agent_list[agent_name][0]
            G = self._agent_list[agent_name][1]

            previous_indoor_temperature = self._catalog.get(f"{agent_name}.previous_indoor_temperature")
            current_indoor_temperature = self._catalog.get(f"{agent_name}.current_indoor_temperature")

            self._catalog.set(f"{agent_name}.previous_indoor_temperature", current_indoor_temperature)  # updating the previous temperature
            current_indoor_temperature = current_outdoor_temperature + 0 * G * (1 - exp(-time_step/thermal_inertia)) + (previous_indoor_temperature - previous_outdoor_temperature) * exp(-time_step/thermal_inertia)

            self._catalog.set(f"{agent_name}.current_indoor_temperature", current_indoor_temperature)  # updating the previous temperature

