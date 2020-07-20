# These dataloggers exports the balances for contracts
from src.common.Datalogger import Datalogger


class ContractBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1):
        if period == "global":
            super().__init__("contract_balances_global", "ContractsBalances_global", period)
        else:
            super().__init__(f"contract_balances_frequency_{period}", f"ContractsBalances_frequency_{period}", period)

        self._contracts_list = self._catalog.get("dictionaries")['contracts'].keys()  # get all the names

        for contract_name in self._contracts_list:  # for each contract registered into world, all the relevant keys are added
            self.add(f"{contract_name}.energy_sold")
            self.add(f"{contract_name}.energy_bought")
            self.add(f"{contract_name}.money_spent")
            self.add(f"{contract_name}.money_earned")


