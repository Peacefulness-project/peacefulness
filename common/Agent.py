# This class represents agent i.e the people or the enterprise which owns
# consumption and/or production points
# It is linked with a contract
from common.Catalog import Catalog


class Agent:

    def __init__(self, name):
        self._name = name  # the name written in the catalog
        # self._natures = list()  # allows to check easily the natures of an agent
        self._contract = dict()  # the contract defines the type of strategy relevant
        # for the agent for each nature of energy. A contract is a keyword

        self._catalog = None  # the catalog in which some data are stored

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    # def add_nature(self, nature):  # method to add a nature for an agent
    #     self._natures.append(nature)  # adds the chosen nature to the list
    #
    #     if self._catalog is not None:  # if the catalog is defined, a new entry is created
    #         self._catalog.add(f"{self._name}.{nature}")

    def set_contract(self, nature, contract):  # a method which defines the contract of the agent
        self._contract[nature] = contract  # add a key in the contract dictionary
        self._catalog.add(f"{self._name}.{nature}", contract)  # add an entry in the catalog to make it public

    def add_catalog(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog

        self._catalog.add(f"{self._name}.dissatisfaction", 0)  # dissatisfaction accounts for the energy
        # not delivered immediately. The higher it is, the higher is the chance of being served
        self._catalog.add(f"{self._name}.money", 0)  # the money earned or spent by the agent during the current round
