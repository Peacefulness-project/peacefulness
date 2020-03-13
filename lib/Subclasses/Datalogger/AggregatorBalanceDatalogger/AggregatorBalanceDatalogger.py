# These dataloggers exports the balances for aggregators
from src.common.Datalogger import Datalogger


class AggregatorBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, world, period=1):
        super().__init__(world, "aggregator_balances", "AggregatorsBalances.txt", period)

        self.add("simulation_time")
        self.add("physical_time")

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}.energy_sold")
            self.add(f"{aggregator_name}.energy_bought")
            self.add(f"{aggregator_name}.money_spent")
            self.add(f"{aggregator_name}.money_earned")
