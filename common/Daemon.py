from common.Catalog import Catalog


class Daemon:

    def __init__(self, name, period=0):

        if name is None:
            raise DaemonException("Daemon needs a name")

        self._name = name
        self._catalog = None  # catalog from which data is extracted
        # linked to the catalog of a world later
        self._period = period  # period between 2 activations

        self._next_time = 0  # next time step for activation

# ##########################################################################################
# Activation
# ##########################################################################################

    def launch(self, time):  # modify the catalog at the given period
        if time == 0:
            self.init()

        if time >= self._next_time:  # data is saved only if the current time is a multiple of the period
            self.process()
            self._next_time += self._period

    def init(self):
        pass

    def process(self):
        pass

# ##########################################################################################
# Utilities
# ##########################################################################################

    @property
    def catalog(self):  # shortcut for read-only
        return self._catalog

    @property
    def name(self):  # shortcut for read-only
        return self._name


# Exception
class DaemonException(Exception):
    def __init__(self, message):
        super().__init__(message)

