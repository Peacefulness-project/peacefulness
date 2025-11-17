# These dataloggers exports the balances for aggregators
from src.common.Datalogger import Datalogger
from copy import deepcopy
# from src.tools.GraphAndTex import __default_graph_options__


class EquityDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, name: str, filename: str, period=1, graph_options="default"):
        super().__init__(name, filename, period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"unserved energy"})

        def create_get_max_diff_quantity_function(device_name, nature_name):

            def get_accorded(name):
                given_quantity = self._catalog.get(f"{device_name}.{nature_name}.energy_accorded")["quantity"]
                min_wanted_quantity = self._catalog.get(f"{device_name}.{nature_name}.energy_wanted")["energy_minimum"]
                max_wanted_quantity = self._catalog.get(f"{device_name}.{nature_name}.energy_wanted")["energy_maximum"]
                if abs(min_wanted_quantity - max_wanted_quantity) < 1e-6 :
                    return_value = abs(max_wanted_quantity - given_quantity)
                else:
                    # return_value = abs((given_quantity - min_wanted_quantity) / (max_wanted_quantity - min_wanted_quantity))  # todo equity for bigger consumers
                    return_value = abs(given_quantity - min_wanted_quantity)  # todo equity for smaller consumers

                return return_value

            return get_accorded

        def create_get_min_diff_quantity_function(device_name, nature_name):

            def get_max_wanted(name):
                given_quantity = self._catalog.get(f"{device_name}.{nature_name}.energy_accorded")["quantity"]
                min_wanted_quantity = self._catalog.get(f"{device_name}.{nature_name}.energy_wanted")["energy_minimum"]
                max_wanted_quantity = self._catalog.get(f"{device_name}.{nature_name}.energy_wanted")["energy_maximum"]

                return min(abs(given_quantity - min_wanted_quantity), abs(given_quantity - max_wanted_quantity))

            return get_max_wanted


        if f"DRL_Strategy.strategy_scope" not in self._catalog.keys:
            self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names
        else:
            self._aggregators_list = [agg.name for agg in self._catalog.get("DRL_Strategy.strategy_scope")]

        self._devices_list = {}
        for aggregator_name in self._aggregators_list:
            device_dict = {}
            for device_name in self._catalog.get("dictionaries")['aggregators'][aggregator_name].devices:
                device_dict[device_name] = {"natures": [nature.name for nature in self._catalog.get("dictionaries")['devices'][device_name].natures],
                                            "type": self._catalog.get("dictionaries")['devices'][device_name].get_type}
            self._devices_list[aggregator_name] = deepcopy(device_dict)

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            for device_name in self._devices_list[aggregator_name]:
                for nature_name in self._devices_list[aggregator_name][device_name]["natures"]:
                    if self._devices_list[aggregator_name][device_name]["type"] == "standard":
                        self.add(f"{self._devices_list[aggregator_name][device_name]["type"]}.{device_name}.{aggregator_name}.unserved", create_get_max_diff_quantity_function(device_name, nature_name), graph_status="Y")
                    else:
                        self.add(f"{self._devices_list[aggregator_name][device_name]["type"]}.{device_name}.{aggregator_name}.unserved", create_get_min_diff_quantity_function(device_name, nature_name), graph_status="Y")


