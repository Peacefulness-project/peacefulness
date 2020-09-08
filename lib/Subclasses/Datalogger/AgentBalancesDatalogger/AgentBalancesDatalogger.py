# These dataloggers exports the balances for agents
from src.common.Datalogger import Datalogger

from src.tools.GraphAndTex import __default_graph_options__


class AgentBalancesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1, graph_options=__default_graph_options__):
        if period == "global":
            super().__init__("agent_balances_global", "AgentsBalances_global", period)
        else:
            super().__init__(f"agent_balances_frequency_{period}", f"AgentsBalances_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"agents energy", "y2label": f"agents money"})

        agents_list = self._catalog.get("dictionaries")['agents'].values()  # get all the agents

        def create_imbalance_function(agent_name, nature_name):  # this function returns a function calculating the unbalance value of the agent for the considered
            def imbalance_calculation(name):
                return abs(self._catalog.get(f"{agent_name}.{nature_name}.energy_bought") - self._catalog.get(f"{agent_name}.{nature_name}.energy_sold"))

            return imbalance_calculation

        for agent in agents_list:  # for each aggregator registered into world, all the relevant keys are added

            if not self._global:
                self.add(f"simulation_time", graph_status="X")
                self.add(f"physical_time", graph_status=None)

            for nature in agent.natures:
                self.add(f"{agent.name}.{nature.name}.energy_bought", graph_status="Y")
                self.add(f"{agent.name}.{nature.name}.energy_sold", graph_status="Y")
                self.add(f"{agent.name}.{nature.name}.energy_erased", graph_status="Y")
                self.add(f"{agent.name}.{nature.name}.energy_imbalance", create_imbalance_function(agent.name, nature.name), graph_status="Y")

            self.add(f"{agent.name}.money_spent", graph_status="Y2")
            self.add(f"{agent.name}.money_earned", graph_status="Y2")

