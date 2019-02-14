from common.Catalog import Catalog

class Deamon:

    def __init__(self, name, period=0):

        if name is None:
            raise DeamonException("Il faut un nom au démon")

        self._name = name
        self._catalog = None
        self._period = period

        self._next_time = 0

    @property
    def catalog(self):
        return self._catalog

    @property
    def name(self):
        return self._name

    def launch(self, time):  # write data at the given frequency
        if time == 0:
            self.init();

        if time >= self._next_time:  # data is saved only if the current time is a
            self.process()
            self._next_time += self._period

    def init(self):
        pass

    def process(self):
        pass



    def set_catalog(self, catalog):
        self._catalog = catalog


# Exception
class DeamonException(Exception):
    def __init__(self, message):
        super().__init__(message)

