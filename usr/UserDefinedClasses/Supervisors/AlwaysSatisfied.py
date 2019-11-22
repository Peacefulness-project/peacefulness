# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign
from common.Supervisor import SupervisorException

from math import inf


class AlwaysSatisfied(Supervisor):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        energy_difference = 0  # this energy is the difference between the energy consumed and produced locally

        # getting back the needs for every device --> standard probably
        for device_name in cluster.devices:
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[0][2]  # maximal quantity of energy wanted by the device

            if Emax == 0:  # if the device is inactive
                break  # we do nothing and we go to the other device

            energy_difference += Emax  # incrementing the total
            cluster.quantities[device_name] = [Emax, sign(Emax) * inf, 0, 0]  # the local quantities are updated in the cluster dedicated dictionary

        for managed_cluster in cluster.subclusters:
            managed_cluster_quantities = self._catalog.get(f"{managed_cluster.name}.{managed_cluster.nature.name}.quantities_asked")  # couples prices/quantities asked by the managed clusters
            i = 0  # an arbitrary number given to couples price/quantities
            for element in managed_cluster_quantities:
                energy_difference += element[0]
                cluster.quantities[f"{managed_cluster.name}_lot_{i}"] = [element[0], element[1], 0, 0]
                i += 1

        quantities_and_prices = [[energy_difference, sign(energy_difference)*inf]]  # wants to satisfy everyone, regardless the price (i.e sells even at -inf and buys even at +inf)

        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.quantities_asked", quantities_and_prices)

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster distributes the energy among its devices and clusters
        quantities_asked = 0
        quantities_given = 0

        energy_bought_outside = 0
        energy_sold_outside = 0
        energy_bought_inside = 0
        energy_sold_inside = 0


        # self._catalog.add(f"{self.name}.{self.nature.name}.energy_bought", 0)  # accounts for the energy bought by the cluster during the round
        # self._catalog.add(f"{self.name}.{self.nature.name}.energy_sold", 0)  # accounts for the energy sold by the cluster during the round

        money_earned_outside = 0
        money_spent_outside = 0
        money_earned_inside = 0
        money_spent_inside = 0

        for element in self._catalog.get(f"{cluster.name}.{cluster.nature.name}.quantities_asked"):
            quantities_asked += element[0]  # the quantity of energy asked

            # making balances
            energy_bought_outside += quantities_asked
            price = max(element[1], 1)  # TODO: il faut trouver un truc pour éviter les prix inf
            # normalement, prix donne par etage du dessus
            money_spent_outside += - quantities_asked * price

        for element in self._catalog.get(f"{cluster.name}.{cluster.nature.name}.quantities_given"):
            quantities_given += element[0]  # the quantity of energy given

            # making balances
            energy_sold_outside += quantities_given
            price = min(element[0], 1)  # TODO: il faut trouver un truc pour éviter les prix inf
            # normalement, prix donne par etage du dessus
            money_earned_outside += quantities_given * price

        if quantities_given == quantities_asked:  # if each device got what it wanted
            for device_name in cluster.devices:  # quantities concerning devices
                energy = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[0][2]  # the maximum quantity of energy asked
                price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[1]  # the price of the energy asked
                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                # balances
                if energy > 0:
                    price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[1]
                    price = min(price, 1)  # TODO: il faut trouver un truc pour éviter les prix inf
                    money_earned_outside += energy * price  # money earned by selling energy to the device
                    energy_sold_inside += energy
                elif energy < 0:
                    price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[1]
                    price = min(price, 1)  # TODO: il faut trouver un truc pour éviter les prix inf
                    money_spent_outside += - energy * price  # money spent by buying energy from the device
                    energy_bought_inside += energy

            for managed_cluster in cluster.subclusters:  # quantities concerning clusters
                quantities_and_prices = self._catalog.get(f"{managed_cluster.name}.{cluster.nature.name}.quantities_asked")
                self._catalog.set(f"{managed_cluster.name}.{cluster.nature.name}.quantities_given", quantities_and_prices)

                # balances
                for couple in quantities_and_prices:  # for each couple energy/price
                    if couple[0] > 0:
                        price = min(42, 1)  # TODO: il faut trouver un truc pour éviter les prix inf
                        money_earned_outside += couple[1] * price  # money earned by selling energy to the device
                        energy_sold_inside += couple[0]
                    else:
                        price = min(42, 1)  # TODO: il faut trouver un truc pour éviter les prix inf
                        money_spent_outside += - couple[1] * price  # money spent by buying energy from the device
                        energy_bought_inside += couple[0]

        else:
            # as we suppose that there is always a grid able to buy/sell an infinite quantity of energy, we souldn't be in this case
            pass
            # raise SupervisorException("An always satisfied supervision supposes the access to an infinite provider/consumer")

        # updates the balances
        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.energy_bought", {"inside": energy_bought_inside, "outside": energy_bought_outside})
        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.energy_sold", {"inside": energy_sold_outside, "outside": energy_sold_inside})

        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.money_spent", {"inside": money_spent_inside, "outside": money_spent_outside})
        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.money_earned", {"inside": money_earned_inside, "outside": money_earned_outside})


user_classes_dictionary[f"{AlwaysSatisfied.__name__}"] = AlwaysSatisfied




