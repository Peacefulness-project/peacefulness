# These dataloggers exports the balances for contracts
from src.common.Datalogger import Datalogger


class ContractBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, world, period=1):
        super().__init__(world, "contract_balances", "ContractsBalances.txt", period)

        self.add("simulation_time")
        self.add("physical_time")

        self._contracts_list = self._catalog.get("dictionaries")['contracts'].keys()  # get all the names

        for contract_name in self._contracts_list:  # for each contract registered into world, all the relevant keys are added
            self.add(f"{contract_name}.energy_sold")
            self.add(f"{contract_name}.energy_bought")
            self.add(f"{contract_name}.money_spent")
            self.add(f"{contract_name}.money_earned")


