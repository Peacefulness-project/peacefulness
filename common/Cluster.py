# This class represents "energy clusters", i.e a group of devices which maximises
# self-consumption (local consumption of local production)
# As an example, it can represent a house with a solar panel
from common.Catalog import Catalog
from common.Nature import Nature


class Cluster:

    def __init__(self, name, nature, supervisor, superior="exchange"):
        self._name = name  # the name written in the catalog
        self._nature = nature  # the nature of energy of the cluster

        self._catalog = None  # the catalog in which some data are stored

        self._supervisor = supervisor

        self.superior = superior

        self._devices = list()  # a list of all the devices managed by the cluster

        self._clusters = list()  # a list of all the clusters managed by the cluster

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world

        self._catalog.add(f"{self.name}.{self.nature.name}.energy_needs", dict())  # couples price/quantities sent by the cluster to its superior
        self._catalog.add(f"{self.name}.{self.nature.name}.energy_flux", 0)  # accounts for the energy exchanged by the cluster during the round

        self._catalog.add(f"{self.name}.{self.nature.name}.money_spent", 0)  # accounts for the money spent by the cluster to buy energy during the round
        self._catalog.add(f"{self.name}.{self.nature.name}.money_earned", 0)  # accounts for the money earned by the cluster by selling energergy during the round
        self._catalog.add(f"{self.name}.{self.nature.name}.profit", 0)  # accounts for the money earned by the cluster during the round

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ask(self):

        for managed_cluster in self.clusters:  # recursive function to make sure all clusters are reached
            managed_cluster.ask()

        self._supervisor.distribute_local_energy(self)  # makes the balance between local producers and consumers
        self._supervisor.publish_needs(self)  # determines lots price/quantities regarding tariffs and penalties under it

    def distribute(self):

        self._supervisor.distribute_remote_energy(self)  # distribute the energy acquired from or sold to the exterior

        for managed_cluster in self.clusters:  # recursive function to make sure all clusters are reached
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
    def clusters(self):  # shortcut for read-only
        return self._clusters

