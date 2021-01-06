# this datalogger exports the data considered as results for ECOS proceedings
from src.common.Datalogger import Datalogger
# from src.tools.GraphAndTex import __default_graph_options__


class WeightedSelfSufficiencyDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1, graph_options="default"):
        if period == "global":
            super().__init__("weighted_self_sufficiency_global", "WeightedSelfSufficiency_global", period)
        else:
            super().__init__(f"weighted_self_sufficiency_frequency_{period}", f"WeightedSelfSufficiency_frequency_{period}", period, graph_options=graph_options)

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names
        self._agents_list = self._catalog.get("dictionaries")['agents'].keys()  # get all the names
        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        if self._global:
            def create_get_inside_value(aggregator_name):
                def get_inside_value(name):
                    if "sold" in name:
                        return self._catalog.get(f"{aggregator_name}.energy_sold")["inside"]
                    elif "bought" in name:
                        return self._catalog.get(f"{aggregator_name}.energy_bought")["inside"]
                return get_inside_value

            for aggregator_name in self._aggregators_list:
                self.add(f"{aggregator_name}.energy_sold", create_get_inside_value(aggregator_name))
                self.add(f"{aggregator_name}.energy_bought", create_get_inside_value(aggregator_name))
        else:
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status=None)

        def create_self_consumption_function(aggregator_name):  # this function returns a function calculating the unbalance value of the agent for the considered

            if self._global:  # in the global case,

                def get_self_consumption(name):
                    energy_sold_inside = self._catalog.get(f"{aggregator_name}.energy_sold")["inside"]
                    energy_bought_inside = self._catalog.get(f"{aggregator_name}.energy_bought")["inside"]
                    if energy_bought_inside != 0:  # if some energy is produced locally
                        self_consumption = min(energy_sold_inside / energy_bought_inside, 1) * energy_bought_inside  # the ratio of the energy produced locally being consumed locally
                    else:
                        self_consumption = None

                    return self_consumption

            else:

                def get_self_consumption(name):
                    energy_sold_inside = self._catalog.get(f"{aggregator_name}.energy_sold")["inside"]
                    energy_bought_inside = self._catalog.get(f"{aggregator_name}.energy_bought")["inside"]
                    if energy_bought_inside != 0:  # if some energy is produced locally
                        self_consumption = min(energy_sold_inside / energy_bought_inside, 1)  # the ratio of the energy produced locally being consumed locally
                    else:
                        self_consumption = None

                    return self_consumption

            return get_self_consumption

        def create_coverage_rate_function(aggregator_name):  # this function returns a function calculating the unbalance value of the agent for the considered

            def get_coverage_rate(name):
                energy_sold_inside = self._catalog.get(f"{aggregator_name}.energy_sold")["inside"]
                energy_bought_inside = self._catalog.get(f"{aggregator_name}.energy_bought")["inside"]
                if energy_sold_inside != 0:  # if some energy is consumed locally
                    coverage_rate = min(energy_bought_inside / energy_sold_inside, 1)  # the ratio of the energy consumed locally being produced locally
                else:
                    coverage_rate = None

                return coverage_rate

            return get_coverage_rate

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}_self_consumption", create_self_consumption_function(aggregator_name), graph_status="Y")
            self.add(f"{aggregator_name}_coverage_rate", create_coverage_rate_function(aggregator_name), graph_status="Y")

    # ##########################################################################################
    # Final operations
    # ##########################################################################################

    def final_process(self):  # final process is modified

        if self._global:

            for aggregator_name in self._aggregators_list:
                if self._buffer[f"{aggregator_name}.energy_bought"]["sum"] != 0:
                    mean_energy_bought = self._buffer[f"{aggregator_name}.energy_bought"]["sum"] / (self._buffer[f"{aggregator_name}_self_consumption"]["active_rounds"] - 1)
                else:
                    mean_energy_bought = 1

                if self._buffer[f"{aggregator_name}.energy_sold"]["sum"] != 0:
                    mean_energy_sold = self._buffer[f"{aggregator_name}.energy_sold"]["sum"] / (self._buffer[f"{aggregator_name}_coverage_rate"]["active_rounds"] - 1)
                else:
                    mean_energy_sold = 1

                for key in self._buffer[f"{aggregator_name}.energy_bought"]:
                    self._buffer[f"{aggregator_name}_self_consumption"][key] = self._buffer[f"{aggregator_name}_self_consumption"][key] / mean_energy_bought
                    self._buffer[f"{aggregator_name}_coverage_rate"][key] = self._buffer[f"{aggregator_name}_coverage_rate"][key] / mean_energy_sold

                self._buffer.pop(f"{aggregator_name}.energy_sold")
                self._buffer.pop(f"{aggregator_name}.energy_bought")

        super().final_process()

