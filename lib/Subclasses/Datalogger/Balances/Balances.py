# These dataloggers exports the balances for agents, natures, clusters
from src.common.Datalogger import Datalogger


class AgentBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, world, period=0):
        super().__init__(world, "agent_balances", "AgentsBalances.txt", period)

    def _register(self, catalog):
        self._catalog = catalog

        self.add("simulation_time")
        self.add("physical_time")

        self._agents_list = self._catalog.get("dictionaries")['agents'].keys()  # get all the names

        for agent_name in self._agents_list:  # for each agent registered into world, all the relevant keys are added
            self.add(f"{agent_name}.energy_sold")
            self.add(f"{agent_name}.energy_bought")
            self.add(f"{agent_name}.money_spent")
            self.add(f"{agent_name}.money_earned")


class AggregatorBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, world, period=0):
        super().__init__(world, "aggregator_balances", "AggregatorsBalances.txt", period)

    def _register(self, catalog):
        self._catalog = catalog

        self.add("simulation_time")
        self.add("physical_time")

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}.energy_sold")
            self.add(f"{aggregator_name}.energy_bought")
            self.add(f"{aggregator_name}.money_spent")
            self.add(f"{aggregator_name}.money_earned")


class ContractBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, world, period=0):
        super().__init__(world, "contract_balances", "ContractsBalances.txt", period)

    def _register(self, catalog):
        self._catalog = catalog

        self.add("simulation_time")
        self.add("physical_time")

        self._contracts_list = self._catalog.get("dictionaries")['contracts'].keys()  # get all the names

        for contract_name in self._contracts_list:  # for each contract registered into world, all the relevant keys are added
            self.add(f"{contract_name}.energy_sold")
            self.add(f"{contract_name}.energy_bought")
            self.add(f"{contract_name}.money_spent")
            self.add(f"{contract_name}.money_earned")


class NatureBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, world, period=0):
        super().__init__(world, "nature_balances", "NaturesBalances.txt", period)

    def _register(self, catalog):
        self._catalog = catalog

        self.add("simulation_time")
        self.add("physical_time")

        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        for nature_name in self._natures_list:  # for each nature registered into world, all the relevant keys are added
            self.add(f"{nature_name}.energy_consumed")
            self.add(f"{nature_name}.energy_produced")
            self.add(f"{nature_name}.money_spent")
            self.add(f"{nature_name}.money_earned")


