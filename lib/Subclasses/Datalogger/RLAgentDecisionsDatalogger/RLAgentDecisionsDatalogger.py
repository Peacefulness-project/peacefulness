# This datalogger exports the decisions taken by the RL agent
from src.common.Datalogger import Datalogger


class RLAgentDecisionsDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the RL agent's decisions

    def __init__(self, period=1, graph_options="default"):

        super().__init__(f"RL_agent_decisions_{period}", f"RLAgentDecisions_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"agent decisions"})
        
        def create_get_decision_message_function(name):  # the RL agent's decision on energy dispatch inside each aggregator

            def get_decision_message(name):
                
                decision_message = self._catalog.get(f"DRL_Strategy.decision_message")

                return decision_message

            return get_decision_message

        def create_get_exchanges_message_function(name):  # The RL agent's decision on energy exchanges between aggregators

            def get_exchanges_message(name):
                
                exchanges_message = self._catalog.get(f"DRL_Strategy.exchanges_message")

                return exchanges_message

            return get_exchanges_message
        
        self.add("RL_agent_decision_message", create_get_decision_message_function(self._name), graph_status="Y")
        self.add("RL_agent_exchanges_message", create_get_exchanges_message_function(self._name), graph_status="Y")
