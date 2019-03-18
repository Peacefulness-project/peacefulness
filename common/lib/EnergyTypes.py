# List of energy
# This class is just a dictionary containing the different nature of energy
# A representative of this class is created for each world


class NatureList:  # this class contains the different natures

    def __init__(self):
        self._dict = dict()  # a dictionary indexing all types of nature
        self._dict["LVE"] = "Low Voltage Electricity"
        self._dict["HVH"] = "High Vapor Heat (temperature around 90°C)"
        self._dict["MVH"] = "Medium Vapor Heat"
        self._dict["LVH"] = "Low Vapor Heat"
        self._dict["NG"] = "Natural Gas"
        self._dict["H2"] = "Hydrogen"

        self._catalog = None

    def add(self, key, description=''):  # allows to add manually an energy type
        self._dict[key] = description

    @property
    def keys(self):  # a shortcut allowing to get a list of energy types faster
        return self._dict.keys()
