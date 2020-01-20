# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign

from math import inf


class WhenProfitable(Supervisor):

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
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_offers)):  # offers
            if sorted_offers[i][0] == 1:  # if it is urgent
                energy_difference += sorted_offers[i][1]  # incrementing the total
                lines_to_remove.append(i)

                try:  # if it is a subcluster
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
                # print(selling_price)

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
        [sorted_demands, sorted_offers] = self._price_sort(cluster)  # sort the quantities according to their prices

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

        # print(energy_available_consumption)
        # print(energy_available_production)

        # ##########################################################################################
        # distribution

        # distribution among consumptions
        i = 0
        while energy_available_consumption > sorted_demands[i][1] and i < len(sorted_demands)-1:  # as long as there is energy available
            device_name = sorted_demands[i][3]

            try:  # if it is a subcluster
                quantities_and_prices = self._catalog.get(f"{device_name}.quantities_asked")

                self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                energy_available_consumption -= quantities_and_prices[0]

                money_earned_inside += quantities_and_prices[0] * quantities_and_prices[1]  # money earned by selling energy to the subcluster
                energy_sold_inside += quantities_and_prices[0]  # the absolute value of energy sold inside
            except:  # if it is a device
                energy = sorted_demands[i][1]  # the quantity of energy needed
                price = sorted_demands[i][2]

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})
                energy_available_consumption -= energy  # the difference between the max and the min is consumed

                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

            i += 1

        # this line gives the remnant of energy to the last unserved device
        if sorted_demands[i][1]:  # if the demand really exists
            device_name = sorted_demands[i][3]
            try:
                quantities_and_prices = self._catalog.get(f"{device_name}.quantities_asked")

                quantities_and_prices[0] = energy_available_consumption
                self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                energy_available = 0

                money_earned_inside += quantities_and_prices[0] * quantities_and_prices[1]  # money earned by selling energy to the subcluster
                energy_sold_inside += quantities_and_prices[0]  # the absolute value of energy sold inside
            except:
                price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy_available_consumption, "price": price})
                energy_available = 0  # the difference between the max and the min is consumed

                money_earned_inside += energy_available_consumption * price  # money earned by selling energy to the device
                energy_sold_inside += energy_available_consumption  # the absolute value of energy sold inside

        # distribution among productions
        i = 0
        while energy_available_production > - sorted_offers[i][1] and i < len(sorted_offers)-1:  # as long as there is energy available
            device_name = sorted_offers[i][3]

            try:  # if it is a subcluster
                quantities_and_prices = self._catalog.get(f"{device_name}.quantities_asked")

                self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                energy_available_production += quantities_and_prices[0]

                money_spent_inside -= quantities_and_prices[0] * quantities_and_prices[1]  # money spent by buying energy from the subcluster
                energy_bought_inside -= quantities_and_prices[0]  # the absolute value of energy bought inside
            except:  # if it is a device
                energy = sorted_offers[i][1]  # the quantity of energy needed
                price = sorted_demands[i][2]  # the price of energy

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})
                energy_available_production += energy  # the difference between the max and the min is consumed

                money_spent_inside -= energy * price  # money spent by buying energy from the device
                energy_bought_inside -= energy  # the absolute value of energy bought inside

            i += 1

        # this line gives the remnant of energy to the last unserved device
        if sorted_offers[i][1]:  # if the demand really exists
            device_name = sorted_offers[i][3]
            try:
                quantities_and_prices = self._catalog.get(f"{device_name}.quantities_asked")

                quantities_and_prices[0] = energy_available_production
                self._catalog.set(f"{device_name}.quantities_given", quantities_and_prices)  # it is served
                energy_available = 0

                money_spent_inside -= quantities_and_prices[0] * quantities_and_prices[1]  # money spent by buying energy from the subcluster
                energy_bought_inside -= quantities_and_prices[0]  # the absolute value of energy bought inside
            except:
                price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy_available_production, "price": price})
                energy_available = 0  # the difference between the max and the min is consumed

                money_spent_inside -= energy_available_production * price  # money spent by buying energy from the device
                energy_bought_inside -= energy_available_production  # the absolute value of energy bought inside

        # print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")
        # print(energy_bought_outside - energy_sold_outside + energy_bought_inside - energy_sold_inside)
        # print(self._catalog.get(f"{cluster.name}.quantities_given"))
        # print(self._catalog.get(f"{cluster.name}.quantities_asked"))

        # updates the balances
        self._catalog.set(f"{cluster.name}.energy_bought", {"inside": energy_bought_inside, "outside": energy_bought_outside})
        self._catalog.set(f"{cluster.name}.energy_sold", {"inside": energy_sold_inside, "outside": energy_sold_outside})

        self._catalog.set(f"{cluster.name}.money_spent", {"inside": money_spent_inside, "outside": money_spent_outside})
        self._catalog.set(f"{cluster.name}.money_earned", {"inside": money_earned_inside, "outside": money_earned_outside})
        #
        # print(f"bought outside {energy_bought_outside}; sold outside {energy_sold_outside}; bought inside {energy_bought_inside}; sold inside {energy_sold_inside}")
        # print(self._quantities_exchanged_internally)
        #
        # print()


user_classes_dictionary[f"{WhenProfitable.__name__}"] = WhenProfitable

