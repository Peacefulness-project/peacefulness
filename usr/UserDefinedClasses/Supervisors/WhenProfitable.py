# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary


class WhenProfitable(Supervisor):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)

        energy_difference = 0  # this energy is the difference between the energy consumed and produced locally

        # getting back the needs for every device --> standard probably
        for device_name in cluster.devices:
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted_maximum")
            price = 5

            if Emax == 0:  # if the device is inactive
                break  # we do nothing and we go to the other device

            energy_difference += Emax  # incrementing the total
            cluster.quantities[device_name] = [Emax, price, 0, 0]  # the local quantities are updated in the cluster dedicated dictionary

        for managed_cluster in cluster.subclusters:
            managed_cluster_quantities = self._catalog.get(f"{managed_cluster.name}.{managed_cluster.nature.name}.quantities_asked")  # couples prices/quantities asked by the managed clusters
            i = 0  # an arbitrary number given to couples price/quantities
            for element in managed_cluster_quantities:
                energy_difference += element[0]
                cluster.quantities[f"{managed_cluster.name}_lot_{i}"] = [element[0], element[1], 0, 0]
                i += 1

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        pass


user_classes_dictionary[f"{WhenProfitable.__name__}"] = WhenProfitable

