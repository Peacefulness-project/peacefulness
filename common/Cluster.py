# This class represents "energy clusters", i.e a group of devices which maximises
# self-consumption (local consumption of local production)
# As an example, it can represent a house with a solar panel
from common.Catalog import Catalog
from common.Nature import Nature


class Cluster:

    def __init__(self, name, nature, is_grid=False):
        self._name = name  # the name written in the catalog
        self._nature = nature  # the nature of energy of the cluster

        self._is_grid = is_grid  # the local grid the cluster is connected with

        self._catalog = None  # the catalog in which some data are stored

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world
        if self._is_grid:
            self._nature.set_external_grid()

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

