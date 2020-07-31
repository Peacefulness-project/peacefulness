# this class serves as the mother for all demons managing prices of contracts.
# it fixes a price once and for all
from json import load
from src.common.Daemon import Daemon
from src.tools.ReadingFonction import get_1_day_per_year

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
        self._files_formats = {"1day/year": get_1_day_per_year}  # 1 representative day, hour by hour, for each month
        self._get_price = self._files_formats[self._format]

        self._catalog.add(f"{self.name}.buying_price", self._get_price(self._prices, self._catalog))  # the buying price for energy is set
        self._catalog.add(f"{self.name}.selling_price", self._get_price(self._prices, self._catalog))  # the selling price for energy is set

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _process(self):
        self._catalog.set(f"{self.name}.buying_price", self._get_price(self._prices, self._catalog))
        self._catalog.set(f"{self.name}.selling_price", self._get_price(self._prices, self._catalog))

    # ##########################################################################################
    # Utilities
    # ##########################################################################################






