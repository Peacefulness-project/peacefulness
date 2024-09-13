# this class is a price manager updating regularly the prices.
from lib.Subclasses.Daemon.DataReadingDaemon.DataReadingDaemon import DataReadingDaemon


class PriceManagerRTPDaemon(DataReadingDaemon):

    def __init__(self, name, parameters, filename="lib/Subclasses/Daemon/PriceManagerRTPDaemon/ProfilesRTP.json"):
        super().__init__(name, 1, parameters, filename)

        self._managed_keys = [("prices", f"{self.name}.buying_price", "intensive"),
                              ("prices", f"{self.name}.selling_price", "intensive"),
                              ]
        self._buying_coefficient = parameters["buying_coefficient"]
        self._selling_coefficient = parameters["selling_coefficient"]

        self._initialize_managed_keys()

    def _data_update(self, time_step_length: int, offset_bis: int):
        values_dict = super()._data_update(time_step_length, offset_bis)
        values_dict[f"{self.name}.buying_price"] *= self._buying_coefficient
        values_dict[f"{self.name}.selling_price"] *= self._selling_coefficient

        return values_dict







