# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor


class AlwaysServed(Supervisor):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def distribute_local_energy(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        pass

    def publish_needs(self, cluster):  # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        pass

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        pass

