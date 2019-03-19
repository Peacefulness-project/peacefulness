# Daemons are objects designed to update entries in the catalog who are not devices
# Just like devices, there is a general class Daemon and it is the user who has to define its own daemons
from common.Catalog import Catalog


class Daemon:

    def __init__(self, name, period=0):

        if name is None:
            raise DaemonException("Daemon needs a name")

        self._name = name
        self._catalog = None  # catalog from which data is extracted
        # linked to the catalog of a world later

        # Daemons are not obliged to act each turn. A period of activation can be defined.
        self._period = period  # period between 2 activations

        self._next_time = 0  # next iteration at which the daemon will be activated

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def add_catalog(self, catalog):  # add a catalog
        self._catalog = catalog

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def launch(self):  # modify the catalog at the given period

        current_time = self._catalog.get("simulation_time")  # the simulation time allows to know if it has
        # to be called or not

        if current_time == 0:
            self.init()

        if current_time >= self._next_time:  # data is saved only if the current time is a multiple of the period
            self.process()
            self._next_time += self._period

    def init(self):  # where are defined specific entries in the catalog
        pass

    def process(self):  # where the catalog entries are modified
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

