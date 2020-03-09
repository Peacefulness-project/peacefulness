# Daemon are objects designed to update entries in the catalog who are not devices
# Just like devices, there is a general class Daemon and it is the user who has to define its own daemons


class Daemon:

    def __init__(self, world, name, period=0, parameters=None):
        if name is None:
            raise DaemonException("Daemon needs a name")

        self._name = name

        self._period = period  # number of rounds between 2 activations

        self._next_time = 0  # next iteration at which the daemon will be activated

        self._catalog = world.catalog  # catalog from which data is extracted

        world.register_daemon(self)  # register this daemon into world dedicated dictionary

        # parameters is the list of different parameters necessary for user-defined daemons subclasses
        # putting them into a list is necessary for the save/load system
        if parameters:
            self._parameters = parameters
        else:
            self._parameters = {}

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def launch(self):  # modify the catalog at the given period
        current_time = self._catalog.get("simulation_time")  # the simulation time allows to know if it has to be called or not

        if current_time >= self._next_time:  # data is saved only if the current time is a multiple of the period
            self._process()
            self._next_time += self._period

    def _process(self):  # where specific tasks are defined
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

