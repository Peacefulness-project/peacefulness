# These dataloggers exports the balances for agents, natures, clusters
from common.Datalogger import Datalogger
from tools.UserClassesDictionary import user_classes_dictionary


class AgentBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self):
        super().__init__("agent_balances", "AgentsBalances.txt")

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


class ClusterBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self):
        super().__init__("cluster_balances", "ClustersBalances.txt")

    def _register(self, catalog):
        self._catalog = catalog

        self.add("simulation_time")
        self.add("physical_time")

        self._clusters_list = self._catalog.get("dictionaries")['clusters'].keys()  # get all the names

        for cluster_name in self._clusters_list:  # for each cluster registered into world, all the relevant keys are added
            self.add(f"{cluster_name}.energy_sold")
            self.add(f"{cluster_name}.energy_bought")
            self.add(f"{cluster_name}.money_spent")
            self.add(f"{cluster_name}.money_earned")


class ContractBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self):
        super().__init__("contract_balances", "ContractsBalances.txt")

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

    def __init__(self):
        super().__init__("nature_balances", "NaturesBalances.txt")

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


user_classes_dictionary[f"{AgentBalanceDatalogger.__name__}"] = AgentBalanceDatalogger
user_classes_dictionary[f"{ClusterBalanceDatalogger.__name__}"] = ClusterBalanceDatalogger
user_classes_dictionary[f"{ContractBalanceDatalogger.__name__}"] = ContractBalanceDatalogger
user_classes_dictionary[f"{NatureBalanceDatalogger.__name__}"] = NatureBalanceDatalogger


