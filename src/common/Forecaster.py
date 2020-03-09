# This class serves to predict quantities both consumed and produced
# It serves as a mother class for all the uer-defined forecasters


class Forecaster:

    def __init__(self, name):
        self._name = name

        self._catalog = None

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):
        self._catalog = catalog

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def fait_quelque_chose(self):
        pass

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name


# Exception
class ForecasterException(Exception):
    def __init__(self, message):
        super().__init__(message)

