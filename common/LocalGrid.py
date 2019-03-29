# This class represents grids intern to world
# Only clusters or devices connected to the same grid are able to exchange
# This class is especially useful considering heat networks, which are often isolated one from another

from common.Catalog import Catalog


class LocalGrid:

    def __init__(self, name, nature):
        self._name = name  # the name of the grid
        self._nature = nature  # the nature of the grid, only one

        self._catalog = None  # the catalog in which some data are stored

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # link the local grid with the catalog of world

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def nature(self):  # shortcut for read-only
        return self._nature
