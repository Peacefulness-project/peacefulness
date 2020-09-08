# These dataloggers exports the balances for contracts
from src.common.Datalogger import Datalogger
from src.tools.GraphAndTex import __default_graph_options__


class ContractBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1, graph_options=__default_graph_options__):
        if period == "global":
            super().__init__("contract_balances_global", "ContractsBalances_global", period)
        else:
            super().__init__(f"contract_balances_frequency_{period}", f"ContractsBalances_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"contracts energy", "y2label": f"contracts money"})

        self._contracts_list = self._catalog.get("dictionaries")['contracts'].keys()  # get all the names

        if not self._global:
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status=None)

        for contract_name in self._contracts_list:  # for each contract registered into world, all the relevant keys are added
            self.add(f"{contract_name}.energy_sold", graph_status="Y")
            self.add(f"{contract_name}.energy_bought", graph_status="Y")
            self.add(f"{contract_name}.energy_erased", graph_status="Y")
            self.add(f"{contract_name}.money_spent", graph_status="Y2")
            self.add(f"{contract_name}.money_earned", graph_status="Y2")


