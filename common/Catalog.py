class Catalog:

    def __init__(self):
        self._data = dict()

    def add(self,name, val=None):
        if name in self._data:
            raise CatalogException(f"key {name} already exists")
        self._data[name]=val

    def set(self,name, val):
        if not name in self._data:
            raise CatalogException(f"key {name} does not exist")
        self._data[name] = val

    def get(self,name):
        if not name in self._data:
            raise CatalogException(f"key {name} does not exist")
        return self._data[name]


    @property
    def keys(self):
        return self._data.keys()

    def __str__(self):
        return f"Calalog : {len(self._data)} items"

    def print_debug(self):
        print("=================================================")
        print(f"Calalog : {len(self._data)} items")
        print("-------------------------------------------------")
        for key in self._data:
            print(f"{key} = {self.get(key)}")
        print("=================================================")


class CatalogException(Exception):
    def __init__(self,message):
        super().__init__(message)


