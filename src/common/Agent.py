# This class represents agent i.e the people or the enterprise which owns
# consumption and/or production points
# It is linked with a contract
from src.common.World import World
from src.common.Messages import MessagesManager


class Agent:

    def __init__(self, name: str, superior=None):
        """
        An agent, object representing the owner of the different devices, aggregators and even other agents in some cases.

        Parameters
        ----------
        name: str, name of this agent
        superior: Agent or None, the superior of this agent if any
        """
        self._name = name  # the name written in the catalog

        self._contracts = dict()  # the contract defines the type of strategy relevant
        # for the agent for each nature of energy. A contract is a keyword (for now, at least)

        world = World.ref_world  # get automatically the world defined for this case
        self._catalog = world.catalog  # the catalog in which some data are stored

        if superior:  # if there is a superior
            self._superior_name = superior.name  # register the name of the superior
        else:
            self._superior_name = None
        self._owned_agents_name = []  # a list containing all the agents owned by this one

        # Creation of specific entries in the catalog
        self._catalog.add(f"{self.name}.money_spent", 0)  # accounts for the money spent by the agent to buy energy during the round
        self._catalog.add(f"{self.name}.money_earned", 0)  # accounts for the money earned by the agent by selling energy during the round

        world.register_agent(self)  # register this agent into world dedicated dictionary

    # ##########################################################################################
    # Dynamic behaviour
    ############################################################################################

    def reinitialize(self):  # reinitialization of the balances
        """
        Method called by world to reinitialize energy and money balances at the beginning of each round.
        """
        self._catalog.set(f"{self.name}.money_spent", 0)  # money spent by the agent to buy energy during the round
        self._catalog.set(f"{self.name}.money_earned", 0)  # money earned by the agent by selling energy during the round

        for nature in self.natures:
            self._catalog.set(f"{self.name}.{nature.name}.energy_bought", 0)  # energy received by the agent during the current round
            self._catalog.set(f"{self.name}.{nature.name}.energy_sold", 0)  # energy delivered by the agent during the current round
            self._catalog.set(f"{self.name}.{nature.name}.energy_erased", 0)  # quantity of energy wanted but not served by the supervisor

        for element_name, default_value in MessagesManager.added_information.items():  # for all added elements
            self._catalog.set(f"{self.name}.{element_name}", default_value)

    def report(self):  # function allowing agents to get information from their owned agents and pass it to their superior
        """
        Method used by world to make energy and money balances of the agent. It also updates the balances of the agent superior if any.
        """
        for agent in self._owned_agents_name:
            agent.report()

        if self._superior_name:  # if the agent has a superior, it increments its balances
            for nature in self.natures:  # balance on energy nature
                energy_sold_herself = self._catalog.get(f"{self.name}.{nature.name}.energy_sold")
                energy_sold_superior = self._catalog.get(f"{self._superior_name}.{nature.name}.energy_sold")
                self._catalog.set(f"{self._superior_name}.{nature.name}.energy_sold", energy_sold_herself + energy_sold_superior)

                energy_bought_herself = self._catalog.get(f"{self.name}.{nature.name}.energy_bought")
                energy_bought_superior = self._catalog.get(f"{self._superior_name}.{nature.name}.energy_bought")
                self._catalog.set(f"{self._superior_name}.{nature.name}.energy_bought", energy_bought_herself + energy_bought_superior)

                energy_erased_herself = self._catalog.get(f"{self.name}.{nature.name}.energy_erased")
                energy_erased_superior = self._catalog.get(f"{self._superior_name}.{nature.name}.energy_erased")
                self._catalog.set(f"{self._superior_name}.{nature.name}.energy_erased", energy_erased_herself + energy_erased_superior)

            money_spent_herself = self._catalog.get(f"{self.name}.money_spent")
            money_spent_superior = self._catalog.get(f"{self._superior_name}.money_spent")
            self._catalog.set(f"{self._superior_name}.money_spent", money_spent_herself + money_spent_superior)

            money_earned_herself = self._catalog.get(f"{self.name}.money_earned")
            money_earned_superior = self._catalog.get(f"{self._superior_name}.money_earned")
            self._catalog.set(f"{self._superior_name}.money_earned", money_earned_herself + money_earned_superior)

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

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
        return self._superior_name




