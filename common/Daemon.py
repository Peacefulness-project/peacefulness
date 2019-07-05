# Daemons are objects designed to update entries in the catalog who are not devices
# Just like devices, there is a general class Daemon and it is the user who has to define its own daemons
from common.Catalog import Catalog


class Daemon:

    def __init__(self, name, period=0):

        if name is None:
            raise DaemonException("Daemon needs a name")

        self._name = name

        # Daemons are not obliged to act each turn. A period of activation can be defined.
        self._period = period  # period between 2 activations

        self._next_time = 0  # next iteration at which the daemon will be activated

        self._catalog = None  # catalog from which data is extracted
        # linked to the catalog of a world later

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog
        self._user_register()  # create relevant entries in the catalog

    def _user_register(self):  # where are defined user-specific entries in the catalog
        pass

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _launch(self):  # modify the catalog at the given period

        current_time = self._catalog.get("simulation_time")  # the simulation time allows to know if it has
        # to be called or not

        if current_time >= self._next_time:  # data is saved only if the current time is a multiple of the period
            self._process()
            self._next_time += self._period

    def _process(self):  # where the catalog entries are modified
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

