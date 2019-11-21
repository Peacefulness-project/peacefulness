# This sheet describes a supervisor always refusing to trade with other
# It can correspond to the supervisor of an island, for example
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary


class Autarky(Supervisor):

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

    def dummy_function(self, cluster, quantities_given, quantities_asked, sorted_demands, sorted_offers):
        # then we distribute all the energy
        # for this, it is needed to know if the cluster asks for or proposes energy to sell
        energy_available = abs(quantities_given)
        argent_achat = 0  # money earned/spent by buying/selling local quantities of energy

        if quantities_asked - quantities_given > 0:  # if the cluster asks for energy
            limiting_quantities = sorted_demands
        elif quantities_asked - quantities_given < 0:  # if the cluster proposes energy
            limiting_quantities = sorted_offers
        # if quantities asked = quantities given, then the cluster is balanced and there is no need to go further

        for quantity in cluster.quantities.values():
            if quantity[0] < 0:  # if the device or the cluster wants to sell energy
                quantity[2] = quantity[0]  # the need is satisfied
                energy_available += abs(quantity)  # this quantity is available to be redistributed later
                # TODO: s'occuper de l'argent
        i = 0
        while energy_available > limiting_quantities[i][0] and i < len(limiting_quantities) - 1:  # as long as the consumption is urgent and there is energy available
            device_name = limiting_quantities[i][2]
            cluster.quantities[device_name][2] = cluster.quantities[device_name][0]  # the device is satisfied
            # TODO: s'occuper de l'argent
            i += 1

        # this line gives the remnant of energy to the last unserved device
        try:
            device_name = limiting_quantities[i][2]
            cluster.quantities[device_name][2] = energy_available
        except:
            pass


user_classes_dictionary[f"{Autarky.__name__}"] = Autarky



