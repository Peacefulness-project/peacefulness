# A catalog is an object containing all the data needed


class Catalog:

    def __init__(self):
        self._data = dict()

# ##########################################################################################
# Data management
# ##########################################################################################

    def add(self, name, val=None):  # add a key in our catalog, value is an option
        if name in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} already exists")
        self._data[name]=val

    def set(self, name, val):  # setting a value to a pre-existing key
        if name not in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} does not exist")
        self._data[name] = val

    def get(self, name):  # getting the value associated with a key
        if name not in self._data:  # checking if the key already exists
            raise CatalogException(f"key {name} does not exist")
        return self._data[name]

# ##########################################################################################
# Utilities
# ##########################################################################################

    @property
    def keys(self):
        return self._data.keys()

    def __str__(self):  # calling our catalog will return the number of items
        return f"Calalog : {len(self._data)} items"

    def print_debug(self):  # print_debug returns the number of items and the keys with their values
        print("=================================================")
        print(f"Calalog : {len(self._data)} items")
        print("-------------------------------------------------")
        for key in self._data:
            print(f"{key} = {self.get(key)}")
        print("=================================================")


# Exception
class CatalogException(Exception):
    def __init__(self, message):
        super().__init__(message)


