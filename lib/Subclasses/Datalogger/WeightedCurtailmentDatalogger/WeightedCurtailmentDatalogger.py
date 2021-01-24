# These dataloggers exports the balances for aggregators
from src.common.Datalogger import Datalogger


class WeightedCurtailmentDatalogger(Datalogger):  # a sub-class of dataloggers designed to export curtailment rates

    def __init__(self, period=1, graph_options="default"):
        if period == "global":
            super().__init__("weighted_curtailment_rate_global", "WeightedCurtailmentRate_global", period)
        else:
            super().__init__(f"weighted_curtailment_rate_frequency_{period}", f"WeightedCurtailmentRate_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"curtailment rate"})

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names

        if self._type == "global":
            def create_get_total_energy(aggregator_name):
                def get_total_energy(name):
                    if "consumption" in name:
                        return self._catalog.get(f"{aggregator_name}.energy_sold")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["consumption"]
                    elif "production" in name:
                        return self._catalog.get(f"{aggregator_name}.energy_bought")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["production"]
                return get_total_energy

            for aggregator_name in self._aggregators_list:
                self.add(f"{aggregator_name}.energy_total_consumption", create_get_total_energy(aggregator_name))
                self.add(f"{aggregator_name}.energy_total_production", create_get_total_energy(aggregator_name))
        else:
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        def create_get_curtailment_rate_function_consumption(aggregator_name):  # this function returns a function calculating
            if self._type == "global":
                def get_curtailment_rate(name):
                    total_energy = self._catalog.get(f"{aggregator_name}.energy_sold")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["consumption"]
                    energy_erased = self._catalog.get(f"{aggregator_name}.energy_erased")["consumption"]

                    if total_energy:  # if this key is not null
                        curtailment_rate = abs(energy_erased / total_energy) * total_energy
                    else:
                        curtailment_rate = None

                    return curtailment_rate

            else:
                def get_curtailment_rate(name):
                    total_energy = self._catalog.get(f"{aggregator_name}.energy_sold")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["consumption"]
                    energy_erased = self._catalog.get(f"{aggregator_name}.energy_erased")["consumption"]

                    if total_energy:  # if this key is not null
                        curtailment_rate = abs(energy_erased / total_energy)
                    else:
                        curtailment_rate = None

                    return curtailment_rate

            return get_curtailment_rate

        def create_get_curtailment_rate_function_production(aggregator_name):  # this function returns a function calculating
            if self._type == "global":  # in the global case,
                def get_curtailment_rate(name):
                    total_energy = self._catalog.get(f"{aggregator_name}.energy_bought")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["production"]
                    energy_erased = self._catalog.get(f"{aggregator_name}.energy_erased")["production"]

                    if self._catalog.get(f"{aggregator_name}.energy_bought")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["production"]:  # if this key is not null
                        curtailment_rate = abs(energy_erased / total_energy) * total_energy
                    else:
                        curtailment_rate = None

                    return curtailment_rate

            else:
                def get_curtailment_rate(name):
                    total_energy = self._catalog.get(f"{aggregator_name}.energy_bought")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["production"]
                    energy_erased = self._catalog.get(f"{aggregator_name}.energy_erased")["production"]

                    if self._catalog.get(f"{aggregator_name}.energy_bought")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["production"]:  # if this key is not null
                        curtailment_rate = abs(energy_erased / total_energy)
                    else:
                        curtailment_rate = None

                    return curtailment_rate

            return get_curtailment_rate

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}.curtailment_rate_consumption", create_get_curtailment_rate_function_consumption(aggregator_name), graph_status="Y")
            self.add(f"{aggregator_name}.curtailment_rate_production", create_get_curtailment_rate_function_production(aggregator_name), graph_status="Y")

    # ##########################################################################################
    # Final operations
    # ##########################################################################################

    def final_process(self):  # final process is modified

        if self._type == "global":

            for aggregator_name in self._aggregators_list:
                if self._buffer[f"{aggregator_name}.energy_total_consumption"]["sum"] != 0:
                    mean_energy_bought = self._buffer[f"{aggregator_name}.energy_total_consumption"]["sum"] / (self._buffer[f"{aggregator_name}.energy_total_consumption"]["active_rounds"] - 1)
                else:
                    mean_energy_bought = 1

                if self._buffer[f"{aggregator_name}.energy_total_production"]["sum"] != 0:
                    mean_energy_sold = self._buffer[f"{aggregator_name}.energy_total_production"]["sum"] / (self._buffer[f"{aggregator_name}.energy_total_production"]["active_rounds"] - 1)
                else:
                    mean_energy_sold = 1

                for key in self._buffer[f"{aggregator_name}.energy_total_consumption"]:
                    self._buffer[f"{aggregator_name}.curtailment_rate_consumption"][key] = self._buffer[f"{aggregator_name}.curtailment_rate_consumption"][key] / mean_energy_bought
                    self._buffer[f"{aggregator_name}.curtailment_rate_production"][key] = self._buffer[f"{aggregator_name}.curtailment_rate_production"][key] / mean_energy_sold

                self._buffer.pop(f"{aggregator_name}.energy_total_consumption")
                self._buffer.pop(f"{aggregator_name}.energy_total_production")

        super().final_process()
