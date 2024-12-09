# These dataloggers exports the balances for several devices
from src.common.Datalogger import Datalogger
from src.tools.Utilities import into_list
from typing import List

# from src.tools.GraphAndTex import __default_graph_options__


class DeviceQuantityDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, name: str, filename: str, devices_list: List[str], period=1, graph_options="default"):
        self._devices_list = {}
        devices_list = into_list(devices_list)

        super().__init__(name, filename, period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"devices energy", "y2label": f"devices money"})
            
        def create_get_quantity_function(device_name, nature_name):

            def get_quantity(name):
                quantity = self._catalog.get(f"{device_name}.{nature_name}.energy_accorded")["quantity"]

                return quantity

            return get_quantity

        def create_get_price_function(device_name, nature_name):

            def get_money(name):
                price = self._catalog.get(f"{device_name}.{nature_name}.energy_accorded")["price"]

                return price

            return get_money

        for device_name in self._catalog.get("dictionaries")['devices'].keys():
            if self._catalog.get("dictionaries")['devices'][device_name].name in devices_list:
                self._devices_list[device_name] = [nature.name for nature in self._catalog.get("dictionaries")['devices'][device_name].natures]  # get all the names

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        for device_name in self._devices_list.keys():  # for each nature registered into world, all the relevant keys are added
            for nature_name in self._devices_list[device_name]:
                    self.add(f"{device_name}.energy", create_get_quantity_function(device_name, nature_name), graph_status="Y")
                    self.add(f"{device_name}.money", create_get_price_function(device_name, nature_name), graph_status="Y2")



