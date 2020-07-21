# These dataloggers exports the balances for natures
from src.common.Datalogger import Datalogger


class NatureBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1):
        if period == "global":
            super().__init__("nature_balances_global", "NaturesBalances_global", period)
        else:
            super().__init__(f"nature_balances_frequency_{period}", f"NaturesBalances_frequency_{period}", period)

        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        if not self._global:
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status=None)

        for nature_name in self._natures_list:  # for each nature registered into world, all the relevant keys are added
            self.add(f"{nature_name}.energy_consumed")
            self.add(f"{nature_name}.energy_produced")
            self.add(f"{nature_name}.money_spent")
            self.add(f"{nature_name}.money_earned")

