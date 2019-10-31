# This class represents "energy clusters", i.e a group of devices which maximises
# self-consumption (local consumption of local production)
# As an example, it can represent a house with a solar panel
from common.Catalog import Catalog
from common.Nature import Nature


class Cluster:

    def __init__(self, name, nature, supervisor):
        self._name = name  # the name written in the catalog
        self._nature = nature  # the nature of energy of the cluster

        self._catalog = None  # the catalog in which some data are stored

        self.supervisor = supervisor

        self._devices = list()  # a list of all the devices managed by the cluster

        self._clusters = list()  # a list of all the clusters managed by the cluster

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world

        self._catalog.add(f"{self.name}.energy_ flux")  # accounts for the energy exchanged by the cluster during the round
        self._catalog.add(f"{self.name}.money_flux")  # accounts for the money exchanged by the cluster during the round

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def supervision(self):  # here, the cluster chooses how to distribute energy and if it exchanges with others clusters
        pass

    def ask(self):

        for under_cluster in self.clusters:  # recursive function to go as deep as possible
            under_cluster.ask()

        for device in self.devices:
            device.update()

        self.supervisor.publish_needs()  # determine lots price/quantities regarding tariffs and penalties under it

    def distribute(self):

        self.supervisor.distribute()  # determines who gets what

        for under_cluster in self.clusters:  # recursive function to go as deep as possible
            under_cluster.distribute()

        for device in self.devices:
            device.react()

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

