# This class represents grids extern to our world, i.e the grid from which world comes from
# The high voltage electric grid is an example of such grid
# For thermal energy, such grid would be uncommon

from common.Catalog import Catalog


class ExternalGrid:

    def __init__(self, name, nature, local_grid):
        self._name = name  # the name of the grid
        self._nature = nature  # the nature of energy in the grid, only one
        self._grid = local_grid  # the local grid it is connected with

        self._price = 0  # the price or stress or whatever to represent the grid will to deliver or absorb energy

        self._catalog = None  # the catalog in which some data are stored

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._add_catalog(catalog)
        self._catalog.add(f"{self._name}.price", self._price)

    def _add_catalog(self, catalog):
        self._catalog = catalog

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

