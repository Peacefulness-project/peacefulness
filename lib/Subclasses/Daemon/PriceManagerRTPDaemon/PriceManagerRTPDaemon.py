# this class is a price manager updating regularly the prices.
from lib.Subclasses.Daemon.DataReadingDaemon.DataReadingDaemon import DataReadingDaemon


class PriceManagerRTPDaemon(DataReadingDaemon):

    def __init__(self, name, parameters, filename="lib/Subclasses/Daemon/PriceManagerRTPDaemon/ProfilesRTP.json"):
        super().__init__(name, 1, parameters, filename)

        self._managed_keys = [("prices", f"{self.name}.buying_price", "intensive"),
                              ("prices", f"{self.name}.selling_price", "intensive"),
                              ]

        self._initialize_managed_keys()

        # if "coefficient" in parameters:
        #     self._selling_coeff = parameters["coefficient"]
        # else:
        #     self._selling_coeff = 1







