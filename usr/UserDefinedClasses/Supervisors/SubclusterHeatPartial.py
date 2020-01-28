# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign

from math import inf


class SubclusterHeatPartial(Supervisor):

    def __init__(self, name, description):
        super().__init__(name, description)

        self._quantities_exchanged_internally = dict()  # this dict contains the quantities exchanged internally

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        min_grid_price = self._catalog.get(
            f"{cluster.nature.name}.grid_selling_price")  # the price at which the grid sells energy
        max_grid_price = self._catalog.get(
            f"{cluster.nature.name}.grid_buying_price")  # the price at which the grid sells energy
        max_price = max_grid_price + abs(max_grid_price) / 2  # maximum price the cluster is allowed to bill
        min_price = min_grid_price - abs(min_grid_price) / 2  # minimum price the cluster is allowed to bill

        # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        energy_difference = 0  # this energy is the difference between the energy consumed and produced locally
        quantities_and_prices = []  # a list containing couples energy/prices

        # getting back the needs for every device --> standard probably
        for device_name in cluster.devices:
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[
                "energy_maximum"]  # maximal quantity of energy wanted by the device
            price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

            if Emax == 0:  # if the device is inactive
                break  # we do nothing and we go to the other device

            cluster.quantities[device_name] = [Emax, price, 0,
                                               0]  # the local quantities are updated in the cluster dedicated dictionary

        for subcluster in cluster.subclusters:
            managed_cluster_quantities = self._catalog.get(
                f"{subcluster.name}.quantities_asked")  # couples prices/quantities asked by the managed clusters
            i = 0  # an arbitrary number given to couples price/quantities
            for element in managed_cluster_quantities:
                cluster.quantities[f"{subcluster.name}_lot_{i}"] = [element[0], element[1], 0, 0]
                i += 1

        # formulation of needs
        [sorted_demands, sorted_offers] = self._price_sort(cluster)  # sort the quantities according to their prices

        # ##########################################################################################
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced

        # quantities concerning devices
        for device_name in cluster.devices:
            energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[
                "energy_minimum"]  # the minimum quantity of energy asked
            # energy_nominal = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_nominal"]  # the nominal quantity of energy asked
            energy_maximum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[
                "energy_maximum"]  # the maximum quantity of energy asked
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

                if abs(couple[1]) >= max_price and couple[0] > 0:  # if the quantity is absolutely necessary
                    minimum_energy_consumed += couple[0]
                    maximum_energy_consumed += couple[0]

                    couple[1] = min(couple[1], max_price)  # maximum price is artificially limited

                elif abs(couple[1]) <= min_price and couple[0] < 0:  # if the quantity is absolutely necessary
                    minimum_energy_produced -= couple[0]
                    maximum_energy_produced -= couple[0]

                    couple[1] = max(couple[1], min_price)  # minimum price is artificially limited

                else:  # if the quantity is not necessary
                    if couple[0] > 0:  # energy bought
                        maximum_energy_consumed += couple[0]

                    elif couple[0] < 0:  # energy sold
                        maximum_energy_produced -= couple[0]

        # first we remove the urgent quantities, already satisfied
        # demand side
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_demands)):  # demands
            if sorted_demands[i][0] == 1:  # if it is urgent
                lines_to_remove.append(i)

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_demands.pop(line_index)

        # offer side
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_offers)):  # offers
            if sorted_offers[i][0] == 1:  # if it is urgent
                lines_to_remove.append(i)

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_offers.pop(line_index)

        if maximum_energy_produced <= minimum_energy_consumed or maximum_energy_consumed <= minimum_energy_produced:  # if there is no possibility to balance the grid without help
            if minimum_energy_consumed > maximum_energy_produced:  # if there is a lack of production
                quantities_and_prices = [[minimum_energy_consumed - maximum_energy_produced,
                                          inf]]  # wants to satisfy everyone, regardless the price (i.e sells even at -inf and buys even at +inf)
            else:  # if there is a lack of consumption
                pass  # this cluster can't sell heat

        # ##########################################################################################
        # exchanges with outside
        energy_difference = 0  # this energy is the difference between the energy consumed and produced locally

        # demand
        for i in range(len(sorted_demands)):  # demands
            energy_difference += sorted_demands[i][1]  # incrementing the total

        # offer
        for i in range(len(sorted_offers)):  # offers
            energy_difference += sorted_offers[i][1]  # incrementing the total

        price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")  # as the cluster can't sell energy

        # publication of these urgent needs
        quantities_and_prices.append([max(energy_difference, 0),
                                      price])  # wants to satisfy everyone, regardless the price (i.e sells even at -inf and buys even at +inf)
        # the cluster heat can't sell energy

        # todo: faire ca proprement
        for element in quantities_and_prices:
            element[0] = min(element[0] / cluster.efficiency, cluster.capacity)
            element[1] = element[1] * cluster.efficiency

        self._catalog.set(f"{cluster.name}.quantities_asked", quantities_and_prices)  # publish its needs

        # quantities_exchanged = min(offer, demand)  # the quantity exchanged internally is the minimum of the current offer and demand
        # self._quantities_exchanged_internally[cluster.name] = [quantities_exchanged, None]  # we store this value for the descendant phase

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        # print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced

        min_grid_price = self._catalog.get(
            f"{cluster.nature.name}.grid_selling_price")  # the price at which the grid sells energy
        max_grid_price = self._catalog.get(
            f"{cluster.nature.name}.grid_buying_price")  # the price at which the grid sells energy
        max_price = max_grid_price + abs(max_grid_price) / 2  # maximum price the cluster is allowed to bill
        min_price = min_grid_price - abs(min_grid_price) / 2  # minimum price the cluster is allowed to bill

        # ##########################################################################################

        # quantities concerning devices
        for device_name in cluster.devices:
            energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[
                "energy_minimum"]  # the minimum quantity of energy asked
            # energy_nominal = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_nominal"]  # the nominal quantity of energy asked
            energy_maximum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[
                "energy_maximum"]  # the maximum quantity of energy asked
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

                if abs(couple[1]) >= max_price and couple[0] > 0:  # if the quantity is absolutely necessary
                    minimum_energy_consumed += couple[0]
                    maximum_energy_consumed += couple[0]

                    couple[1] = min(couple[1], max_price)  # maximum price is artificially limited

                elif abs(couple[1]) <= min_price and couple[0] < 0:  # if the quantity is absolutely necessary
                    minimum_energy_produced -= couple[0]
                    maximum_energy_produced -= couple[0]

                    couple[1] = max(couple[1], min_price)  # minimum price is artificially limited

                else:  # if the quantity is not necessary
                    if couple[0] > 0:  # energy bought
                        maximum_energy_consumed += couple[0]

                    elif couple[0] < 0:  # energy sold
                        maximum_energy_produced -= couple[0]

        # print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")

        # what is given
        for couple in self._catalog.get(f"{cluster.name}.quantities_given"):
            if couple[0] > 0:  # energy bought by the aggregator

                # making balances
                # energy bought
                money_spent_outside += couple[0] * couple[1]  # the absolute value of money spent outside
                energy_bought_outside += couple[0] * cluster.efficiency  # the absolute value of energy bought outside

            elif couple[0] < 0:  # energy sold by the aggregator

                # making balances
                # energy sold
                money_earned_outside -= couple[0] * couple[1]  # the absolute value of money earned outside
                energy_sold_outside -= couple[0] * cluster.efficiency  # the absolute value of energy sold outside

        # formulation of needs
        [sorted_demands, sorted_offers] = self._emergency_sort(cluster)  # sort the quantities according to their prices

        # ##########################################################################################
        # balance of energy available

        energy_available_consumption = energy_bought_outside + maximum_energy_produced  # the total energy available for consumptions
        energy_available_production = maximum_energy_consumed - energy_bought_outside  # the total energy available for productions

        # print(energy_sold_inside)
        # print(maximum_energy_consumed)
        # print(energy_available_consumption)
        # print(energy_available_production)
        # print()

        # first we ensure the urgent quantities will be satisfied
        # demand side
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_demands)):  # demands
            device_name = sorted_demands[i][3]
            energy = sorted_demands[i][1]
            price = sorted_demands[i][2]
            price = min(price, max_price)

            if sorted_demands[i][0] == 1:  # if it is urgent
                lines_to_remove.append(i)

                try:  # if it is a subcluster
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                    couple = [energy, price]
                    quantities_given.append(couple)

                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded",
                                      {"quantity": energy, "price": price})

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

            else:  # if it is a device, it may asks for a min of energy too
                try:
                    energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[
                        "energy_minimum"]  # the minimum quantity of energy asked
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded",
                                      {"quantity": energy_minimum, "price": price})

                    energy_available_consumption -= energy_minimum
                    money_earned_inside += energy_minimum * price  # money earned by selling energy to the device
                    energy_sold_inside += energy_minimum  # the absolute value of energy sold inside
                except:
                    pass

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_demands.pop(line_index)

        # offer side
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_offers)):  # offers
            energy = sorted_offers[i][1]
            price = sorted_offers[i][2]
            price = max(price, min_price)
            device_name = sorted_offers[i][3]

            if sorted_offers[i][0] == 1:  # if it is urgent
                lines_to_remove.append(i)

                try:  # if it is a subcluster
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                    couple = [energy, price]
                    quantities_given.append(couple)

                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded",
                                      {"quantity": energy, "price": price})

                money_spent_inside -= energy * price  # money spent by buying energy from the subcluster
                energy_bought_inside -= energy  # the absolute value of energy bought inside
                energy_available_production += energy  # the difference between the max and the min is consumed

            else:  # if it is a device, it may asks for a min of energy too
                try:
                    energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")[
                        "energy_minimum"]  # the minimum quantity of energy asked
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded",
                                      {"quantity": energy_minimum, "price": price})

                    money_spent_inside -= energy_minimum * price  # money spent by buying energy from the subcluster
                    energy_bought_inside -= energy_minimum  # the absolute value of energy bought inside
                    energy_available_production += energy_minimum  # the difference between the max and the min is consumed
                except:
                    pass

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_offers.pop(line_index)

        # calculating the energy available
        # print(f"max conso {maximum_energy_consumed}; min conso {minimum_energy_consumed}; max prod {maximum_energy_produced}; min prod {minimum_energy_produced}")

        # print()
        # print(energy_bought_inside)
        # print(energy_available_production)
        # print(minimum_energy_consumed)
        # print(energy_sold_inside)
        # print(minimum_energy_produced)
        # print(energy_available_production)
        # print()
        # print(energy_available_consumption)
        # print(energy_sold_inside)
        # ##########################################################################################
        # distribution

        # distribution among consumptions
        # emergency_total = 0
        energy_total = 0
        for element in sorted_demands:  # we sum all the emergency and the energy of demands
            # emergency_total += element[0] + 0.1
            energy_total += element[1]

        if energy_total != 0:
            # emergency_mean = emergency_total / len(sorted_demands)  # the mean of emergency among all devices and subclusters

            # if emergency_mean == 0:  # to avoid divsions by 0
            #     emergency_mean = 1

            energy_ratio = energy_available_consumption / energy_total  # the average rate of satisfaction

            for element in sorted_demands:  # then we distribute a bit of energy to all demands
                # print(element)
                # emergency_ratio = (element[0] + 0.1) / emergency_total  # the relative emergency of this demand
                energy = element[1] * energy_ratio
                price = element[2]
                device_name = element[3]  # the name of the device or the subcluster

                # todo: virer cette rustine
                if device_name == '':
                    break

                try:  # if it is a subcluster
                    quantities_and_prices = self._catalog.get(f"{device_name}.quantities_given")
                    quantities_and_prices.append([energy, price])

                    self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})
                # print(energy_sold_inside)

                money_earned_inside += energy * price  # money earned by selling energy to the subcluster
                energy_sold_inside += energy  # the absolute value of energy sold inside

        # distribution among productions
        # emergency_total = 0
        energy_total = 0
        for element in sorted_offers:  # we sum all the emergency and the energy of offers
            # emergency_total += element[0] + 0.1
            energy_total -= element[1]

        if energy_total != 0:
            # emergency_mean = emergency_total / len(sorted_offers)  # the mean of emergency among all devices and subclusters

            energy_ratio = energy_available_production / energy_total  # the average rate of satisfaction

            for element in sorted_offers:  # then we distribute a bit of energy to all offers
                # emergency_ratio = (element[0] + 0.1) / emergency_mean  # the relative emergency of this offer
                energy = element[1] * energy_ratio
                device_name = element[3]  # the name of the device or the subcluster
                price = element[2]

                # todo: virer cette rustine
                if device_name == '':
                    break

                try:  # if it is a subcluster
                    quantities_and_prices = self._catalog.get(f"{device_name}.quantities_asked")
                    quantities_and_prices.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                money_spent_inside -= energy * price  # money spent by buying energy from the device
                energy_bought_inside -= energy  # the absolute value of energy bought inside

        # print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")
        print(energy_bought_outside - energy_sold_outside + energy_bought_inside - energy_sold_inside)
        # print(self._catalog.get(f"{cluster.name}.quantities_given"))
        # print(self._catalog.get(f"{cluster.name}.quantities_asked"))
        # print()

        # updates the balances
        self._catalog.set(f"{cluster.name}.energy_bought", {"inside": energy_bought_inside, "outside": energy_bought_outside})
        self._catalog.set(f"{cluster.name}.energy_sold", {"inside": energy_sold_inside, "outside": energy_sold_outside})

        self._catalog.set(f"{cluster.name}.money_spent", {"inside": money_spent_inside, "outside": money_spent_outside})
        self._catalog.set(f"{cluster.name}.money_earned", {"inside": money_earned_inside, "outside": money_earned_outside})

        # print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")
        # print(self._quantities_exchanged_internally)
        #
        # print()


user_classes_dictionary[f"{SubclusterHeatPartial.__name__}"] = SubclusterHeatPartial

