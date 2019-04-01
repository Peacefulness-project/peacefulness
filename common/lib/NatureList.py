# List of energy
# This class is just a dictionary containing the different nature of energy
# A representative of this class is created for each world
from copy import deepcopy


class NatureList:  # this class contains the different natures

    def __init__(self):
        self._dict = dict()  # a dictionary indexing all types of nature
        self._dict["LVE"] = "Low Voltage Electricity"
        self._dict["HVH"] = "High Vapor Heat (temperature around 90°C)"
        self._dict["MVH"] = "Medium Vapor Heat"
        self._dict["LVH"] = "Low Vapor Heat"
        self._dict["NG"] = "Natural Gas"
        self._dict["H2"] = "Hydrogen"

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def add(self, key, description=''):  # allows to add manually an energy type
        self._dict[key] = description

    def purge_unused(self, used_natures):  # remove unused keys
        # as we can't remove keys in a dictionary we are reading, we have to create a secondary dictionary, which will
        # be read without modification
        keys_to_remove = list()
        for key in self._dict:
            if key not in used_natures:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            self._dict.pop(key)

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def keys(self):  # a shortcut allowing to get a list of energy types faster
        return self._dict.keys()
