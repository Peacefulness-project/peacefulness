# These dataloggers exports the balances for aggregators
from src.common.Datalogger import Datalogger


class CurtailmentDatalogger(Datalogger):  # a sub-class of dataloggers designed to export curtailment rates

    def __init__(self, period=1, graph_options="default"):
        if period == "global":
            super().__init__("curtailment_rate_global", "CurtailmentRate_global", period)
        else:
            super().__init__(f"curtailment_rate_frequency_{period}", f"CurtailmentRate_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"curtailment rate"})

        def create_get_curtailment_rate_function(aggregator_name, consumed_or_produced):  # this function returns a function calculating
            if consumed_or_produced =="consumption":
                def get_curtailment_rate(name):
                    if self._catalog.get(f"{aggregator_name}.energy_sold")["inside"]:  # if this key is not null
                        curtailment_rate = abs(self._catalog.get(f"{aggregator_name}.energy_erased")["consumption"] / (self._catalog.get(f"{aggregator_name}.energy_sold")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["consumption"]))
                    else:
                        curtailment_rate = None

                    return curtailment_rate

                return get_curtailment_rate

            elif consumed_or_produced =="production":
                def get_curtailment_rate(name):
                    if self._catalog.get(f"{aggregator_name}.energy_bought")["inside"]:  # if this key is not null
                        curtailment_rate = abs(self._catalog.get(f"{aggregator_name}.energy_erased")["production"] / (self._catalog.get(f"{aggregator_name}.energy_bought")["inside"] + self._catalog.get(f"{aggregator_name}.energy_erased")["production"]))
                    else:
                        curtailment_rate = None

                    return curtailment_rate

                return get_curtailment_rate

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}.energy_erased_production", create_get_curtailment_rate_function(aggregator_name, "production"), graph_status="Y")
            self.add(f"{aggregator_name}.energy_erased_consumption", create_get_curtailment_rate_function(aggregator_name, "consumption"), graph_status="Y")


