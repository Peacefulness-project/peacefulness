# this daemon is designed to manage teh temperature in the system
# Here, it is very basic as it supposes that temperature is uniform and constant
from src.common.Daemon import Daemon
from math import exp


class IndoorTemperatureDaemon(Daemon):

    def __init__(self, name, period=0, parameters=None):
        super().__init__(name, period, parameters)

        self._agent_list = None

        # get back the list of agents needing temperature calculation
        self._agent_list = self._catalog.get("agents_with_temperature_devices")  # here are stored agent names, their thermal inertia and their G coefficient
        self._catalog.remove("agents_with_temperature_devices")  # the entry is not useful anymore in the catalog, so it is deleted

        # set initial indoor temperatures to the outdoor initial temperature
        for agent_name in self._agent_list:
            self._catalog.set(f"{agent_name}.previous_indoor_temperature", 17)
            self._catalog.set(f"{agent_name}.current_indoor_temperature", 17)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):

        # indoor temperature second_update
        list_of_locations = self._catalog.get("locations")
        previous_outdoor_temperature = {}
        current_outdoor_temperature = {}
        time_step = self._catalog.get("time_step") * 3600  # the duration of a time step in seconds

        for location in list_of_locations:
            previous_outdoor_temperature[location] = self._catalog.get(f"{location}.previous_outdoor_temperature")
            current_outdoor_temperature[location] = self._catalog.get(f"{location}.current_outdoor_temperature")

            for agent_name in self._agent_list:
                thermal_inertia = self._agent_list[agent_name][0]
                G = self._agent_list[agent_name][1]

                previous_indoor_temperature = self._catalog.get(f"{agent_name}.previous_indoor_temperature")
                current_indoor_temperature = self._catalog.get(f"{agent_name}.current_indoor_temperature")

                self._catalog.set(f"{agent_name}.previous_indoor_temperature", current_indoor_temperature)  # updating the previous temperature
                deltaT_heating_or_cooling = current_indoor_temperature - previous_indoor_temperature
                current_indoor_temperature = previous_outdoor_temperature[location] + \
                                            (previous_indoor_temperature - previous_outdoor_temperature[location]) * exp(-time_step/thermal_inertia) + deltaT_heating_or_cooling

                self._catalog.set(f"{agent_name}.current_indoor_temperature", current_indoor_temperature)  # updating the previous temperature



