# These dataloggers exports the balances for several devices
from src.common.Datalogger import Datalogger
from src.tools.Utilities import into_list
from typing import List


# from src.tools.GraphAndTex import __default_graph_options__


class ExpertStrategyDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, name: str, filename: str, devices_list: List[str], aggregator: str, period=1, graph_options="default"):
        self._devices_list = {}
        device_list = into_list(devices_list)

        super().__init__(name, filename, period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"aggregator state", "y2label": f"price information"})

        self._concerned_aggregator = self._catalog.aggregators[aggregator]

        def create_get_device_function(device, nature_name):

            def get_device_message(name):
                quantity = device.get_energy_accorded(nature_name)

                return quantity

            return get_device_message

        def create_get_superior_aggregator_function(superior, agregateur):

            def get_aggregator_message(name):
                externalSupMessage = self._catalog.get(f"{agregateur.name}.{agregateur.superior.nature.name}.energy_accorded")

                return externalSupMessage

            return get_aggregator_message

        def create_get_subaggregator_function(agregateur, subaggregator):

            def get_aggregator_message(name):
                externalSubMessage = self._catalog.get(f"{subaggregator.name}.{agregateur.nature.name}.energy_accorded")

                return externalSubMessage

            return get_aggregator_message

        for device_name in device_list:
            self._devices_list[device_name] = self._catalog.devices[device_name]

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        concerned_nature = self._concerned_aggregator.nature

        # devices message
        for device_name in self._devices_list:  # for each nature registered into world, all the relevant keys are added
            self.add(f"{device_name}.internal_expert_message", create_get_device_function(self._devices_list[device_name], concerned_nature),graph_status="Y")

        # energy exchange with outside - superior
        if self._concerned_aggregator.superior:
            self.add(f"{aggregator}.superior_expert_message", create_get_superior_aggregator_function(self._concerned_aggregator.superior, self._concerned_aggregator))

        # energy exchange with outside - subaggregator
        for subaggregator in self._concerned_aggregator.subaggregators:
            self.add(f"{aggregator}.sub_expert_message", create_get_subaggregator_function(self._concerned_aggregator, subaggregator))

