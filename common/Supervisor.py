# This sheet describes the supervisor
# It contains only the name of a file serving as a "main" for the supervisor and a description
from math import inf


class Supervisor:

    def __init__(self, name, description):
        self._name = name  # the name of the supervisor  in the catalog
        self.description = description  # a description of the objective/choice/process of the supervisor

        self._catalog = None  # the catalog in which some data are stored

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):
        pass

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        pass

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        pass

    # ##########################################################################################
    # Strategy briques
    # ##########################################################################################

    def _get_quantities(self, cluster):
        # getting back the needs for every device
        for device_name in cluster.devices:
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]  # maximal quantity of energy wanted by the device
            price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

            if Emax == 0:  # if the device is inactive
                break  # we do nothing and we go to the other device

            cluster.quantities[device_name] = [Emax, price, 0, 0]  # the local quantities are updated in the cluster dedicated dictionary

        # getting back the needs for every subcluster
        for subcluster in cluster.subclusters:
            managed_cluster_quantities = self._catalog.get(f"{subcluster.name}.quantities_asked")  # couples prices/quantities asked by the managed clusters
            i = 0  # an arbitrary number given to couples price/quantities
            for element in managed_cluster_quantities:
                cluster.quantities[f"{subcluster.name}_lot_{i}"] = [element[0], element[1], 0, 0]
                i += 1

    def _limit_prices(self, cluster):
        min_grid_price = self._catalog.get(f"{cluster.nature.name}.grid_selling_price")  # the price at which the grid sells energy
        max_grid_price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")  # the price at which the grid sells energy
        max_price = max_grid_price + abs(max_grid_price) / 2  # maximum price the cluster is allowed to bill
        min_price = min_grid_price - abs(min_grid_price) / 2  # minimum price the cluster is allowed to bill

        return [min_price, max_price]

    def _limit_quantities(self, cluster, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced):
        # quantities concerning devices
        for device_name in cluster.devices:
            energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
            energy_nominal = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_nominal"]  # the nominal quantity of energy asked
            energy_maximum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]  # the maximum quantity of energy asked

            # balances
            if energy_maximum > 0:  # the device wants to consume energy
                if energy_nominal == energy_maximum:  # if it is urgent
                    minimum_energy_consumed += energy_maximum
                    
                else:  # if there is a minimum
                    minimum_energy_consumed += energy_minimum
                maximum_energy_consumed += energy_maximum

            elif energy_maximum < 0:  # the devices wants to sell energy
                if energy_nominal == energy_maximum:  # if it is urgent
                    minimum_energy_produced -= energy_maximum
                else:
                    minimum_energy_produced -= energy_minimum
                maximum_energy_produced -= energy_maximum

            # quantities concerning subclusters
        for subcluster in cluster.subclusters:  # quantities concerning clusters
            quantities_and_prices = self._catalog.get(f"{subcluster.name}.quantities_asked")

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

        return [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced]

    # ##########################################################################################
    # ascendant phase functions
    
    def _remove_emergencies(self, cluster, sorted_demands, sorted_offers):
        lines_to_remove = []  # a list containing the number of lines having to be removed

        # removing of urgent demands
        for i in range(len(sorted_demands)):  # demands
            device_name = sorted_demands[i][3]

            if sorted_demands[i][0] == 1:  # if it is urgent
                lines_to_remove.append(i)

            else:  # if it is a device, it may asks for a min of energy too
                try:
                    energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                    sorted_demands[i][1] -= energy_minimum
                except:
                    pass

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_demands.pop(line_index)

        lines_to_remove = []  # a list containing the number of lines having to be removed

        # removing of urgent offers
        for i in range(len(sorted_offers)):  # demands
            device_name = sorted_offers[i][3]

            if sorted_offers[i][0] == 1:  # if it is urgent
                lines_to_remove.append(i)

            else:  # if it is a device, it may asks for a min of energy too
                try:
                    energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                    sorted_offers[i][1] -= energy_minimum
                except:
                    pass

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_offers.pop(line_index)

        return [sorted_demands, sorted_offers]        

    def _exchanges_balance(self, cluster, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside):
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

        return [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside]

    def _prepare_quantitites_subcluster(self, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, price, quantities_and_prices):  # this function prepare the quantities and prices asked or proposed to the grid
        if maximum_energy_produced < minimum_energy_consumed or maximum_energy_consumed < minimum_energy_produced:  # if there is no possibility to balance the grid without help
            if minimum_energy_consumed > maximum_energy_produced:  # if there is a lack of production
                quantities_and_prices = [[minimum_energy_consumed - maximum_energy_produced, inf]]  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)
                energy_difference = maximum_energy_consumed - minimum_energy_consumed

            else:  # if there is a lack of consumption
                quantities_and_prices = [[-(minimum_energy_produced - maximum_energy_consumed), -inf]]  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)
                energy_difference = - (maximum_energy_produced - minimum_energy_consumed)

        else:  # for the quantity which is not urgent
            if maximum_energy_produced < maximum_energy_consumed:  # if there is a lack of production
                energy_difference = maximum_energy_consumed - maximum_energy_produced  # this energy represent  the unavialbale part of non-urgent quantities of energy

            else:  # if there is a lack of consumption
                energy_difference = - (maximum_energy_consumed - maximum_energy_produced)

        # publication of the non-urgent quantities
        quantities_and_prices.append([energy_difference, price])

        return quantities_and_prices

    def _prepare_quantities_when_profitable(self, cluster, sorted_demands, sorted_offers, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices, buying_price, selling_price, final_price):
        if maximum_energy_produced < minimum_energy_consumed or maximum_energy_consumed < minimum_energy_produced:  # if there is no possibility to balance the grid without help
            if minimum_energy_consumed > maximum_energy_produced:  # if there is a lack of production
                quantities_and_prices = [[minimum_energy_consumed - maximum_energy_produced, inf]]  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)

                quantity_remaining_offer = 0  # there is not enough production to satisfy even the urgent needs
                quantity_remaining_demand = maximum_energy_consumed - minimum_energy_consumed  # the non-urgent consumption
                quantities_exchanged = maximum_energy_produced  # there is no available energy to make intern exchanges, quantity exchanged internally is set to the maximum energy produced

            else:  # if there is a lack of consumption
                quantities_and_prices = [[-(minimum_energy_produced - maximum_energy_consumed), -inf]]  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)

                quantity_remaining_offer = maximum_energy_produced - minimum_energy_produced  # the non-urgent production
                quantity_remaining_demand = 0  # there is not enough consumption to absorb the urgent production
                quantities_exchanged = maximum_energy_produced  # there is no available energy to make intern exchanges, quantity exchanged internally is set to the maximum energy consumed

        else:  # if the grid can satisfy its urgent needs
            # first it organizes profitable interns exchanges
            [sorted_demands, sorted_offers] = self._remove_emergencies(cluster, sorted_demands, sorted_offers)  # the mininum of energy, both for demands and offers, is removed form the corresponding lists

            i = 0  # iteration on consumption
            j = 0  # iteration on production

            quantities_exchanged = max(minimum_energy_produced, minimum_energy_consumed)  # the urgent quantities have obligatory been satisfied
            available_energy = min(maximum_energy_produced, maximum_energy_consumed) - quantities_exchanged  # the remaining quantity available for exchanges once urgent needs have been satisfied
            # print(available_energy)

            demand = 0  # quantities wanted for consumption
            offer = 0  # quantities wanted for production

            while buying_price >= selling_price and i < len(sorted_demands) - 1:  # as long the buying price is above the selling one and that there is demand
                demand += sorted_demands[i][1]  # total of demand exchanged internally
                buying_price = sorted_demands[i][2]
                final_price = buying_price

                while buying_price >= selling_price and offer <= demand and j < len(sorted_offers) - 1:  # as long as there is offer
                    offer -= sorted_offers[j][1]  # total of offer exchanged internally
                    selling_price = sorted_offers[j][2]
                    final_price = selling_price

                    j += 1

                if offer > available_energy:  # if the offers exceeds the available energy
                    offer = available_energy  # it is reduced to this value
                    break  # and the loop ends

                if demand > available_energy:  # if the demand exceeds the available energy
                    demand = available_energy  # it is reduced to this value
                    break  # and the loop ends

                i += 1

            quantities_exchanged += min(offer, demand)  # the quantity exchanged internally is the minimum of the current offer and demand
            # print(quantities_exchanged)

            # the remaining quantities of energy are reported outside
            # demand
            # calculus of the remaining quantity of energy for consumption
            quantity_remaining_demand = maximum_energy_consumed - quantities_exchanged - 0*max(minimum_energy_produced, minimum_energy_consumed)  # the remaining quantity of energy

            # offer
            # calculus of the remaining quantity of energy for production
            quantity_remaining_offer = maximum_energy_produced - quantities_exchanged - 0*max(minimum_energy_consumed, minimum_energy_produced)  # the remaining quantity of energy

        # setting the call for above supervisor
        # todo: virer rustine
        if sorted_demands[-1][3] == '':
            sorted_demands.pop()
        # demand
        price_remaining_demand = (final_price + sorted_demands[-1][2]) / 2  # the price used is the mean between the intern price and the lowest price
        quantities_and_prices.append([quantity_remaining_demand, price_remaining_demand])  # the quantity the cluster wants to buy cheaply

        # offer
        # todo: virer rustine
        if sorted_offers[-1][3] == '':
            sorted_offers.pop()
        price_remaining_offer = (final_price + sorted_offers[-1][2]) / 2  # the price used is the mean between the intern price and the highest price
        quantities_and_prices.append([-quantity_remaining_offer, price_remaining_offer])  # the quantity the cluster wants to sell expensively

        return [quantities_exchanged, quantities_and_prices]

    def _publish_needs(self, cluster, quantities_and_prices):  # this function manages the appeals to the superior cluster regarding capacity and efficiency
        # todo: passer capacity en dictionnaire pour le sens
        energy_pullable = cluster.capacity  # total energy obtainable from the superior through the connection
        energy_pushable = cluster.capacity  # total energy givable from the superior through the connection

        def get_price(line):
            return line[1]

        quantities_and_prices = sorted(quantities_and_prices, key=get_price, reverse=True)  # sort the quantities and price by decreasing importance according to the sort_function

        # capacity and efficiency management
        # at this point, couples are formulated from this cluster point of view (without the effect of capacity and of efficiency)
        for couple in quantities_and_prices:

            if couple[0] > 0:  # if it is a demand of energy
                couple[0] = min(couple[0], energy_pullable) / cluster.efficiency  # the minimum between the need and the remaining quantity
                couple[1] = couple[1] * cluster.efficiency

                energy_pullable -= couple[0] * cluster.efficiency

            # the mirror
            else:
                couple[0] = max(couple[0], - energy_pushable) / cluster.efficiency  # the minimum between the need and the remaining quantity, but values are negative
                couple[1] = couple[1] * cluster.efficiency

                energy_pushable += couple[0] * cluster.efficiency

        self._catalog.set(f"{cluster.name}.quantities_asked", quantities_and_prices)  # publish its needs

    # ##########################################################################################
    # sort functions

    def get_emergency(self, line):
        return line[0]

    def get_revenue(self, line):
        return line[1] * line[2]

    def get_price(self, line):
        return line[2]

    def _sort_quantities(self, cluster, sort_function):  # a function calculating the emergency associated with devices and returning 2 sorted lists: one for the demands and one for the offers
        sorted_demands = []  # a list where the demands of energy are sorted by emergency
        sorted_offers = []  # a list where the offers of energy are sorted by emergency

        [min_price, max_price] = self._limit_prices(cluster)  # min and max prices allowed

        for device_name in cluster.devices:  # if there is missing energy
            Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]
            Enom = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_nominal"]
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]
            price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

            if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                emergency = 1  # an indicator of how much the quantity is urgent
            else:
                emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

            if Emax > 0:  # if the energy is strictly positive, it means that the device or the cluster is asking for energy
                sorted_demands.append([emergency, Emax, price, device_name])
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the cluster is proposing energy
                sorted_offers.append([emergency, Emax, price, device_name])
                
            # if the energy = 0, then there is no need to add it to one of the list

        # energy_price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")
        for subcluster in cluster.subclusters:
            quantities = self._catalog.get(f"{subcluster.name}.quantities_asked")

            for couple in quantities:
                if couple[0] > 0:  # if the energy is strictly positive, it means that the device or the cluster is asking for energy
                    price = max(couple[1], min_price)
                    emergency = min(1, (price - min_price)/(max_price - min_price))

                    sorted_demands.append([emergency, couple[0], couple[1], subcluster.name])
                elif couple[0] < 0:  # if the energy is strictly negative, it means that the device or the cluster is proposing energy
                    price = min(couple[1], max_price)
                    emergency = min(1, (max_price - price) / (max_price - min_price))

                    sorted_offers.append([emergency, couple[0], couple[1], subcluster.name])

        sorted_demands = sorted(sorted_demands, key=sort_function, reverse=True)
        sorted_offers = sorted(sorted_offers, key=sort_function, reverse=True)

        sorted_demands.append([0, 0, 0, ""])
        sorted_offers.append([0, 0, 0, ""])

        return [sorted_demands, sorted_offers]

    # ##########################################################################################
    # emergency distribution functions

    def _serve_emergency_demands(self, cluster, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside):
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_demands)):  # demands
            energy = sorted_demands[i][1]

            if energy > energy_available_consumption:
                energy = energy_available_consumption

            device_name = sorted_demands[i][3]
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
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

            else:  # if it is a device, it may asks for a min of energy too
                try:
                    energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy_minimum, "price": price})

                    energy_available_consumption -= energy_minimum
                    money_earned_inside += energy_minimum * price  # money earned by selling energy to the device
                    energy_sold_inside += energy_minimum  # the absolute value of energy sold inside
                    sorted_demands[i][1] = energy - energy_minimum
                except:
                    pass

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_demands.pop(line_index)

        return [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _serve_emergency_offers(self, cluster, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside):
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_offers)):  # offers
            energy = sorted_offers[i][1]

            if energy < - energy_available_production:
                energy = - energy_available_production

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
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                money_spent_inside -= energy * price  # money spent by buying energy from the subcluster
                energy_bought_inside -= energy  # the absolute value of energy bought inside
                energy_available_production += energy  # the difference between the max and the min is consumed

            else:  # if it is a device, it may asks for a min of energy too
                try:
                    energy_minimum = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": energy_minimum, "price": price})

                    money_spent_inside -= energy_minimum * price  # money spent by buying energy from the subcluster
                    energy_bought_inside -= energy_minimum  # the absolute value of energy bought inside
                    energy_available_production += energy_minimum  # the difference between the max and the min is consumed
                    sorted_offers[i][1] = energy - energy_minimum
                except:
                    pass

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_offers.pop(line_index)

        return [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside]

    # ##########################################################################################
    # distribution functions

    def _distribute_consumption_full_service(self, cluster, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside):
        i = 0
        while energy_available_consumption > sorted_demands[i][1] and i < len(sorted_demands) - 1:  # as long as there is energy available
            device_name = sorted_demands[i][3]
            energy = sorted_demands[i][1]  # the quantity of energy needed
            price = sorted_demands[i][2]  # the price of energy
            price = min(price, max_price)

            try:  # if it is a subcluster
                quantities_given = self._catalog.get(f"{device_name}.quantities_given")

                quantities_given.append([energy, price])
                self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served
            except:  # if it is a device
                Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

            money_earned_inside += energy * price  # money earned by selling energy to the subcluster
            energy_sold_inside += energy  # the absolute value of energy sold inside
            energy_available_consumption -= energy

            i += 1

        # this block gives the remaining energy to the last unserved device
        if sorted_demands[i][1]:  # if the demand really exists
            device_name = sorted_demands[i][3]
            energy = min(sorted_demands[i][1], energy_available_consumption)  # the quantity of energy needed
            price = sorted_demands[i][2]  # the price of energy
            price = min(price, max_price)

            try:  # if it is a subcluster
                quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                quantities_given.append([energy, price])
                self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served
            except:  # if it is a device
                Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

            money_earned_inside += energy * price  # money earned by selling energy to the device
            energy_sold_inside += energy  # the absolute value of energy sold inside

        return [energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _distribute_production_full_service(self, cluster, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside):
        i = 0
        while energy_available_production > - sorted_offers[i][1] and i < len(sorted_offers) - 1:  # as long as there is energy available
            device_name = sorted_offers[i][3]
            energy = sorted_offers[i][1]  # the quantity of energy needed
            price = sorted_offers[i][2]  # the price of energy
            price = max(price, min_price)

            try:  # if it is a subcluster
                quantities_given = self._catalog.get(f"{device_name}.quantities_given")

                quantities_given.append([energy, price])
                self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served

            except:  # if it is a device
                Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

            money_spent_inside -= energy * price  # money earned by selling energy to the subcluster
            energy_bought_inside -= energy  # the absolute value of energy sold inside
            energy_available_production += energy

            i += 1

        # this line gives the remnant of energy to the last unserved device
        if sorted_offers[i][1]:  # if the demand really exists
            device_name = sorted_offers[i][3]
            energy = max(sorted_offers[i][1], - energy_available_production)  # the quantity of energy needed
            price = sorted_offers[i][2]  # the price of energy
            price = max(price, min_price)

            try:  # if it is a subcluster
                quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                quantities_given.append([energy, price])
                self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served
            except:  # if it is a device
                Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

            money_spent_inside -= energy * price  # money spent by buying energy from the device
            energy_bought_inside -= energy  # the absolute value of energy bought inside

        return [energy_available_production, money_spent_inside, energy_bought_inside]

    def _distribute_consumption_partial_service(self, cluster, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside):  # distribution among consumptions
        # emergency_total = 0
        energy_total = 0
        for element in sorted_demands:  # we sum all the emergency and the energy of demands1
            energy_total += element[1]

        if energy_total != 0:

            energy_ratio = min(1, energy_available_consumption / energy_total)  # the average rate of satisfaction, cannot be superior to 1

            for demand in sorted_demands:  # then we distribute a bit of energy to all demands
                device_name = demand[3]
                energy = demand[1]  # the quantity of energy needed
                price = demand[2]  # the price of energy
                price = min(price, max_price)
                energy *= energy_ratio

                # todo: virer cette rustine
                if device_name == '':
                    break

                try:  # if it is a subcluster
                    Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})
                except:  # if it is a device
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")

                    quantities_given.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served

                money_earned_inside += energy * price  # money earned by selling energy to the subcluster
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

        return [energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _distribute_production_partial_service(self, cluster, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside):
        # distribution among productions
        energy_total = 0

        for element in sorted_offers:  # we sum all the emergency and the energy of offers
            energy_total -= element[1]

        if energy_total != 0:

            energy_ratio = min(1, energy_available_production / energy_total)  # the average rate of satisfaction, cannot be superior to 1

            for offer in sorted_offers:  # then we distribute a bit of energy to all offers
                device_name = offer[3]
                energy = offer[1]  # the quantity of energy needed
                price = offer[2]  # the price of energy
                price = max(price, min_price)
                energy *= energy_ratio

                # todo: virer cette rustine
                if device_name == '':
                    break

                try:  # if it is a subcluster
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")

                    quantities_given.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served

                except:  # if it is a device
                    Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                    self._catalog.set(f"{device_name}.{cluster.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

                money_spent_inside -= energy * price  # money earned by selling energy to the subcluster
                energy_bought_inside -= energy  # the absolute value of energy sold inside
                energy_available_production += energy

        return [energy_available_production, money_spent_inside, energy_bought_inside]

    # ##########################################################################################
    # results publication

    def _update_balances(self, cluster, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside):
        self._catalog.set(f"{cluster.name}.energy_bought", {"inside": energy_bought_inside, "outside": energy_bought_outside})
        self._catalog.set(f"{cluster.name}.energy_sold", {"inside": energy_sold_inside, "outside": energy_sold_outside})

        self._catalog.set(f"{cluster.name}.money_spent", {"inside": money_spent_inside, "outside": money_spent_outside})
        self._catalog.set(f"{cluster.name}.money_earned", {"inside": money_earned_inside, "outside": money_earned_outside})

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name


class SupervisorException(Exception):
    def __init__(self, message):
        super().__init__(message)


