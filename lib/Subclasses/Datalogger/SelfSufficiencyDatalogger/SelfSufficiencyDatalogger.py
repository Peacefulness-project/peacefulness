# this datalogger exports the data considered as results for ECOS proceedings
from src.common.Datalogger import Datalogger
from src.tools.Utilities import adapt_path


class SelfSufficiencyDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1):
        if period == "global":
            super().__init__("self_sufficiency_global", "SelfSufficiency_global.txt", period)
        else:
            super().__init__(f"self_sufficiency_frequency_{period}", f"SelfSufficiency_frequency_{period}.txt", period)

        def create_self_consumption_function(aggregator_name):  # this function returns a function calculating the unbalance value of the agent for the considered

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

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names
        self._agents_list = self._catalog.get("dictionaries")['agents'].keys()  # get all the names
        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}_self_consumption", create_self_consumption_function(aggregator_name))
            self.add(f"{aggregator_name}_coverage_rate", create_coverage_rate_function(aggregator_name))
