# List of energy
# This class is just a dictionary containing the different nature of energy
# A representative of this class is created for each world
from copy import deepcopy


class Nature:  # this class contains the different natures
    _list = list()  # a list indexing all types of nature

    def __init__(self, name, description):
        Nature._list = list()  # a list indexing all types of nature

        if name in Nature._list:
            raise NatureException(f"{name} is already a defined nature")
        else:
            Nature._list.append(name)
            self._name = name

        self.description = description
        self._grid = False

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def has_external_grid(self):
        return self._grid

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

