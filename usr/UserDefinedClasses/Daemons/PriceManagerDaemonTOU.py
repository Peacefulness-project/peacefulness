# this daemon is designed to manage the price of a given energy for sellers or buyers

from common.Daemon import Daemon
from tools.UserClassesDictionary import user_classes_dictionary


class PriceManagerDaemonTOU(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)
        self._nature = parameters["nature"]
        self._buying_prices = parameters["buying_prices"]
        self._selling_prices = parameters["selling_prices"]

        self._hours = []
        hours_range = parameters["hours"]
        for hour_range in hours_range:
            for i in range(hour_range[0], hour_range[1]):
                self._hours.append(i)

        self._moment = None  # indicates if the tariff is HP or HC

    def _user_register(self):
        self._moment = (self._catalog.get("physical_time").hour in self._hours) * 1  # 1 = HP, 0 = HC

        self._catalog.add(f"{self._nature}.buying_price_TOU", self._buying_prices[self._moment])
        self._catalog.add(f"{self._nature}.selling_price_TOU", self._selling_prices[self._moment])

    def _process(self):  # make shifts between HP/HC todo: traduire
        self._moment = (self._catalog.get("physical_time").hour in self._hours) * 1  # 1 = HP, 0 = HC

        self._catalog.set(f"{self._nature}.buying_price_TOU", self._buying_prices[self._moment])
        self._catalog.set(f"{self._nature}.selling_price_TOU", self._selling_prices[self._moment])


user_classes_dictionary[f"{PriceManagerDaemonTOU.__name__}"] = PriceManagerDaemonTOU




