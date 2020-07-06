# List of energy
# This class is just a dictionary containing the different nature of energy
# A representative of this class is created for each world
from src.tools.GlobalWorld import get_world


class Nature:  # this class contains the different natures
    _list = list()  # a list indexing all types of nature

    def __init__(self, name, description):
        Nature._list = list()  # a list indexing all types of nature

        if name in Nature._list:  # to avoid double definitions
            raise NatureException(f"{name} is already a defined nature")
        else:
            Nature._list.append(name)
            self._name = name  # the name of the nature, which is used as a keyword

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # the catalog in which some data are stored

        self.description = description  # a description of the nature

        # Creation of specific entries in the catalog
        self._catalog.add(f"{self.name}.energy_produced", 0)  # total of energy of this nature produced during the round
        self._catalog.add(f"{self.name}.energy_consumed", 0)  # total of energy of this nature consumed during the round

        self._catalog.add(f"{self.name}.money_spent", 0)  # energy received by the nature during the current round
        self._catalog.add(f"{self.name}.money_earned", 0)  # energy delivered by the nature during the current round

        world.register_nature(self)  # register this nature into world dedicated dictionary

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):  # reinitialization of the values
        self._catalog.set(f"{self.name}.energy_produced", 0)  # total of energy of this nature produced during the round
        self._catalog.set(f"{self.name}.energy_consumed", 0)  # total of energy of this nature consumed during the round

        self._catalog.set(f"{self.name}.money_spent", 0)  # energy received by the agent during the current round
        self._catalog.set(f"{self.name}.money_earned", 0)  # energy delivered by the agent during the current round

        for element in self._catalog.get("additional_elements"):
            self._catalog.set(f"{self.name}.{element}", self._catalog.get("additional_elements")[element])

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

