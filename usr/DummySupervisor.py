from common.Supervisor import Supervisor
from common.Catalog import Catalog
from common.Core import World


class DummySupervisor(Supervisor):

    def __init__(self, name, world):
        super().__init__(name, world)
        self._stress = dict()  # a dictionary containing the grid "stress" for each nature and each subworld

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def initialize(self, world=None):
        if not world:  # if no world is given, the main world is the default value
            world = self._world  # this operation allows not to give a name when calling the method

        for subworld in world._subworlds:
            self.initialize(world._subworlds[subworld])

        for nature in world._natures:
            self._catalog.add(f"{world._name}_{nature}_consumer_balance", 0)
            self._catalog.add(f"{world._name}_{nature}_producer_balance", 0)

        self._stress[world._name] = dict()  # it allows to have an entry for each subworld

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def process(self):

        for i in range(self._world._time_limit):
            self._world.update()  # update all the data of entities

            self.make_balance()  # make the energy balance for each world and subworld

            self.stress_calculus()  # calculate a set of values representing the grid "stress" at each level

            self.arbitrage()  # using the stress and the properties of the consumptions and of the productions,
            # the supervisor arbitrates the delivery of energy

            self._world.next()  # update both physical and simulation time, and call dataloggers and daemons

    def stress_calculus(self, world=None):  # calculus of the stress for each level of subworld
        if not world:  # if no world is given, the main world is the default value
            world = self._world  # this operation allows not to give a name when calling the method

        for subworld in world._subworlds:
            self.stress_calculus(world._subworlds[subworld])

        for nature in world._natures:
            cons = self._catalog.get(f"{world._name}_{nature}_consumer_balance")
            prod = self._catalog.get(f"{world._name}_{nature}_producer_balance")

            self._stress[world._name][nature] = cons/prod - prod/cons  # this function has the following behavior:
            # cons/prod --> +inf ==> stress --> +inf
            # cons/prod  =  1    ==> stress  =  1
            # cons/prod --> 0    ==> stress --> -inf
            # but it has no other meaning

    def arbitrage(self, world=None):
        if not world:  # if no world is given, the main world is the default value
            world = self._world  # this operation allows not to give a name when calling the method

        for subworld in world._subworlds:
            self.arbitrage(world._subworlds[subworld])

        # here, a wonderful calculation takes place

        # results are then written in the catalog
        # for the moment, everyone is satisfied and no balance is made at all
        for key in world._producers:
            producer = world._producers[key]
            world.catalog.set(f"{key}.energy", producer._energy)

        for key in world._consumers:
            consumer = world._consumers[key]
            world.catalog.set(f"{key}.energy", consumer._energy)
