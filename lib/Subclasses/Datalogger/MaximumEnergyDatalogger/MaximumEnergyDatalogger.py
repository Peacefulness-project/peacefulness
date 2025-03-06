# This datalogger exports the decisions taken by the RL agent
from src.common.Datalogger import Datalogger
from src.tools.Utilities import into_list
from typing import List
# from src.tools.GraphAndTex import __default_graph_options__


class MaximumEnergyDatalogger(Datalogger):  # a subclass of datalogger designed to export the Emax of the devices

    def __init__(self, name: str, filename: str, devices_list: List[str], period=1, graph_options="default"):
        devices_list = into_list(devices_list)
        self._devices_list = {}

        super().__init__(name, filename, period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"Emax"})

        self.add(f"simulation_time", graph_status="X")
        self.add(f"physical_time", graph_status="")

        def create_get_Emax_function(device_name, nature_name):

            def get_Emax(name):
                Emax = self._catalog.get(f"{device_name}.{nature_name}.energy_wanted")["energy_maximum"]

                return Emax

            return get_Emax

        for device_name in self._catalog.get("dictionaries")['devices'].keys():
            if self._catalog.get("dictionaries")['devices'][device_name].name in devices_list:  # get all the names
                nature_list = [nature.name for nature in self._catalog.get("dictionaries")['devices'][device_name].natures]  # get all the natures in a list
                aggregator_list = self._catalog.get("dictionaries")['devices'][device_name].device_aggregators  # get the aggregator list
                self._devices_list[device_name] = (nature_list, aggregator_list)

        for device_name in self._devices_list.keys():  # for each nature registered into world, the Emax key is added
            for nature_name in self._devices_list[device_name][0]:
                aggregator_name = self._devices_list[device_name][1][0].name
                self.add(f"{device_name}.{aggregator_name}.{nature_name}.maximum_energy", create_get_Emax_function(device_name, nature_name), graph_status="Y")
