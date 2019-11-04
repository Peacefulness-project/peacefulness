# the exchange leader is the object who resolves the "exchanges between clusters" phase.


class ExchangeLeader:

    def __init__(self):
        self.clusters = dict()  # this dict contains all the clusters which do not obey to any other cluster
        self._catalog = None

        self.exchanges = dict()  # a dict containing all the independent clusters and their possibility of exchanging with other clusters
        # each link with another cluster is unidirectional, and defines an efficiency and a capacity

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def organise_exchanges(self):  # makes the match between the different quantities cluster would like to exchange
        pass


