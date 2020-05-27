# this class serves as the mother for all demons managing prices of contracts.
# it fixes a price once and for all
from json import load
from src.common.Daemon import Daemon


class PriceManagerRTPDaemon(Daemon):

    def __init__(self, name, parameters):
        self._location = parameters["location"]  # the location corresponding to the data

        super().__init__(name, 1, parameters)

        # getting the data for the chosen location
        if "datafile" in parameters:  # if the user has chosen another datafile
            file = open(parameters["datafile"], "r")
        else:
            file = open("lib/Subclasses/Daemon/PriceManagerRTPDaemon/ProfilesRTP.json", "r")
        data = load(file)[parameters["location"]]
        file.close()

        self._format = data["format"]
        self._prices = data["prices"]

        # getting back the appropriate way of reading the data
        self._files_formats = {"1day/year": self._get_price_1_day_per_year}  # 1 representative day, hour by hour, for each month
        self._get_price = self._files_formats[self._format]

        self._catalog.add(f"{self.name}.buying_price", self._get_price())  # the buying price for energy is set
        self._catalog.add(f"{self.name}.selling_price", self._get_price())  # the selling price for energy is set

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self.name}.buying_price", self._get_price())
        self._catalog.set(f"{self.name}.selling_price", self._get_price())

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def _get_price_1_day_per_year(self):
        hour = (self._catalog.get("physical_time").hour+1) % 24
        return self._prices[hour]





