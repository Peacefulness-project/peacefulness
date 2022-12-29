# The catalog is the object containing all the data needed
# Data need to appear in the catalog to be exported
from src.tools.Utilities import little_separation, middle_separation, big_separation


class Catalog:
    """
    Catalogs are in charge of containing data needed by several objects. Usually, all this data concerns only the ongoing round.
    """

    def __init__(self):
        """
        Catalogs are automatically instantiated during the instantiation of a world.
        """
        self._data = dict()

    # ##########################################################################################
    # Data management
    # ##########################################################################################

    def add(self, name: str, value=None):  # add a key in our catalog, value is optional
        """
        Adds a key to the catalog and gives the possibility to set its value during the first round.

        Parameters
        ----------
        name: str, name with which the key will be stored in the catalog.
        value: Any type, the value used during the first round. Set to None by default.
        """
        if name in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} already exists")
        self._data[name] = value

    def set(self, name: str, value):  # setting a value to a pre-existing key
        """
        Changes the value of a key in the catalog.

        Parameters
        ----------
        name: str, the key whose value changes
        value: Any type, the new value
        """
        if name not in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} does not exist")
        self._data[name] = value

    def get(self, name: str):  # getting the value associated with a key
        """
        Returns the value of the key.

        Parameters
        ----------
        name: str
        """
        if name not in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} does not exist")
        return self._data[name]

    def remove(self, name: str):
        """
        Removes a key from the catalog.

        Parameters
        ----------
        name: str
        """
        if name not in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} does not exist")
        self._data.pop(name)

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def keys(self):  # for read only
        return self._data.keys()

    def __str__(self):  # calling our catalog will return the number of items
        return middle_separation + f"\nCatalog : {len(self._data)} items"

    def print_debug(self):  # print_debug returns the number of items and the keys with their values
        print(big_separation)
        print(f"Catalog : {len(self._data)} items")
        print(little_separation)
        for key in self._data:
            print(f"{key} = {self.get(key)}")
    
    # ##########################################################################################
    # Dictionaries direct access
    # ##########################################################################################

    @property
    def natures(self):  # for read only
        return self._data["dictionaries"]["natures"]

    @property
    def daemons(self):  # for read only
        return self._data["dictionaries"]["daemons"]

    @property
    def strategies(self):  # for read only
        return self._data["dictionaries"]["strategies"]

    @property
    def agents(self):  # for read only
        return self._data["dictionaries"]["agents"]

    @property
    def contracts(self):  # for read only
        return self._data["dictionaries"]["contracts"]

    @property
    def aggregators(self):  # for read only
        return self._data["dictionaries"]["aggregators"]

    @property
    def devices(self):  # for read only
        return self._data["dictionaries"]["devices"]

    @property
    def dataloggers(self):  # for read only
        return self._data["dictionaries"]["dataloggers"]

    @property
    def graph_options(self):  # for read only
        return self._data["dictionaries"]["graph_options"]


# Exception
class CatalogException(Exception):
    def __init__(self, message):
        super().__init__(message)
