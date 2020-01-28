# This class represents "energy clusters", i.e a group of devices which maximises
# self-consumption (local consumption of local production)
# As an example, it can represent a house with a solar panel
from common.Catalog import Catalog
from common.Nature import Nature

from math import inf


class Cluster:

    def __init__(self, name, nature, supervisor, superior="exchange", efficiency=1, capacity=inf):
        self._name = name  # the name written in the catalog
        self._nature = nature  # the nature of energy of the cluster

        self._catalog = None  # the catalog in which some data are stored

        self._supervisor = supervisor

        self.superior = superior  # the object the cluster is obeying
        # it can be either another cluster either a exchanger

        self._devices = list()  # a list of all the devices managed by the cluster
        self._subclusters = list()  # a list of all the clusters managed by the cluster

        self.quantities = dict()  # a dictionary containing, for each device and each subcluster, the quantity asked, the price billed, the quantity delivered and the price it cost it

        # todo: me virer ce merdier et le faire proprement
        # hors de question que ce soit fige a la declaration comme ça
        # a stocker dans un dico au niveau de world plutot
        self.efficiency = efficiency
        self.capacity = capacity

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world

        self._catalog.add(f"{self.name}.quantities_asked", [])  # couples price/quantities sent by the cluster to its superior
        self._catalog.add(f"{self.name}.quantities_given", [])  # couple price/quantities accorded by the cluster superior

        self._catalog.add(f"{self.name}.energy_bought", {"inside": 0, "outside": 0})  # accounts for the energy bought by the cluster during the round
        self._catalog.add(f"{self.name}.energy_sold", {"inside": 0, "outside": 0})  # accounts for the energy sold by the cluster during the round

        self._catalog.add(f"{self.name}.money_spent", {"inside": 0, "outside": 0})  # accounts for the money spent by the cluster to buy energy during the round
        self._catalog.add(f"{self.name}.money_earned", {"inside": 0, "outside": 0})  # accounts for the money earned by the cluster by selling energy during the round

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the values
        self._catalog.set(f"{self.name}.quantities_asked", [])  # couples price/quantities sent by the cluster to its superior
        self._catalog.set(f"{self.name}.quantities_given", [])  # couple price/quantities accorded by the cluster superior

        self._catalog.set(f"{self.name}.energy_bought", {"inside": 0, "outside": 0})  # accounts for the energy bought by the cluster during the round
        self._catalog.set(f"{self.name}.energy_sold", {"inside": 0, "outside": 0})  # accounts for the energy sold by the cluster during the round

        self._catalog.set(f"{self.name}.money_spent", {"inside": 0, "outside": 0})  # accounts for the money spent by the cluster to buy energy during the round
        self._catalog.set(f"{self.name}.money_earned", {"inside": 0, "outside": 0})  # accounts for the money earned by the cluster by selling energy during the round

    def ask(self):  # clusters make local balances and then publish their needs (both in demand and in offer)
        for managed_cluster in self.subclusters:  # recursive function to reach all clusters
            managed_cluster.ask()

        self._supervisor.ascendant_phase(self)  # makes the balance between local producers and consumers and determines couples price/quantities regarding tariffs and penalties under it

    def distribute(self):  # clusters distribute the energy they exchanged with outside
        self._supervisor.distribute_remote_energy(self)  # distribute the energy acquired from or sold to the exterior

        for managed_cluster in self.subclusters:  # recursive function to reach all clusters
            managed_cluster.distribute()

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
    def subclusters(self):  # shortcut for read-only
        return self._subclusters

