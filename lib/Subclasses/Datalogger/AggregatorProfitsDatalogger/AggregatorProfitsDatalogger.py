# These dataloggers exports the balances for aggregators
from src.common.Datalogger import Datalogger
# from src.tools.GraphAndTex import __default_graph_options__


class AggregatorProfitsDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1, graph_options="default"):
        if period == "global":
            super().__init__("aggregator_profits_global", "AggregatorsProfits_global", period)
        else:
            super().__init__(f"aggregator_profits_frequency_{period}", f"AggregatorsProfits_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"aggregators profits"})
        
        def create_get_money_function(aggregator_name):  # this function returns a function calculating the unbalance value of the agent for the considered

            def get_money(name):
                money_earned = sum(self._catalog.get(f"{aggregator_name}.money_earned").values())
                money_spent = sum(self._catalog.get(f"{aggregator_name}.money_spent").values())

                return money_earned - money_spent

            return get_money

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}.profits", create_get_money_function(aggregator_name), graph_status="Y")

