#  This sheet describes the supervisor, i.e the component ruling the distribution of energy in our grid

from common.Core import World
from common.Catalog import Catalog


class Supervisor:  # generic class supervisor

    def __init__(self, name):
        self._name = name
        self._catalog = None

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def initialize(self, world=None):  # initialization of the supervisor by adding entries later used in the catalog
        if not world:  # if no world is given, the main world is the default value
            world = self._world  # this operation allows not to give a name when calling the method

        for subworld in world._subworlds:
            self.initialize(world._subworlds[subworld])

        for nature in world._natures:
            self._catalog.add(f"{world._name}_{nature}_consumer_balance", 0)
            self._catalog.add(f"{world._name}_{nature}_producer_balance", 0)

    def _add_catalog(self, catalog):  # add a catalog
        self._catalog = catalog

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def process(self):
        pass

    def make_balance(self, world=None):  # make the balance for the world and for each subworld recursively
        if not world:  # if no world is given, the main world is the default value
            world = self._world  # this operation allows not to give a name when the method is called

        balance = dict()  # balance is a dictionary containing the balance for each energy type in the world
        for nature in world._natures:
            balance[nature] = [0, 0]  # balance contains the consumption total in first position
        # and the production total in second

        for subworld in world._subworlds:  # recuperation of the balance of subworlds
            self.make_balance(world._subworlds[subworld])

        for nature in world._natures:
            balance[nature][0] += world._catalog.get(f"{world._name}_{nature}_consumer_balance")
            balance[nature][1] += world._catalog.get(f"{world._name}_{nature}_producer_balance")

        for key in world._consumers:  # calculus of the total of consumption
            consumer = world._consumers[key]
            balance[consumer._nature][0] += consumer._energy

        for key in world._producers:  # calculus of the total of production
            producer = world._producers[key]
            balance[producer._nature][1] += producer._energy

        for nature in world._natures:  # saving the balance in the catalog
            self._catalog.set(f"{world._name}_{nature}_consumer_balance", balance[nature][0])
            self._catalog.set(f"{world._name}_{nature}_producer_balance", balance[nature][1])

    # ##########################################################################################
    # Utility
    # ##########################################################################################


