# This class represents agent i.e the people or the enterprise which owns
# consumption and/or production points
# It is linked with a contract
from common.Catalog import Catalog
from common.Contract import Contract


class Agent:

    def __init__(self, name):
        self._name = name  # the name written in the catalog

        self._contracts = dict()  # the contract defines the type of strategy relevant
        # for the agent for each nature of energy. A contract is a keyword (for now, at least)

        self._catalog = None  # the catalog in which some data are stored

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def set_contract(self, nature, contract):  # a method which defines the contract of the agent
        # self._contracts[nature] = contract  # add a contract for an energy nature
        pass

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the agent with the catalog of world

        # Creation of specific entries
        self._catalog.add(f"{self.name}.money_spent", 0)  # accounts for the money spent by the cluster to buy energy during the round
        self._catalog.add(f"{self.name}.money_earned", 0)  # accounts for the money earned by the cluster by selling energy during the round

        self._catalog.add(f"{self.name}.energy_erased", 0)

        self._catalog.add(f"{self.name}.energy_bought", 0)  # the energy received by the agent during the current round
        self._catalog.add(f"{self.name}.energy_sold", 0)  # the energy delivered by the agent during the current round

    # ##########################################################################################
    # Dynamic behaviour
    ############################################################################################

    def reinitialize(self):  # reinitialization of the values
        self._catalog.set(f"{self.name}.money_spent", 0)  # money spent by the cluster to buy energy during the round
        self._catalog.set(f"{self.name}.money_earned", 0)  # money earned by the cluster by selling energy during the round

        self._catalog.set(f"{self.name}.energy_erased", 0)

        self._catalog.set(f"{self.name}.energy_bought", 0)  # energy received by the agent during the current round
        self._catalog.set(f"{self.name}.energy_sold", 0)  # energy delivered by the agent during the current round

        for nature in self.natures:  # effort management
            cumulated_effort = self._catalog.get(f"{self.name}.{nature.name}.effort")["cumulated_effort"]
            self._catalog.set(f"{self.name}.{nature.name}.effort", {"current_round_effort": 0, "cumulated_effort": cumulated_effort})  # current effort is reinitialized

    def make_balance(self):

        for nature in self.natures:  # balance on energy nature
            energy_produced = self._catalog.get(f"{self.name}.energy_sold")
            self._catalog.set(f"{nature.name}.energy_produced", energy_produced)

            energy_consumed = self._catalog.get(f"{self.name}.energy_bought")
            self._catalog.set(f"{nature.name}.energy_consumed", energy_consumed)

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




