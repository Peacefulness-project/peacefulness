# These dataloggers exports the balances for aggregators
from src.common.Datalogger import Datalogger


class AggregatorBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1):
        if period == "global":
            super().__init__("aggregator_balances_global", "AggregatorsBalances_global.txt", period)
        else:
            super().__init__(f"aggregator_balances_frequency_{period}", f"AggregatorsBalances_frequency_{period}.txt", period)

        def create_get_energy_function(aggregator_name, bought_or_sold, inside_or_outside):  # this function returns a function calculating the unbalance value of the agent for the considered

            def get_energy(name):
                return self._catalog.get(f"{aggregator_name}.energy_{bought_or_sold}")[inside_or_outside]

            return get_energy
        
        def create_get_money_function(aggregator_name, spent_or_earned, inside_or_outside):  # this function returns a function calculating the unbalance value of the agent for the considered

            def get_money(name):
                return self._catalog.get(f"{aggregator_name}.money_{spent_or_earned}")[inside_or_outside]

            return get_money

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}.energy_sold_inside", create_get_energy_function(aggregator_name, "sold", "inside"))
            self.add(f"{aggregator_name}.energy_sold_outside", create_get_energy_function(aggregator_name, "sold", "outside"))

            self.add(f"{aggregator_name}.energy_bought_inside", create_get_energy_function(aggregator_name, "bought", "inside"))
            self.add(f"{aggregator_name}.energy_bought_outside", create_get_energy_function(aggregator_name, "bought", "outside"))

            self.add(f"{aggregator_name}.money_spent_inside", create_get_money_function(aggregator_name, "spent", "inside"))
            self.add(f"{aggregator_name}.money_spent_outside", create_get_money_function(aggregator_name, "spent", "outside"))

            self.add(f"{aggregator_name}.money_earned_inside", create_get_money_function(aggregator_name, "earned", "inside"))
            self.add(f"{aggregator_name}.money_earned_outside", create_get_money_function(aggregator_name, "earned", "outside"))

