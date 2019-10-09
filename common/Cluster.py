# This class represents "energy clusters", i.e a group of devices which maximises
# self-consumption (local consumption of local production)
# As an example, it can represent a house with a solar panel
from common.Catalog import Catalog
from common.Nature import Nature


class Cluster:

    def __init__(self, name, nature, supervisor, is_grid=False):
        self._name = name  # the name written in the catalog
        self._nature = nature  # the nature of energy of the cluster

        self._is_grid = is_grid  # the local grid the cluster is connected with

        self._catalog = None  # the catalog in which some data are stored

        self.supervisor = supervisor

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world

        self._catalog.add(f"{self.name}.energy_ flux")  # accounts for the energy exchanged by the cluster during the round
        self._catalog.add(f"{self.name}.money_flux")  # accounts for the money exchanged by the cluster during the round

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def supervision(self):  # here, the cluster chooses how to distribute energy and if it exchanges with others clusters
        pass

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
    def is_grid(self):  # shortcut for read-only
        return self._is_grid

