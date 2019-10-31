# the exchange leader is the object who resolves the "exchanges between clusters" phase.


class ExchangeLeader:

    def __init__(self):
        self.clusters = dict()  # this dict contains all the clusters which do not obey to any other cluster
        self._catalog = None

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def organise_exchanges(self):  # makes the match between the different quantities cluster would like to exchange
        pass


