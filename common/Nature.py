# List of energy
# This class is just a dictionary containing the different nature of energy
# A representative of this class is created for each world
from copy import deepcopy


class Nature:  # this class contains the different natures
    _list = list()  # a list indexing all types of nature

    def __init__(self, name):
        Nature._list = list()  # a list indexing all types of nature

        if name in Nature._list:
            raise NatureException(f"{name} is already a defined nature")
        else:
            Nature._list.append(name)
            self._name = name

        self.description = None
        self._grid = False

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def add_description(self, description):  # allows to add a description for an energy type
        self.description = description

    def set_external_grid(self):
        if self._grid:
            raise NatureException(f"a grid has already been defined for {self.name}")
        else:
            self._grid = True

    @property
    def has_external_grid(self):
        return self._grid

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    def list(cls):  # a method allowing to get a list of energy types
        return cls._list

    list = classmethod(list)

    @property
    def name(self):  # shortcut for read-only
        return self._name


# Exception
class NatureException(Exception):
    def __init__(self, message):
        super().__init__(message)

