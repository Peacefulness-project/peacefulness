# This sheet describes a supervisor always refusing to trade with other
# It can correspond to the supervisor of an island, for example
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary

from math import inf


class AutarkyRevenues(Supervisor):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        energy_difference = 0  # this energy is the difference between the energy consumed and produced locally

        # getting back the needs for every device --> standard probably
        for device_name in cluster.devices:
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]  # maximal quantity of energy wanted by the device
            price = 5

            if Emax == 0:  # if the device is inactive
                break  # we do nothing and we go to the other device

            energy_difference += Emax  # incrementing the total
            cluster.quantities[device_name] = [Emax, price, 0, 0]  # the local quantities are updated in the cluster dedicated dictionary

        for subcluster in cluster.subclusters:
            managed_cluster_quantities = self._catalog.get(f"{subcluster.name}.quantities_asked")  # couples prices/quantities asked by the managed clusters
            i = 0  # an arbitrary number given to couples price/quantities
            for element in managed_cluster_quantities:
                energy_difference += element[0]
                cluster.quantities[f"{subcluster.name}_lot_{i}"] = [element[0], element[1], 0, 0]
                i += 1

        quantities_and_prices = [[0, 0]]  # always refuses to exchange with the exterior.

        # todo: faire ca proprement
        for element in quantities_and_prices:
            element[0] = min(element[0] * cluster.efficiency, cluster.capacity)
            element[1] = element[1] / cluster.efficiency

        self._catalog.set(f"{cluster.name}.quantities_asked", quantities_and_prices)  # publish its needs

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced

        grid_price = self._catalog.get(f"{cluster.nature.name}.grid_selling_price")  # the price at which the grid sells energy

        # quantities concerning devices
        for device_name in cluster.devices:
            energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
            # energy_nominal = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_nominal"]  # the nominal quantity of energy asked
            energy_maximum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]  # the maximum quantity of energy asked
            # price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]  # the price of the energy asked

            # self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

            # balances
            if energy_maximum > 0:  # the device wants to consume energy
                minimum_energy_consumed += energy_minimum
                maximum_energy_consumed += energy_maximum

                # money_earned_inside += energy * price  # money earned by selling energy to the device
                # energy_sold_inside += energy  # the absolute value of energy sold inside
            elif energy_maximum < 0:  # the devices wants to sell energy
                minimum_energy_produced -= energy_minimum
                maximum_energy_produced -= energy_maximum

                # money_spent_inside -= energy * price  # money spent by buying energy from the device
                # energy_bought_inside -= energy  # the absolute value of energy bought inside

        # quantities concerning subclusters
        for subcluster in cluster.subclusters:  # quantities concerning clusters
            quantities_and_prices = self._catalog.get(f"{subcluster.name}.quantities_asked")
            # self._catalog.set(f"{subcluster.name}.quantities_given", quantities_and_prices)

            # balances
            for couple in quantities_and_prices:  # for each couple energy/price

                if abs(couple[1]) == +inf:  # if the quantity is absolutely necessary
                    if couple[0] > 0:  # energy bought
                        minimum_energy_consumed += couple[0]
                        maximum_energy_consumed += couple[0]

                        max_price = grid_price + abs(grid_price) / 2  # maximum price the cluster is allowed to bill
                        couple[1] = min(couple[1], max_price)  # maximum price is artificially limited
                    elif couple[0] < 0:  # energy sold
                        minimum_energy_produced -= couple[0]
                        maximum_energy_produced -= couple[0]

                        min_price = grid_price - abs(grid_price) / 2  # minimum price the cluster is allowed to bill
                        couple[1] = max(couple[1], min_price)  # minimum price is artificially limited

                else:  # if the quantity is not necessary
                    if couple[0] > 0:  # energy bought
                        maximum_energy_consumed += couple[0]

                    elif couple[0] < 0:  # energy sold
                        maximum_energy_produced -= couple[0]

        # ##########################################################################################

        # distribution of energy

        if maximum_energy_produced <= minimum_energy_consumed or maximum_energy_consumed <= minimum_energy_produced:  # if there is no possibility to balance the grid
            # we consider that the gird falls
            # updates the balances
            self._catalog.set(f"{cluster.name}.energy_bought", {"inside": 0, "outside": 0})
            self._catalog.set(f"{cluster.name}.energy_sold", {"inside": 0, "outside": 0})

            self._catalog.set(f"{cluster.name}.money_spent", {"inside": 0, "outside": 0})
            self._catalog.set(f"{cluster.name}.money_earned", {"inside": 0, "outside": 0})

        else:  # if there is some possibility to balance the grid
            # here we choose to serve at maximum devices
            [sorted_demands, sorted_offers] = self._revenues_sort(cluster)  # sort the quantities by decreasing emergency

            if maximum_energy_consumed >= maximum_energy_produced:  # if there is not enough production to satisfy all the consumption

                # first, we ensure that the minimum is served to everybody and that all the energy is produced
                for device_name in cluster.devices:  # for devices quantities
                    energy_wanted = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")
                    Emin = energy_wanted["energy_minimum"]  # the minimum of energy, which has to be served
                    energy = energy_wanted["energy_maximum"]  # the maximum of energy, which has to be accepted if it is production
                    price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

                    if energy < 0:  # if the energy is produced, it is automatically accepted
                        self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                        money_spent_inside -= energy * price  # money spent by buying energy from the device
                        energy_bought_inside -= energy  # the absolute value of energy bought inside
                    elif energy > 0:  # else it is a consumption and only the minimum is guaranteed
                        self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emin, "price": price})

                        money_earned_inside += Emin * price  # money earned by selling energy to the device
                        energy_sold_inside += Emin  # the absolute value of energy sold inside

                max_price = grid_price + abs(grid_price) / 2  # maximum price the cluster is allowed to bill
                for subcluster in cluster.subclusters:  # for subclusters quantities
                    quantities_and_prices = self._catalog.get(f"{subcluster.name}.quantities_asked")

                    for couple in quantities_and_prices:  # for each couple energy/price
                        if couple[0] < 0:  # if the quantity is produced
                            quantities_given = self._catalog.get(f"{subcluster.name}.quantities_given")
                            quantities_given.append(couple)
                            self._catalog.set(f"{subcluster.name}.quantities_given", quantities_given)  # then it is served

                            money_spent_inside -= couple[0] * couple[1]  # money spent by buying energy from the subcluster
                            energy_bought_inside -= couple[0]  # the absolute value of energy bought inside

                        elif abs(couple[1]) == max_price:  # if the quantity is absolutely necessary
                            quantities_given = self._catalog.get(f"{subcluster.name}.quantities_given")
                            quantities_given.append(couple)
                            self._catalog.set(f"{subcluster.name}.quantities_given", quantities_given)  # then it is served

                            money_earned_inside += couple[0] * couple[1]  # money earned by selling energy to the subcluster
                            energy_sold_inside += couple[0]  # the absolute value of energy sold inside

                for element in sorted_demands:  # we subtract the minimum guaranteed to the needs
                    try:  # if it is a device
                        energy_wanted = self._catalog.get(f"{element[3]}.{cluster.nature.name}.energy_wanted")
                        Emin = energy_wanted["energy_minimum"]  # the minimum of energy, which has to be served

                        element[1] -= Emin  # we subtract Emin, which is served automatically
                    except:
                        pass

                # then, we distribute the rest of energy available
                energy_available = maximum_energy_produced - minimum_energy_consumed  # the energy available once the min has been served

                i = 0
                while energy_available > sorted_demands[i][1]:  # as long as there is energy available
                    device_name = sorted_demands[i][3]
                    energy = sorted_demands[i][1]  # the quantity of energy needed
                    price = sorted_demands[i][2]  # the price of energy

                    try:  # if it is a subcluster
                        quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                        quantities_given.append([energy, price])
                        self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served
                        energy_available -= energy

                        money_earned_inside += energy * price  # money earned by selling energy to the subcluster
                        energy_sold_inside += energy  # the absolute value of energy sold inside
                    except:  # if it is a device
                        self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})
                        energy_available -= energy  # the difference between the max and the min is consumed

                        money_earned_inside += energy * price  # money earned by selling energy to the device
                        energy_sold_inside += energy  # the absolute value of energy sold inside

                    i += 1
                    # TODO: corriger ça en reprenant la structure --> pas de disjonction ici normalement

                # le problème c'est qu'il faut faire une disjonction des cas entre devices et clusters
                # ce qui est chiant parce tout l'intérêt du sort, c'était de les grouper

                # this line gives the remnant of energy to the last unserved device
                device_name = sorted_demands[i][3]
                price = sorted_demands[i][2]  # the price of energy

                try:
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                    quantities_given.append([energy_available, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served

                    money_earned_inside += energy_available * price  # money earned by selling energy to the subcluster
                    energy_sold_inside += energy_available  # the absolute value of energy sold inside

                    energy_available = 0
                except:
                    price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy_available, "price": price})

                    money_earned_inside += energy_available * price  # money earned by selling energy to the device
                    energy_sold_inside += energy_available  # the absolute value of energy sold inside

                    energy_available = 0

        # ##########################################################################################
            else:  # if there is not enough consumption to absorb all the demand

                # first, we ensure that the minimum is served to everybody and that all the energy is consumed
                for device_name in cluster.devices:  # for devices quantities
                    energy_wanted = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")
                    Emin = energy_wanted["energy_minimum"]  # the minimum of energy, which has to be served
                    energy = energy_wanted["energy_maximum"]  # the maximum of energy, which has to be accepted if it is production
                    price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

                    if energy > 0:  # if the energy is consumed, it is automatically accepted
                        self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                        money_earned_inside += energy * price  # money earned by selling energy to the device
                        energy_sold_inside += energy  # the absolute value of energy sold inside
                    elif energy < 0:  # else it is a production and only the minimum is guaranteed
                        self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emin, "price": price})

                        money_spent_inside -= Emin * price  # money spent by buying energy from the device
                        energy_bought_inside -= Emin  # the absolute value of energy bought inside

                min_price = grid_price - abs(grid_price) / 2  # minimum price the cluster is allowed to bill
                for subcluster in cluster.subclusters:  # for subclusters quantities
                    quantities_and_prices = self._catalog.get(f"{subcluster.name}.quantities_asked")

                    for couple in quantities_and_prices:  # for each couple energy/price
                        if couple[0] > 0:  # if the quantity is consumed
                            quantities_given = self._catalog.get(f"{subcluster.name}.quantities_given")
                            quantities_given.append(couple)
                            self._catalog.set(f"{subcluster.name}.quantities_given", quantities_given)  # then it is served

                            money_earned_inside += couple[0] * couple[1]  # money earned by selling energy to the subcluster
                            energy_sold_inside += couple[0]  # the absolute value of energy sold inside

                        elif abs(couple[1]) == min_price:  # if the quantity is absolutely necessary
                            quantities_given = self._catalog.get(f"{subcluster.name}.quantities_given")
                            quantities_given.append(couple)
                            self._catalog.set(f"{subcluster.name}.quantities_given", quantities_given)  # then it is served

                            money_spent_inside -= couple[0] * couple[1]  # money spent by buying energy from the subcluster
                            energy_bought_inside -= couple[0]  # the absolute value of energy bought inside

                for element in sorted_offers:  # we subtract the minimum guaranteed to the needs
                    try:  # if it is a device
                        energy_wanted = self._catalog.get(f"{element[3]}.{cluster.nature.name}.energy_wanted")
                        Emin = energy_wanted["energy_minimum"]  # the minimum of energy, which has to be served

                        element[1] -= Emin  # we subtract Emin, which is served automatically
                    except:
                        pass

                # then, we distribute the rest of energy available
                energy_available = maximum_energy_consumed - minimum_energy_produced  # the energy available once the min has been served

                i = 0
                while energy_available > - sorted_offers[i][1]:  # as long as there is energy available
                    device_name = sorted_offers[i][3]
                    energy = - sorted_offers[i][1]  # the quantity of energy needed
                    price = sorted_offers[i][2]  # the price of energy

                    try:  # if it is a subcluster
                        quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                        quantities_given.append([-energy, price])
                        self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served
                        energy_available -= energy

                        money_spent_inside += energy * price  # money spent by buying energy from the subcluster
                        energy_bought_inside += energy  # the absolute value of energy bought inside
                    except:  # if it is a device

                        self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": -energy, "price": price})
                        energy_available -= energy  # the difference between the max and the min is consumed

                        money_spent_inside += energy * price  # money spent by buying energy from the device
                        energy_bought_inside += energy  # the absolute value of energy bought inside

                    # TODO: corriger ça en reprenant la structure --> pas de disjonction ici normalement

                    i += 1

                # le problème c'est qu'il faut faire une disjonction des cas entre devices et clusters
                # ce qui est chiant parce tout l'intérêt du sort, c'était de les grouper

                # this line gives the remnant of energy to the last unserved device
                device_name = sorted_offers[i][3]
                price = sorted_offers[i][2]  # the price of energy

                try:
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                    quantities_given.append([-energy_available, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served

                    money_spent_inside += energy_available * price  # money spent by buying energy from the subcluster
                    energy_bought_inside += energy_available  # the absolute value of energy bought inside

                    energy_available = 0
                except:
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": -energy_available, "price": price})

                    money_spent_inside += energy_available * price  # money spent by buying energy from the device
                    energy_bought_inside += energy_available  # the absolute value of energy bought inside

                    energy_available = 0  # the difference between the max and the min is consumed

        # print(f"bought outside {0}; sold outside {0}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")
        print(energy_bought_inside - energy_sold_inside)

        # ##########################################################################################

        # updates the balances
        self._catalog.set(f"{cluster.name}.energy_bought", {"inside": energy_bought_inside, "outside": 0})
        self._catalog.set(f"{cluster.name}.energy_sold", {"inside": energy_sold_inside, "outside": 0})

        self._catalog.set(f"{cluster.name}.money_spent", {"inside": money_spent_inside, "outside": 0})
        self._catalog.set(f"{cluster.name}.money_earned", {"inside": money_earned_inside, "outside": 0})


user_classes_dictionary[f"{AutarkyRevenues.__name__}"] = AutarkyRevenues



