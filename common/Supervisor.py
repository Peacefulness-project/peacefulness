# This sheet describes the supervisor
# It contains only the name of a file serving as a "main" for the supervisor and a description


class Supervisor:

    def __init__(self, name, filename, description):
        self._name = name  # the name of the supervisor  in the catalog
        self._filename = filename  # the name of the file, who must be in usr.supervisors
        self.description = description  # a description of the objective/choice/process of the supervisor

        self._catalog = None  # the catalog in which some data are stored

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def distribute_local_energy(self):  # before communicating with the exterior, the cluster makes its local balances
        pass

    def publish_needs(self):  # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        pass

    def distribute_remote_energy(self):  #
        pass

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def filename(self):  # shortcut for read-only
        return self._filename

