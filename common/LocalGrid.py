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

    def _add_catalog(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog


