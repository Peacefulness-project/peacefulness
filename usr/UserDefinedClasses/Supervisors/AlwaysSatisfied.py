# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign

from math import inf


class AlwaysSatisfied(Supervisor):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        # quantities_and_prices = list()  # this list collects all the quantities inside the cluster, both consumptions and productions

        energy_difference = 0  # this energy is the difference between the energy consumed and produced locally

        # getting back the needs for every device --> standard probably
        for device_name in cluster.devices:
            Pmax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted_maximum")

            if Pmax == 0:  # if the device is inactive
                break  # we do nothing and we go to the other device

            energy_difference += Pmax  # incrementing the total

        for managed_cluster in cluster.subclusters:
            turlututu = self._catalog.get(f"{managed_cluster.name}.{managed_cluster.nature.name}.quantities_asked")  # couples prices/quantities asked by the managed clusters
            for element in turlututu:
                energy_difference += element[0]

        quantities_and_prices = [[energy_difference, sign(energy_difference)*inf]]  # wants to satisfy everyone, regardless the price (i.e sells even at -inf and buys even at +inf)

        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.quantities_asked", quantities_and_prices)

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster distributes the energy among its devices and clusters
        quantities_asked = 0
        quantities_given = 0

        for element in self._catalog.get(f"{cluster.name}.{cluster.nature.name}.quantities_asked"):
            quantities_asked += element[0]  # the quantity of energy asked
        for element in self._catalog.get(f"{cluster.name}.{cluster.nature.name}.quantities_given"):
            quantities_given += element[0]  # the quantity of energy given

        if quantities_given == quantities_asked:  # if each device got what it wanted
            for device_name in cluster.devices:
                energy = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted_maximum")
                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", energy)

            for managed_cluster in cluster.subclusters:
                 quantities_and_prices = self._catalog.get(f"{managed_cluster.name}.{cluster.nature.name}.quantities_asked")
                 self._catalog.set(f"{managed_cluster.name}.{cluster.nature.name}.quantities_given", quantities_and_prices)

        else:
            for device in cluster.devices:  # if there is missing energy
                pass


user_classes_dictionary[f"{AlwaysSatisfied.__name__}"] = AlwaysSatisfied

