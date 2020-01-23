# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign

from math import inf


class WhenProfitablePartialService(Supervisor):

    def __init__(self, name, description):
        super().__init__(name, description)

        self._quantities_exchanged_internally = dict()  # this dict contains the quantities exchanged internally

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        energy_difference = 0  # this energy is the difference between the energy consumed and produced locally
        quantities_and_prices = []  # a list containing couples energy/prices

        # getting back the needs for every device --> standard probably
        for device_name in cluster.devices:
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]  # maximal quantity of energy wanted by the device
            price = 5

            if Emax == 0:  # if the device is inactive
                break  # we do nothing and we go to the other device

            cluster.quantities[device_name] = [Emax, price, 0, 0]  # the local quantities are updated in the cluster dedicated dictionary

        for subcluster in cluster.subclusters:
            managed_cluster_quantities = self._catalog.get(f"{subcluster.name}.quantities_asked")  # couples prices/quantities asked by the managed clusters
            i = 0  # an arbitrary number given to couples price/quantities
            for element in managed_cluster_quantities:
                energy_difference += element[0]
                cluster.quantities[f"{subcluster.name}_lot_{i}"] = [element[0], element[1], 0, 0]
                i += 1

        # formulation of needs
        [sorted_demands, sorted_offers] = self._price_sort(cluster)  # sort the quantities according to their prices

        # ##########################################################################################

        # first we ensure the urgent quantities will be satisfied
        # demand side
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_demands)):  # demands
            if sorted_demands[i][0] == 1:  # if it is urgent
                energy_difference += sorted_demands[i][1]  # incrementing the total
                lines_to_remove.append(i)

                try:  # if it is a subcluster
                    self._catalog.set(f"{sorted_demands[i][3]}.quantities_given", quantities_and_prices)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{sorted_demands[i][3]}.{cluster.nature.name}.energy_accorded", {"quantity": sorted_demands[i][1], "price": sorted_demands[i][2]})

                money_earned_inside += sorted_demands[i][1] * sorted_demands[i][2]  # money earned by selling energy to the device
                energy_sold_inside += sorted_demands[i][1]  # the absolute value of energy sold inside

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_demands.pop(line_index)
        
        # offer side
        print(sorted_offers)
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_offers)):  # offers
            if sorted_offers[i][0] == 1:  # if it is urgent
                energy_difference += sorted_offers[i][1]  # incrementing the total
                lines_to_remove.append(i)

                try:  # if it is a subcluster
                    quantities_and_prices = self._catalog.get(f"{device_name}.quantities_given")

                    quantities_and_prices.append([sorted_offers[i][1], sorted_offers[i][2]])

                    self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emax, "price": price})

                money_spent_inside -= sorted_offers[i][1] * sorted_offers[i][2]  # money spent by buying energy from the subcluster
                energy_bought_inside -= sorted_offers[i][1]  # the absolute value of energy bought inside

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_offers.pop(line_index)

        # publication of these urgent needs
        quantities_and_prices = [[energy_difference, sign(energy_difference)*inf]]  # wants to satisfy everyone, regardless the price (i.e sells even at -inf and buys even at +inf)

        # updates the balances
        self._catalog.set(f"{cluster.name}.energy_bought", {"inside": energy_bought_inside, "outside": 0})
        self._catalog.set(f"{cluster.name}.energy_sold", {"inside": energy_sold_inside, "outside": 0})

        self._catalog.set(f"{cluster.name}.money_spent", {"inside": money_spent_inside, "outside": 0})
        self._catalog.set(f"{cluster.name}.money_earned", {"inside": money_earned_inside, "outside": 0})

        # ##########################################################################################

        i = 0  # iteration on consumption
        j = 0  # iteration on production

        buying_price = sorted_demands[0][1]  # price given by consumers
        selling_price = sorted_offers[0][1]  # price given by producers

        demand = 0  # quantities wanted for consumption
        offer = 0  # quantities wanted for production

        final_price = (buying_price + selling_price) / 2

        while buying_price >= selling_price and i < len(sorted_demands) - 1:  # as long the buying price is aboce the selling one and that there is demand
            demand += sorted_demands[i][1]
            buying_price = sorted_demands[i][2]
            final_price = buying_price

            while buying_price >= selling_price and offer <= demand and j < len(sorted_offers) - 1:  # as long as there is offer
                offer -= sorted_offers[j][1]
                selling_price = sorted_offers[j][2]
                final_price = selling_price

                j += 1

            i += 1

        quantities_exchanged = min(offer, demand)  # the quantity exchanged internally is the minimum of the current offer and demand
        self._quantities_exchanged_internally[cluster.name] = [quantities_exchanged, final_price]  # we store this value for the descendant phase

        # ##########################################################################################
        # exchanges with outside

        # demand
        # calculus of the restant quantity of energy for consumption
        total_demand = [line[1] for line in sorted_demands]
        total_demand = sum(total_demand)  # the total amount of energy needed for consumption
        quantity_rest_demand = total_demand - quantities_exchanged  # the restant quantity of energy

        price_rest_demand = (final_price + sorted_demands[-1][2]) / 2  # the price used is the mean between the intern price and the lowest price

        quantities_and_prices.append([quantity_rest_demand, price_rest_demand])  # the quantity the cluster wants to buy cheaply

        # offer
        # calculus of the restant quantity of energy for production
        total_offer = [line[1] for line in sorted_offers]
        total_offer = sum(total_offer)  # the total amount of energy needed for production
        quantity_rest_offer = total_offer + quantities_exchanged  # the restant quantity of energy

        price_rest_offer = (final_price + sorted_offers[-1][2]) / 2  # the price used is the mean between the intern price and the highest price

        quantities_and_prices.append([quantity_rest_offer, price_rest_offer])  # the quantity the cluster wants to sell expensively

        # todo: faire ca proprement
        for element in quantities_and_prices:
            element[0] = min(element[0] * cluster.efficiency, cluster.capacity)
            element[1] = element[1] / cluster.efficiency

        self._catalog.set(f"{cluster.name}.quantities_asked", quantities_and_prices)  # publish its needs

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = self._catalog.get(f"{cluster.name}.energy_bought")["inside"]  # the absolute value of energy bought inside
        energy_sold_inside = self._catalog.get(f"{cluster.name}.energy_sold")["inside"]  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = self._catalog.get(f"{cluster.name}.money_earned")["inside"]  # the absolute value of money earned inside
        money_spent_inside = self._catalog.get(f"{cluster.name}.money_spent")["inside"]  # the absolute value of money spent inside

        # print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")

        # what is given
        # print(self._catalog.get(f"{cluster.name}.quantities_given"))
        # print(cluster.name)
        for couple in self._catalog.get(f"{cluster.name}.quantities_given"):
            if couple[0] > 0:  # energy bought by the aggregator

                # making balances
                # energy bought
                energy_bought_outside += couple[0]  # the absolute value of energy bought outside
                money_spent_outside += couple[0] * couple[1]  # the absolute value of money spent outside

            elif couple[0] < 0:  # energy sold by the aggregator

                # making balances
                # energy sold
                energy_sold_outside -= couple[0]  # the absolute value of energy sold outside
                money_earned_outside -= couple[0] * couple[1]  # the absolute value of money earned outside

        # formulation of needs
        [sorted_demands, sorted_offers] = self._emergency_sort(cluster)  # sort the quantities according to their prices

        # ##########################################################################################
        # balance of energy available

        # we remove the urgent needs, which have been satisfied above

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

        # calculating the energy available
        energy_available_consumption = self._quantities_exchanged_internally[cluster.name][0] + energy_bought_outside  # the total energy available for consumptions
        energy_available_production = self._quantities_exchanged_internally[cluster.name][0] + energy_sold_outside  # the total energy available for productions
        print(self._quantities_exchanged_internally[cluster.name][0])

        # ##########################################################################################
        # distribution

        # distribution among consumptions
        emergency_total = 0
        energy_total = 0
        for element in sorted_demands:  # we sum all the emergency and the energy of demands
            emergency_total += element[0]
            energy_total += element[1]

        if energy_total != 0:
            emergency_mean = emergency_total / len(sorted_demands)  # the mean of emergency among all devices and subclusters

            if emergency_mean == 0:  # to avoid divsions by 0
                emergency_mean = 1

            energy_ratio = energy_available_consumption / energy_total  # the average rate of satisfaction

            for element in sorted_demands:  # then we distribute a bit of energy to all demands
                emergency_ratio = element[0] / emergency_mean  # the relative emergency of this demand
                energy = element[1] * energy_ratio * emergency_ratio
                price = element[2]
                device_name = element[3]  # the name of the device or the subcluster

                try:  # if it is a subcluster
                    quantities_and_prices = self._catalog.get(f"{device_name}.quantities_given")
                    quantities_and_prices.append([energy, price])

                    self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                money_earned_inside += energy * price  # money earned by selling energy to the subcluster
                energy_sold_inside += energy  # the absolute value of energy sold inside

        # distribution among productions
        emergency_total = 0
        energy_total = 0
        for element in sorted_offers:  # we sum all the emergency and the energy of offers
            emergency_total += element[0] + 0.1
            energy_total -= element[1]

        if energy_total != 0:
            emergency_mean = emergency_total / len(sorted_offers)  # the mean of emergency among all devices and subclusters

            energy_ratio = energy_available_production / energy_total  # the average rate of satisfaction

            for element in sorted_offers:  # then we distribute a bit of energy to all offers
                emergency_ratio = (element[0] + 0.1) / emergency_mean  # the relative emergency of this offer
                energy = element[1] * energy_ratio * emergency_ratio
                device_name = element[3]  # the name of the device or the subcluster
                price = element[2]

                try:  # if it is a subcluster
                    quantities_and_prices = self._catalog.get(f"{device_name}.quantities_asked")
                    quantities_and_prices.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                money_spent_inside -= energy * price  # money spent by buying energy from the device
                energy_bought_inside -= energy  # the absolute value of energy bought inside

        print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")
        print(energy_bought_outside - energy_sold_outside + energy_bought_inside - energy_sold_inside)
        print(self._catalog.get(f"{cluster.name}.quantities_given"))
        print(self._catalog.get(f"{cluster.name}.quantities_asked"))
        print()

        # updates the balances
        self._catalog.set(f"{cluster.name}.energy_bought", {"inside": energy_bought_inside, "outside": energy_bought_outside})
        self._catalog.set(f"{cluster.name}.energy_sold", {"inside": energy_sold_inside, "outside": energy_sold_outside})

        self._catalog.set(f"{cluster.name}.money_spent", {"inside": money_spent_inside, "outside": money_spent_outside})
        self._catalog.set(f"{cluster.name}.money_earned", {"inside": money_earned_inside, "outside": money_earned_outside})

        # print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")
        # print(self._quantities_exchanged_internally)
        #
        # print()


user_classes_dictionary[f"{WhenProfitablePartialService.__name__}"] = WhenProfitablePartialService
