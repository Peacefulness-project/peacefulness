# These dataloggers exports the balances for natures
from src.common.Datalogger import Datalogger
# from src.tools.GraphAndTex import __default_graph_options__


class NatureBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1, graph_options="default"):
        if period == "global":
            super().__init__("nature_balances_global", "NaturesBalances_global", period)
        else:
            super().__init__(f"nature_balances_frequency_{period}", f"NaturesBalances_frequency_{period}", period, graph_options=graph_options)

        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        for nature_name in self._natures_list:  # for each nature registered into world, all the relevant keys are added
            self.add(f"{nature_name}.energy_consumed", graph_status="Y")
            self.add(f"{nature_name}.energy_produced", graph_status="Y")
            self.add(f"{nature_name}.energy_erased", graph_status="Y")
            self.add(f"{nature_name}.money_spent", graph_status="Y2")
            self.add(f"{nature_name}.money_earned", graph_status="Y2")

