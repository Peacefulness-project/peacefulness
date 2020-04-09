# These dataloggers exports the balances for agents
from src.common.Datalogger import Datalogger


class AgentBalanceDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1):
        super().__init__("agent_balances", "AgentsBalances.txt", period)

        self.add("simulation_time")
        self.add("physical_time")

        self._agents_list = self._catalog.get("dictionaries")['agents'].keys()  # get all the names

        for agent_name in self._agents_list:  # for each agent registered into world, all the relevant keys are added
            self.add(f"{agent_name}.energy_sold")
            self.add(f"{agent_name}.energy_bought")
            self.add(f"{agent_name}.money_spent")
            self.add(f"{agent_name}.money_earned")
