# These dataloggers exports the balances for aggregators
from src.common.Datalogger import Datalogger
# from src.tools.GraphAndTex import __default_graph_options__


class AggregatorBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1, graph_options="default"):
        if period == "global":
            super().__init__("aggregator_balances_global", "AggregatorsBalances_global", period)
        else:
            super().__init__(f"aggregator_balances_frequency_{period}", f"AggregatorsBalances_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"aggregators energy", "y2label": f"aggregators money"})

        def create_get_energy_function(aggregator_name, bought_or_sold, inside_or_outside):

            def get_energy(name):
                return self._catalog.get(f"{aggregator_name}.energy_{bought_or_sold}")[inside_or_outside]

            return get_energy

        def create_get_energy_erased_function(aggregator_name, bought_or_sold):

            def get_energy(name):
                return self._catalog.get(f"{aggregator_name}.energy_erased")[bought_or_sold]

            return get_energy

        def create_get_money_function(aggregator_name, spent_or_earned, inside_or_outside):

            def get_money(name):
                return self._catalog.get(f"{aggregator_name}.money_{spent_or_earned}")[inside_or_outside]

            return get_money

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}.energy_sold_inside", create_get_energy_function(aggregator_name, "sold", "inside"), graph_status="Y")
            self.add(f"{aggregator_name}.energy_sold_outside", create_get_energy_function(aggregator_name, "sold", "outside"), graph_status="Y")

            self.add(f"{aggregator_name}.energy_bought_inside", create_get_energy_function(aggregator_name, "bought", "inside"), graph_status="Y")
            self.add(f"{aggregator_name}.energy_bought_outside", create_get_energy_function(aggregator_name, "bought", "outside"), graph_status="Y")

            self.add(f"{aggregator_name}.energy_erased_consumption", create_get_energy_erased_function(aggregator_name, "consumption"), graph_status="Y")
            self.add(f"{aggregator_name}.energy_erased_production", create_get_energy_erased_function(aggregator_name, "production"), graph_status="Y")

            self.add(f"{aggregator_name}.money_spent_inside", create_get_money_function(aggregator_name, "spent", "inside"), graph_status="Y2")
            self.add(f"{aggregator_name}.money_spent_outside", create_get_money_function(aggregator_name, "spent", "outside"), graph_status="Y2")

            self.add(f"{aggregator_name}.money_earned_inside", create_get_money_function(aggregator_name, "earned", "inside"), graph_status="Y2")
            self.add(f"{aggregator_name}.money_earned_outside", create_get_money_function(aggregator_name, "earned", "outside"), graph_status="Y2")

