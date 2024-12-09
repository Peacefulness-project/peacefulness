# This datalogger exports the state of charge of Energy Storage Systems (ESS) present in the energy grid
from src.common.Datalogger import Datalogger
from src.tools.Utilities import into_list
from typing import List


class StateOfChargeDatalogger(Datalogger):  # a subclass of datalogger designed to export the SoC
    def __init__(self, name: str, filename: str, devices_list: List[str], period=1, graph_options="default"):
        devices_list = into_list(devices_list)
        self._devices_list = {}

        super().__init__(name, filename, period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"state of charge"})

        self.add(f"simulation_time", graph_status="X")
        self.add(f"physical_time", graph_status="")

        def create_get_soc_function(device_name, nature_name):

            def get_soc(name):
                soc = self._catalog.get(f"{device_name}.{nature_name}.energy_wanted")["state_of_charge"]

                return soc

            return get_soc

        for device_name in self._catalog.get("dictionaries")['devices'].keys():
            if self._catalog.get("dictionaries")['devices'][device_name].name in devices_list:  # get all the names
                nature_list = [nature.name for nature in self._catalog.get("dictionaries")['devices'][device_name].natures]  # get all the natures in a list
                aggregator_list = self._catalog.get("dictionaries")['devices'][device_name].device_aggregators  # get the aggregator list
                self._devices_list[device_name] = (nature_list, aggregator_list)

        for device_name in self._devices_list.keys():  # for each nature registered into world, the SoC key is added
            for nature_name in self._devices_list[device_name][0]:
                aggregator_name = self._devices_list[device_name][1][0].name
                self.add(f"{device_name}.{aggregator_name}.{nature_name}.SoC", create_get_soc_function(device_name, nature_name), graph_status="Y")
