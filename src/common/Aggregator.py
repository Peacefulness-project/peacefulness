# This class represents "energy aggregators", i.e a group of devices which maximises
# self-consumption (local consumption of local production)
# As an example, it can represent a house with a solar panel

from math import inf


class Aggregator:

    def __init__(self, name, nature, strategy, superior=None, efficiency=1, capacity=inf):
        self._name = name  # the name written in the catalog
        self._nature = nature  # the nature of energy of the aggregator

        self._catalog = None  # the catalog in which some data are stored

        self._strategy = strategy  # the strategy, i.e the strategy applied by this aggregator

        self.superior = superior  # the other aggregator this one is obeying to
        # It can be None

        self._devices = list()  # a list of all the devices managed by the aggregator
        self._subaggregators = list()  # a list of all the aggregators managed by the aggregator

        self.quantities = dict()  # a dictionary containing, for each device and each subaggregator, the quantity asked, the price billed, the quantity delivered and the price it cost it

        # todo: me virer ce merdier et le faire proprement (mais après discussion avec Sterwin)
        # hors de question que ce soit fige a la declaration comme ça
        # a stocker dans un dico au niveau de world plutot
        self.efficiency = efficiency
        self.capacity = capacity

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world

        self._catalog.add(f"{self.name}.quantities_asked", [])  # couples price/quantities sent by the aggregator to its superior
        self._catalog.add(f"{self.name}.quantities_given", [])  # couple price/quantities accorded by the aggregator superior

        self._catalog.add(f"{self.name}.energy_bought", {"inside": 0, "outside": 0})  # accounts for the energy bought by the aggregator during the round
        self._catalog.add(f"{self.name}.energy_sold", {"inside": 0, "outside": 0})  # accounts for the energy sold by the aggregator during the round

        self._catalog.add(f"{self.name}.money_spent", {"inside": 0, "outside": 0})  # accounts for the money spent by the aggregator to buy energy during the round
        self._catalog.add(f"{self.name}.money_earned", {"inside": 0, "outside": 0})  # accounts for the money earned by the aggregator by selling energy during the round

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the values
        self._catalog.set(f"{self.name}.quantities_asked", [])  # couples price/quantities sent by the aggregator to its superior
        self._catalog.set(f"{self.name}.quantities_given", [])  # couple price/quantities accorded by the aggregator superior

        self._catalog.set(f"{self.name}.energy_bought", {"inside": 0, "outside": 0})  # accounts for the energy bought by the aggregator during the round
        self._catalog.set(f"{self.name}.energy_sold", {"inside": 0, "outside": 0})  # accounts for the energy sold by the aggregator during the round

        self._catalog.set(f"{self.name}.money_spent", {"inside": 0, "outside": 0})  # accounts for the money spent by the aggregator to buy energy during the round
        self._catalog.set(f"{self.name}.money_earned", {"inside": 0, "outside": 0})  # accounts for the money earned by the aggregator by selling energy during the round

    def ask(self):  # aggregators make local balances and then publish their needs (both in demand and in offer)
        for managed_aggregator in self.subaggregators:  # recursive function to reach all aggregators
            managed_aggregator.ask()

        self._strategy.ascendant_phase(self)  # makes the balance between local producers and consumers and determines couples price/quantities regarding tariffs and penalties under it

    def distribute(self):  # aggregators distribute the energy they exchanged with outside
        self._strategy.distribute_remote_energy(self)  # distribute the energy acquired from or sold to the exterior

        for managed_aggregator in self.subaggregators:  # recursive function to reach all aggregators
            managed_aggregator.distribute()

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def devices(self):  # shortcut for read-only
        return self._devices

    @property
    def subaggregators(self):  # shortcut for read-only
        return self._subaggregators

