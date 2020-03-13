# These dataloggers exports the balances for natures
from src.common.Datalogger import Datalogger


class NatureBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, world, period=1):
        super().__init__(world, "nature_balances", "NaturesBalances.txt", period)

        self.add("simulation_time")
        self.add("physical_time")

        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        for nature_name in self._natures_list:  # for each nature registered into world, all the relevant keys are added
            self.add(f"{nature_name}.energy_consumed")
            self.add(f"{nature_name}.energy_produced")
            self.add(f"{nature_name}.money_spent")
            self.add(f"{nature_name}.money_earned")

