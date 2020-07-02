# These dataloggers exports the balances for agents
from src.common.Datalogger import Datalogger


class AgentBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1):
        if period == "global":
            super().__init__("agent_balances_global", "AgentsBalances_global.txt", period)
        else:
            super().__init__(f"agent_balances_frequency_{period}", f"AgentsBalances_frequency_{period}.txt", period)

        agents_list = self._catalog.get("dictionaries")['agents'].values()  # get all the agents

        def create_imbalance_function(agent_name, nature_name):  # this function returns a function calculating the unbalance value of the agent for the considered
            def imbalance_calculation(name):
                return abs(self._catalog.get(f"{agent_name}.{nature_name}.energy_bought") - self._catalog.get(f"{agent_name}.{nature_name}.energy_sold"))

            return imbalance_calculation

        for agent in agents_list:  # for each aggregator registered into world, all the relevant keys are added
            for nature in agent.natures:
                self.add(f"{agent.name}.{nature.name}.energy_bought")
                self.add(f"{agent.name}.{nature.name}.energy_sold")
                self.add(f"{agent.name}.{nature.name}.energy_erased")
                self.add(f"{agent.name}.{nature.name}.energy_imbalance", create_imbalance_function(agent.name, nature.name))

            self.add(f"{agent.name}.money_spent")
            self.add(f"{agent.name}.money_earned")

