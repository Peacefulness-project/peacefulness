# This class represents agent i.e the people or the enterprise which owns
# consumption and/or production points
# It is linked with a contract
from src.tools.GlobalWorld import get_world


class Agent:

    def __init__(self, name, superior=None):
        self._name = name  # the name written in the catalog

        self._contracts = dict()  # the contract defines the type of strategy relevant
        # for the agent for each nature of energy. A contract is a keyword (for now, at least)

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # the catalog in which some data are stored
        
        self._superior = superior  # the potential owner this agent has. It is another agent
        self._owned_agents_name = []  # a list containing all the agents owned by this one

        # Creation of specific entries in the catalog
        self._catalog.add(f"{self.name}.money_spent", 0)  # accounts for the money spent by the agent to buy energy during the round
        self._catalog.add(f"{self.name}.money_earned", 0)  # accounts for the money earned by the agent by selling energy during the round

        world.register_agent(self)  # register this agent into world dedicated dictionary

    # ##########################################################################################
    # Dynamic behaviour
    ############################################################################################

    def reinitialize(self):  # reinitialization of the balances
        self._catalog.set(f"{self.name}.money_spent", 0)  # money spent by the agent to buy energy during the round
        self._catalog.set(f"{self.name}.money_earned", 0)  # money earned by the agent by selling energy during the round

        for nature in self.natures:
            cumulated_effort = self._catalog.get(f"{self.name}.{nature.name}.effort")["cumulated_effort"]  # effort management
            self._catalog.set(f"{self.name}.{nature.name}.effort", {"current_round_effort": 0, "cumulated_effort": cumulated_effort})  # current effort is reinitialized

            self._catalog.set(f"{self.name}.{nature.name}.energy_bought", 0)  # energy received by the agent during the current round
            self._catalog.set(f"{self.name}.{nature.name}.energy_sold", 0)  # energy delivered by the agent during the current round

            self._catalog.set(f"{self.name}.{nature.name}.energy_erased", 0)  # quantity of energy wanted but not served by the supervisor

    def report(self):  # function allowing agents to get information from their owned agents and pass it to their superior
        for agent in self._owned_agents_name:
            agent.report()

        if self._superior:  # if the agent has a superior, it increments its balances
            for nature in self.natures:  # balance on energy nature
                energy_sold_herself = self._catalog.get(f"{self.name}.{nature.name}.energy_sold")
                energy_sold_superior = self._catalog.get(f"{self._superior.name}.{nature.name}.energy_sold")
                self._catalog.set(f"{self._superior.name}.{nature.name}.energy_sold", energy_sold_herself + energy_sold_superior)

                energy_bought_herself = self._catalog.get(f"{self.name}.{nature.name}.energy_bought")
                energy_bought_superior = self._catalog.get(f"{self._superior.name}.{nature.name}.energy_bought")
                self._catalog.set(f"{self._superior.name}.{nature.name}.energy_bought", energy_bought_herself + energy_bought_superior)

                energy_erased_herself = self._catalog.get(f"{self.name}.{nature.name}.energy_erased")
                energy_erased_superior = self._catalog.get(f"{self._superior.name}.{nature.name}.energy_erased")
                self._catalog.set(f"{self._superior.name}.{nature.name}.energy_erased", energy_erased_herself + energy_erased_superior)

            money_spent_herself = self._catalog.get(f"{self.name}.money_spent")
            money_spent_superior = self._catalog.get(f"{self._superior.name}.money_spent")
            self._catalog.set(f"{self._superior.name}.money_spent", money_spent_herself + money_spent_superior)

            money_earned_herself = self._catalog.get(f"{self.name}.money_earned")
            money_earned_superior = self._catalog.get(f"{self._superior.name}.money_earned")
            self._catalog.set(f"{self._superior.name}.money_earned", money_earned_herself + money_earned_superior)
        
    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def add_effort(self, effort, nature):
        current_effort = self._catalog.get(f"{self.name}.{nature.name}.effort")["current_round_effort"] + effort
        cumulated_effort = self._catalog.get(f"{self.name}.{nature.name}.effort")["cumulated_effort"] + effort
        self._catalog.set(f"{self.name}.{nature.name}.effort", {"current_round_effort": current_effort, "cumulated_effort": cumulated_effort})

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def natures(self):  # shortcut for read-only
        return self._contracts.keys()

    @property
    def contracts(self):  # shortcut for read-only
        return self._contracts.values()

    @property
    def superior(self):  # shortcut for read-only
        return self._superior




