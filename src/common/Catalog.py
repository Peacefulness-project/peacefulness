# The catalog is the object containing all the data needed
# Data need to appear in the catalog to be exported
from src.tools.Utilities import little_separation, middle_separation, big_separation


class Catalog:

    def __init__(self):
        self._data = dict()

    # ##########################################################################################
    # Data management
    # ##########################################################################################

    def add(self, name, val=None):  # add a key in our catalog, value is optional
        if name in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} already exists")
        self._data[name] = val

    def set(self, name, val):  # setting a value to a pre-existing key
        if name not in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} does not exist")
        self._data[name] = val

    def get(self, name):  # getting the value associated with a key
        if name not in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} does not exist")
        return self._data[name]

    def remove(self, name):
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
    def forecasters(self):  # for read only
        return self._data["dictionaries"]["forecasters"]

    @property
    def strategies(self):  # for read only
        return self._data["dictionaries"]["strategys"]

    @property
    def natures(self):  # for read only
        return self._data["dictionaries"]["natures"]

    @property
    def aggregators(self):  # for read only
        return self._data["dictionaries"]["aggregators"]

    @property
    def exchange_nodes(self):  # for read only
        return self._data["dictionaries"]["exchange_nodes"]

    @property
    def contracts(self):  # for read only
        return self._data["dictionaries"]["contracts"]
    
    @property
    def agents(self):  # for read only
        return self._data["dictionaries"]["agents"]

    @property
    def devices(self):  # for read only
        return self._data["dictionaries"]["devices"]

    @property
    def dataloggers(self):  # for read only
        return self._data["dictionaries"]["dataloggers"]

    @property
    def daemons(self):  # for read only
        return self._data["dictionaries"]["daemons"]


# Exception
class CatalogException(Exception):
    def __init__(self, message):
        super().__init__(message)
