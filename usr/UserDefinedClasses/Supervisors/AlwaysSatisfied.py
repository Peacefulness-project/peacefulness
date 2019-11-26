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
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]  # maximal quantity of energy wanted by the device

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
        print(cluster.name)
        # preparing balances
        quantities_asked = {"bought": 0, "sold": 0}
        quantities_given = {"bought": 0, "sold": 0}

        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        # counting the offers and the demands at its own level
        # what was asked
        for couple in self._catalog.get(f"{cluster.name}.{cluster.nature.name}.quantities_asked"):
            if couple[0] > 0:  # energy the aggregator wanted to buy
                quantities_asked["bought"] += couple[0]  # the quantity of energy asked the cluster wanted to buy
            elif couple[0] < 0:  # energy the aggregator wanted to sell
                quantities_asked["sold"] += couple[0]  # the quantity of energy asked the cluster wanted to sell

        # what is given
        for couple in self._catalog.get(f"{cluster.name}.{cluster.nature.name}.quantities_given"):
            if couple[0] > 0:  # energy bought by the aggregator
                quantities_given["bought"] += couple[0]  # the quantity of energy sold to the cluster

                # making balances
                # energy bought
                energy_bought_outside += quantities_given["bought"]  # the absolute value of energy bought outside
                money_spent_outside += quantities_given["bought"] * couple[1]  # the absolute value of money spent outside

            elif couple[0] < 0:  # energy sold by the aggregator
                quantities_given["sold"] += couple[0]  # the quantity of energy bought by the cluster

                # making balances
                # energy sold
                energy_sold_outside -= quantities_given["sold"]  # the absolute value of energy sold outside
                money_earned_outside -= quantities_given["sold"] * couple[1]  # the absolute value of money earned outside

        # energy distribution and billing
        print(f"given catalog:{self._catalog.get(f'{cluster.name}.{cluster.nature.name}.quantities_given')} local:{quantities_given}")
        print(f"asked catalog:{self._catalog.get(f'{cluster.name}.{cluster.nature.name}.quantities_asked')} local:{quantities_asked}")
        if quantities_given == quantities_asked:  # if the cluster got what it wanted

            # quantities concerning devices
            for device_name in cluster.devices:
                energy = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]  # the maximum quantity of energy asked
                price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]  # the price of the energy asked

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                # balances
                if energy > 0:  # energy bought
                    price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]
                    money_earned_inside += energy * price  # money earned by selling energy to the device
                    energy_sold_inside += energy  # the absolute value of energy sold inside
                elif energy < 0:  # energy sold
                    price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]
                    money_spent_inside -= energy * price  # money spent by buying energy from the device
                    energy_bought_inside -= energy  # the absolute value of energy bought inside

            # quantities concerning subclusters
            for subcluster in cluster.subclusters:  # quantities concerning clusters
                quantities_and_prices = self._catalog.get(f"{subcluster.name}.{cluster.nature.name}.quantities_asked")
                self._catalog.set(f"{subcluster.name}.{cluster.nature.name}.quantities_given", quantities_and_prices)

                # balances
                for couple in quantities_and_prices:  # for each couple energy/price
                    if couple[0] > 0:  # energy bought
                        grid_price = self._catalog.get(f"{cluster.nature.name}.grid_selling_price")  # the price at which the grid sells energy
                        max_price = grid_price + abs(grid_price)/2  # maximum price the cluster is allowed to bill
                        couple[1] = min(couple[1], max_price)  # maximum price is artificially limited
                        money_earned_inside += couple[0] * couple[1]  # money earned by selling energy to the subcluster
                        energy_sold_inside += couple[0]  # the absolute value of energy sold inside
                    elif couple[0] < 0:  # energy sold
                        grid_price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")  # the price at which the grid buys energy
                        min_price = grid_price - abs(grid_price)/2  # minimum price the cluster is allowed to bill
                        couple[1] = max(couple[1], min_price)  # minimum price is artificially limited
                        money_spent_inside -= couple[0] * couple[1]  # money spent by buying energy from the subcluster
                        energy_bought_inside -= couple[0]  # the absolute value of energy bought inside
        else:
            # as we suppose that there is always a grid able to buy/sell an infinite quantity of energy, we souldn't be in this case
            pass
            # raise SupervisorException("An always satisfied supervision supposes the access to an infinite provider/consumer")

        print(f"from outside  money earned:{money_earned_outside}/spent:{money_spent_outside}, energy bought:{energy_bought_outside}/sold:{energy_sold_outside}")
        print(f"from inside  money earned:{money_earned_inside}/spent:{money_spent_inside},  energy bought:{energy_bought_inside}/sold:{energy_sold_inside}")
        print(f"sum          money:{money_earned_outside - money_spent_outside + money_earned_inside - money_spent_inside},"
              f" energy:{energy_bought_outside - energy_sold_outside + energy_bought_inside - energy_sold_inside}")
        print("\n")

        # updates the balances
        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.energy_bought", {"inside": energy_bought_inside, "outside": energy_bought_outside})
        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.energy_sold", {"inside": energy_sold_inside, "outside": energy_sold_outside})

        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.money_spent", {"inside": money_spent_inside, "outside": money_spent_outside})
        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.money_earned", {"inside": money_earned_inside, "outside": money_earned_outside})


user_classes_dictionary[f"{AlwaysSatisfied.__name__}"] = AlwaysSatisfied




