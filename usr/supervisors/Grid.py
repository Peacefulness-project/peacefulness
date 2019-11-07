# This sheet describes a supervisor of a TSO
# It represents the higher level of energy management. Here, it is a black box: it both proposes and accepts unlimited amounts of energy
from common.Supervisor import Supervisor


class Grid(Supervisor):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def distribute_local_energy(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        pass

    def publish_needs(self, cluster):  # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        pass

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        pass

