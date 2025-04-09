# These dataloggers exports the balances for several devices
from src.common.Datalogger import Datalogger
from src.tools.Utilities import into_list
from typing import List


# from src.tools.GraphAndTex import __default_graph_options__


class MEGstateDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, name: str, filename: str, devices_list: List[str], aggregator: str, period=1, graph_options="default"):
        self._devices_list = {}
        device_list = into_list(devices_list)

        super().__init__(name, filename, period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"aggregator state", "y2label": f"price information"})

        self._concerned_aggregator = self._catalog.aggregators[aggregator]

        def create_get_device_function(device, nature_name):

            def get_device_message(name):
                quantity = device.get_energy_wanted(nature_name)

                return quantity

            return get_device_message

        def create_get_aggregator_function(agregateur):

            def get_aggregator_message(name):
                min_exchange = - agregateur.capacity["buying"]
                max_exchange = agregateur.capacity["selling"]
                eff_exchange = agregateur.efficiency

                return [min_exchange, max_exchange, eff_exchange]

            return get_aggregator_message

        def create_get_price_information(nature_name):

            def get_price_message(name):
                max_price = self._catalog.get(f"{nature_name}.limit_buying_price")
                min_price = self._catalog.get(f"{nature_name}.limit_selling_price")

                return [max_price, min_price]

            return get_price_message

        for device_name in device_list:
            self._devices_list[device_name] = self._catalog.devices[device_name]

        #     if self._catalog.get("dictionaries")['devices'][device_name].name in devices_list:
        #         self._devices_list[device_name] = [nature.name for nature in self._catalog.get("dictionaries")['devices'][device_name].natures]  # get all the names

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        concerned_nature = self._concerned_aggregator.nature

        # devices message
        for device_name in self._devices_list:  # for each nature registered into world, all the relevant keys are added
            self.add(f"{device_name}.message", create_get_device_function(self._devices_list[device_name], concerned_nature),graph_status="Y")

        # energy exchange with outside
        self.add(f"{aggregator}.exchange_message", create_get_aggregator_function(self._concerned_aggregator))

        # energy prices
        self.add(f"Mirror_Aggregator_energy_prices_message", create_get_price_information(concerned_nature.name))

