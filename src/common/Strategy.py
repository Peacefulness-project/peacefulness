# This sheet describes the supervisor
# It contains only the name of a file serving as a "main" for the supervisor and a description
from math import inf


class Strategy:

    def __init__(self, world, name, description):
        self._name = name  # the name of the supervisor  in the catalog
        self.description = description  # a description of the objective/choice/process of the supervisor

        self._catalog = world.catalog  # the catalog in which some data are stored

        world.register_strategy(self)  # register the strategy into world dedicated dictionary

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

    def ascendant_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        # once the aggregator has made made local arrangements, it publishes its needs (both in demand and in offer)
        pass

    def distribute_remote_energy(self, aggregator):  # after having exchanged with the exterior, the aggregator ditribute the energy among the devices and the subaggregators it has to manage
        pass

    # ##########################################################################################
    # Strategy blocks
    # ##########################################################################################

    def _get_quantities(self, aggregator):  # prepare the quantities needed by every device and subaggregator
        # getting back the needs for every device
        for device_name in aggregator.devices:
            Emax = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]  # maximal quantity of energy wanted by the device
            price = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["price"]

            if Emax == 0:  # if the device is inactive
                break  # we do nothing and we go to the other device

            aggregator.quantities[device_name] = {"quantity": Emax, "price": price}  # the local quantities are updated in the aggregator dedicated dictionary

        # getting back the needs for every subaggregator
        for subaggregator in aggregator.subaggregators:
            managed_aggregator_quantities = self._catalog.get(f"{subaggregator.name}.quantities_asked")  # couples prices/quantities asked by the managed aggregators
            i = 0  # an arbitrary number given to couples price/quantities
            for element in managed_aggregator_quantities:
                aggregator.quantities[f"{subaggregator.name}_lot_{i}"] = {"quantity": element["quantity"], "price": element["price"]}
                i += 1

    def _limit_prices(self, aggregator):  # set limit prices for selling and buying energy
        min_grid_price = self._catalog.get(f"{aggregator.nature.name}.grid_selling_price")  # the price at which the grid sells energy
        max_grid_price = self._catalog.get(f"{aggregator.nature.name}.grid_buying_price")  # the price at which the grid sells energy
        max_price = max_grid_price + abs(max_grid_price) / 2  # maximum price the aggregator is allowed to bill
        min_price = min_grid_price - abs(min_grid_price) / 2  # minimum price the aggregator is allowed to bill

        return [min_price, max_price]

    def _limit_quantities(self, aggregator, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters=0):  # compute the minimum an maximum quntities of energy needed to be consumed and produced locally
        # quantities concerning devices
        for converter_name in aggregator.devices:
            energy_minimum = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
            energy_nominal = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]  # the nominal quantity of energy asked
            energy_maximum = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]  # the maximum quantity of energy asked

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

        # quantities concerning subaggregators
        for subaggregator in aggregator.subaggregators:  # quantities concerning aggregators
            quantities_and_prices = self._catalog.get(f"{subaggregator.name}.quantities_asked")

            # balances
            for couple in quantities_and_prices:  # for each couple energy/price

                if abs(couple["price"]) >= max_price and couple["quantity"] > 0:  # if the quantity is absolutely necessary
                    minimum_energy_consumed += couple["quantity"]
                    maximum_energy_consumed += couple["quantity"]

                    couple["price"] = min(couple["price"], max_price)  # maximum price is artificially limited

                elif abs(couple["price"]) <= min_price and couple["quantity"] < 0:  # if the quantity is absolutely necessary
                    minimum_energy_produced -= couple["quantity"]
                    maximum_energy_produced -= couple["quantity"]

                    couple["price"] = max(couple["price"], min_price)  # minimum price is artificially limited

                else:  # if the quantity is not necessary
                    if couple["quantity"] > 0:  # energy bought
                        maximum_energy_consumed += couple["quantity"]

                    elif couple["quantity"] < 0:  # energy sold
                        maximum_energy_produced -= couple["quantity"]

        # quantities concerning converters
        for converter_name in aggregator.converters:
            energy_minimum = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
            energy_maximum = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]  # the maximum quantity of energy asked

            # balances
            minimum_energy_produced -= energy_minimum
            energy_available_from_converters -= energy_maximum

        return [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters]

    # ##########################################################################################
    # ascendant phase functions
    # ##########################################################################################

    def _remove_emergencies(self, aggregator, sorted_demands, sorted_offers):  # remove all the demands and offers who are urgent
        lines_to_remove = []  # a list containing the number of lines having to be removed

        # removing of urgent demands
        for i in range(len(sorted_demands)):  # demands
            device_name = sorted_demands[i]["name"]

            if sorted_demands[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

            else:  # if it is a device, it may asks for a min of energy too
                if device_name in aggregator.devices:  # if it is a device
                    energy_minimum = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                    sorted_demands[i]["quantity"] -= energy_minimum

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_demands.pop(line_index)

        lines_to_remove = []  # a list containing the number of lines having to be removed

        # removing of urgent offers
        for i in range(len(sorted_offers)):  # demands
            device_name = sorted_offers[i]["name"]

            if sorted_offers[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

            else:  # if it is a device, it may asks for a min of energy too
                if device_name in aggregator.devices:  # if it is a device
                    energy_minimum = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                    sorted_offers[i]["quantity"] -= energy_minimum

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_offers.pop(line_index)

        return [sorted_demands, sorted_offers]

    def _exchanges_balance(self, aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside):
        for couple in self._catalog.get(f"{aggregator.name}.quantities_given"):
            if couple["quantity"] > 0:  # energy bought by the aggregator
                # making balances
                # energy bought
                money_spent_outside += couple["quantity"] * couple["price"]  # the absolute value of money spent outside
                energy_bought_outside += couple["quantity"] * aggregator.efficiency  # the absolute value of energy bought outside

            elif couple["quantity"] < 0:  # energy sold by the aggregator
                # making balances
                # energy sold
                money_earned_outside -= couple["quantity"] * couple["price"]  # the absolute value of money earned outside
                energy_sold_outside -= couple["quantity"] * aggregator.efficiency  # the absolute value of energy sold outside

        return [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside]

    def _prepare_quantitites_subaggregator(self, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, price, quantities_and_prices):  # this function prepare the quantities and prices asked or proposed to the grid
        if maximum_energy_produced < minimum_energy_consumed or maximum_energy_consumed < minimum_energy_produced:  # if there is no possibility to balance the grid without help
            energy_difference = maximum_energy_consumed - minimum_energy_consumed
            quantities_and_prices.append({"quantity": energy_difference, "price": inf})  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)

        else:  # for the quantities which are not urgent
            energy_difference = maximum_energy_consumed - maximum_energy_produced  # this energy represents the unavailable part of non-urgent quantities of energy
            quantities_and_prices.append({"quantity": energy_difference, "price": price})  # satisfy the need at a more reasonable price

        return quantities_and_prices

    def _calculate_prices(self, sorted_demands, sorted_offers, max_price, min_price):
        if sorted_demands:
            buying_price = min(sorted_demands[0]["price"], max_price)  # maximum price given by consumers
            final_price = buying_price
        else:
            buying_price = None

        if sorted_offers:
            selling_price = max(sorted_offers[0]["price"], min_price)  # minimum price given by producers
            final_price = selling_price
        else:
            selling_price = None

        try:
            final_price = (buying_price + selling_price) / 2  # initialization of the final price
        except:
            pass

        return [buying_price, selling_price, final_price]

    def _prepare_quantities_when_profitable(self, aggregator, sorted_demands, sorted_offers, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices, buying_price, selling_price, final_price):
        if maximum_energy_produced < minimum_energy_consumed or maximum_energy_consumed < minimum_energy_produced:  # if there is no possibility to balance the grid without help
            if minimum_energy_consumed > maximum_energy_produced:  # if there is a lack of production
                quantities_and_prices = [{"quantity": minimum_energy_consumed - maximum_energy_produced, "price": inf}]  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)

                quantity_remaining_offer = 0  # there is not enough production to satisfy even the urgent needs
                quantity_remaining_demand = maximum_energy_consumed - minimum_energy_consumed  # the non-urgent consumption
                quantities_exchanged = maximum_energy_produced  # there is no available energy to make intern exchanges, quantity exchanged internally is set to the maximum energy produced

            else:  # if there is a lack of consumption
                quantities_and_prices = [{"quantity": -(minimum_energy_produced - maximum_energy_consumed), "price": -inf}]  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)

                quantity_remaining_offer = maximum_energy_produced - minimum_energy_produced  # the non-urgent production
                quantity_remaining_demand = 0  # there is not enough consumption to absorb the urgent production
                quantities_exchanged = maximum_energy_produced  # there is no available energy to make intern exchanges, quantity exchanged internally is set to the maximum energy consumed

        else:  # if the grid can satisfy its urgent needs
            # first it organizes profitable interns exchanges
            [sorted_demands, sorted_offers] = self._remove_emergencies(aggregator, sorted_demands, sorted_offers)  # the mininum of energy, both for demands and offers, is removed form the corresponding lists

            i = 0  # iteration on consumption
            j = 0  # iteration on production

            quantities_exchanged = max(minimum_energy_produced, minimum_energy_consumed)  # the urgent quantities have obligatory been satisfied
            available_energy = min(maximum_energy_produced, maximum_energy_consumed) - quantities_exchanged  # the remaining quantity available for exchanges once urgent needs have been satisfied

            demand = 0  # quantities wanted for consumption
            offer = 0  # quantities wanted for production

            while buying_price >= selling_price and i < len(sorted_demands) - 1:  # as long the buying price is above the selling one and that there is demand
                demand += sorted_demands[i]["quantity"]  # total of demand exchanged internally
                buying_price = sorted_demands[i]["price"]
                final_price = buying_price

                while buying_price >= selling_price and offer <= demand and j < len(sorted_offers) - 1:  # as long as there is offer
                    offer -= sorted_offers[j]["quantity"]  # total of offer exchanged internally
                    selling_price = sorted_offers[j]["price"]
                    final_price = selling_price

                    j += 1

                if offer > available_energy:  # if the offer exceeds the available energy
                    offer = available_energy  # it is reduced to this value
                    break  # and the loop ends

                if demand > available_energy:  # if the demand exceeds the available energy
                    demand = available_energy  # it is reduced to this value
                    break  # and the loop ends

                i += 1

            quantities_exchanged += min(offer, demand)  # the quantity exchanged internally is the minimum of the current offer and demand

            # the remaining quantities of energy are reported outside
            # calculus of the remaining quantity of energy for consumption
            quantity_remaining_demand = maximum_energy_consumed - quantities_exchanged - 0*max(minimum_energy_produced, minimum_energy_consumed)  # the remaining quantity of energy

            # calculus of the remaining quantity of energy for production
            quantity_remaining_offer = maximum_energy_produced - quantities_exchanged - 0*max(minimum_energy_consumed, minimum_energy_produced)  # the remaining quantity of energy

        # setting the call for above supervisor
        # demand
        if sorted_demands:  # if there is a demand
            price_remaining_demand = (final_price + sorted_demands[-1]["price"]) / 2  # the price used is the mean between the intern price and the lowest price
        else:
            price_remaining_demand = 0

        quantities_and_prices.append([quantity_remaining_demand, price_remaining_demand])  # the quantity the aggregator wants to buy cheaply

        # offer
        if sorted_offers:  # if there is an offer
            price_remaining_offer = (final_price + sorted_offers[-1]["price"]) / 2  # the price used is the mean between the intern price and the highest price
        else:
            price_remaining_offer = 0
        quantities_and_prices.append([-quantity_remaining_offer, price_remaining_offer])  # the quantity the aggregator wants to sell expensively

        return [quantities_exchanged, quantities_and_prices]

    def _prepare_quantities_emergency_only(self, aggregator, sorted_demands, sorted_offers, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices):  # put all the urgent needs in the quantities and prices asked to the superior aggregator
        if maximum_energy_produced < minimum_energy_consumed or maximum_energy_consumed < minimum_energy_produced:  # if there is no possibility to balance the grid without help
            if minimum_energy_consumed > maximum_energy_produced:  # if there is a lack of production
                quantities_and_prices = [{"quantity": minimum_energy_consumed - maximum_energy_produced, "price": inf}]  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)

            else:  # if there is a lack of consumption
                quantities_and_prices = [{"quantity": -(minimum_energy_produced - maximum_energy_consumed), "price": -inf}]  # wants to satisfy the minimum, regardless the price (i.e sells even at -inf and buys even at +inf)

        return quantities_and_prices

    def _publish_needs(self, aggregator, quantities_and_prices):  # this function manages the appeals to the superior aggregator regarding capacity and efficiency
        energy_pullable = aggregator.capacity  # total energy obtainable from the superior through the connection
        energy_pushable = aggregator.capacity  # total energy givable from the superior through the connection

        def get_price(line):
            return line["price"]

        quantities_and_prices = sorted(quantities_and_prices, key=get_price, reverse=True)  # sort the quantities and price by decreasing price

        # capacity and efficiency management
        # at this point, couples are formulated from this aggregator point of view (without the effect of capacity and of efficiency)
        for couple in quantities_and_prices:

            if couple["quantity"] > 0:  # if it is a demand of energy
                couple["quantity"] = min(couple["quantity"], energy_pullable) / aggregator.efficiency  # the minimum between the need and the remaining quantity
                couple["price"] = couple["price"] * aggregator.efficiency

                energy_pullable -= couple["quantity"] * aggregator.efficiency

            else:  # if it is an offer of energy
                couple["quantity"] = max(couple["quantity"], - energy_pushable) / aggregator.efficiency  # the minimum between the need and the remaining quantity, but values are negative
                couple["price"] = couple["price"] * aggregator.efficiency

                energy_pushable += couple["quantity"] * aggregator.efficiency

        self._catalog.set(f"{aggregator.name}.quantities_asked", quantities_and_prices)  # publish its needs

    # ##########################################################################################
    # converters management
    # ##########################################################################################

    def _call_to_converters(self, aggregator, min_price, sorted_conversion_offers, energy_to_convert):  # method attributing demands to converters according to the quantity of energy to be converted
        i = 0
        energy_converted = 0

        if len(sorted_conversion_offers) >= 1:  # if there are still offers
            while energy_to_convert > - sorted_conversion_offers[i]["quantity"] and i < len(sorted_conversion_offers) - 1:  # as long as there is energy available
                converter_name = sorted_conversion_offers[i]["name"]
                energy = sorted_conversion_offers[i]["quantity"]  # the quantity of energy needed
                price = sorted_conversion_offers[i]["price"]  # the price of energy
                price = max(price, min_price)
                Emin = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_asked")["quantity"]  # we get back the minimum, which has already been served

                self._catalog.set(f"{converter_name}.{aggregator.nature.name}.energy_asked", {"quantity": Emin + energy, "price": price})
                energy_converted += energy

                i += 1

        # this line gives the remnant of energy to the last unserved device
        if sorted_conversion_offers[i]["quantity"]:  # if the demand really exists
            converter_name = sorted_conversion_offers[i]["name"]
            energy = max(sorted_conversion_offers[i]["quantity"], - energy_to_convert)  # the quantity of energy needed
            price = sorted_conversion_offers[i]["price"]  # the price of energy
            price = max(price, min_price)

            Emin = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_asked")["quantity"]  # we get back the minimum, which has already been served

            self._catalog.set(f"{converter_name}.{aggregator.nature.name}.energy_asked", {"quantity": Emin + energy, "price": price})
            energy_converted += energy

        return energy_converted

    def _energy_received_from_converters(self, aggregator, money_spent_outside, energy_bought_outside):
        for converter_name in aggregator.converters:
            quantity = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_accorded")

            money_spent_outside -= quantity["quantity"] * quantity["price"]  # the absolute value of money spent outside
            energy_bought_outside -= quantity["quantity"]  # the absolute value of energy bought outside

        return [money_spent_outside, energy_bought_outside]

    # ##########################################################################################
    # sort functions
    # ##########################################################################################

    def get_emergency(self, line):
        return line["emergency"]

    def get_revenue(self, line):
        return line["quantity"] * line["price"]

    def get_price(self, line):
        return line["price"]

    def _sort_quantities(self, aggregator, sort_function):  # a function calculating the emergency associated with devices and returning 2 sorted lists: one for the demands and one for the offers
        sorted_demands = []  # a list where the demands of energy are sorted by emergency
        sorted_offers = []  # a list where the offers of energy are sorted by emergency

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        for device_name in aggregator.devices:  # if there is missing energy
            Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
            Enom = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]
            Emax = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
            price = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["price"]

            if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                emergency = 1  # an indicator of how much the quantity is urgent
            else:
                emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

            if Emax > 0:  # if the energy is strictly positive, it means that the device or the aggregator is asking for energy
                sorted_demands.append({"emergency": emergency, "quantity": Emax, "price": price, "name": device_name})
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                sorted_offers.append({"emergency": emergency, "quantity": Emax, "price": price, "name": device_name})

            # if the energy = 0, then there is no need to add it to one of the list

        for subaggregator in aggregator.subaggregators:
            quantities = self._catalog.get(f"{subaggregator.name}.quantities_asked")

            for couple in quantities:
                if couple["energy"] > 0:  # if the energy is strictly positive, it means that the device or the aggregator is asking for energy
                    price = max(couple["price"], min_price)
                    emergency = min(1, (price - min_price)/(max_price - min_price))

                    sorted_demands.append({"emergency": emergency, "quantity": couple["energy"], "price": couple["price"], "name": subaggregator.name})
                elif couple["energy"] < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                    price = min(couple["price"], max_price)
                    emergency = min(1, (max_price - price) / (max_price - min_price))

                    sorted_offers.append({"emergency": emergency, "quantity": couple["energy"], "price": couple["price"], "name": subaggregator.name})

        sorted_demands = sorted(sorted_demands, key=sort_function, reverse=True)
        sorted_offers = sorted(sorted_offers, key=sort_function, reverse=True)

        return [sorted_demands, sorted_offers]

    def _sort_conversion_offers(self, aggregator, sort_function_converters, sorted_offers, sort_function_offers):  # a function calculating the emergency associated with devices and returning 2 sorted lists: one for the demands and one for the offers
        sorted_conversion_offers = []  # a list where the offers of energy from converters is sorted according to the chosen function

        for converter_name in aggregator.converters:  # if there is missing energy
            Emin = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
            Emax = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
            price = self._catalog.get(f"{converter_name}.{aggregator.nature.name}.energy_wanted")["price"]

            self._catalog.set(f"{converter_name}.{aggregator.nature.name}.energy_asked", {"quantity": Emin, "price": price})

            sorted_conversion_offers.append({"emergency": 0, "quantity": Emax - Emin, "price": price, "name": converter_name})  # converters always have an emergency of 0, as they are purely facultative

            emergency = 1  # as this quantity is only the physical minimum, it has to be served by the aggregator
            sorted_offers.append({"emergency": emergency, "quantity": Emin, "price": price, "name": converter_name})  # append the physical minimum to be served to the classical offers

        sorted_conversion_offers = sorted(sorted_conversion_offers, key=sort_function_converters, reverse=True)
        sorted_offers = sorted(sorted_offers, key=sort_function_offers, reverse=True)

        return [sorted_conversion_offers, sorted_offers]

    # ##########################################################################################
    # emergency distribution functions

    def _serve_emergency_demands(self, aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside):
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_demands)):  # demands
            energy = sorted_demands[i]["quantity"]

            if energy > energy_available_consumption:  # if the quantity demanded is superior to the rest of energy available
                energy = energy_available_consumption  # it is served partially, even if it is urgent

            device_name = sorted_demands[i]["name"]
            price = sorted_demands[i]["price"]
            price = min(price, max_price)

            if sorted_demands[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

                try:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                    couple = {"quantity": energy, "price": price}
                    quantities_given.append(couple)

                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

            else:  # if it is a device, it may asks for a min of energy too
                try:
                    energy_minimum = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": energy_minimum, "price": price})

                    energy_available_consumption -= energy_minimum
                    money_earned_inside += energy_minimum * price  # money earned by selling energy to the device
                    energy_sold_inside += energy_minimum  # the absolute value of energy sold inside
                    sorted_demands[i]["quantity"] = energy - energy_minimum
                except:
                    pass

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_demands.pop(line_index)

        return [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _serve_emergency_offers(self, aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside):
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_offers)):  # offers
            energy = sorted_offers[i]["quantity"]

            if energy < - energy_available_production:  # if the quantity offered is superior to the rest of energy available
                energy = - energy_available_production  # it is served partially, even if it is urgent

            price = sorted_offers[i]["price"]
            price = max(price, min_price)
            device_name = sorted_offers[i]["name"]

            if sorted_offers[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

                try:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                    couple = {"quantity": energy, "price": price}
                    quantities_given.append(couple)

                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # it is served
                except:  # if it is a device
                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": energy, "price": price})

                money_spent_inside -= energy * price  # money spent by buying energy from the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy bought inside
                energy_available_production += energy  # the difference between the max and the min is consumed

            else:  # if it is a device, it may asks for a min of energy too
                try:
                    energy_minimum = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": energy_minimum, "price": price})

                    money_spent_inside -= energy_minimum * price  # money spent by buying energy from the subaggregator
                    energy_bought_inside -= energy_minimum  # the absolute value of energy bought inside
                    energy_available_production += energy_minimum  # the difference between the max and the min is consumed
                    sorted_offers[i]["quantity"] = energy - energy_minimum
                except:
                    pass

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_offers.pop(line_index)

        return [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside]

    # ##########################################################################################
    # distribution functions

    def _distribute_consumption_full_service(self, aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside):
        i = 0

        if len(sorted_demands) >= 1:  # if there are offers
            while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
                device_name = sorted_demands[i]["name"]
                energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
                price = sorted_demands[i]["price"]  # the price of energy
                price = min(price, max_price)

                try:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")

                    quantities_given.append({"quantity": energy, "price": price})
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served
                except:  # if it is a device
                    Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

                money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

                i += 1

            # this block gives the remaining energy to the last unserved device
            if sorted_demands[i]["quantity"]:  # if the demand really exists
                device_name = sorted_demands[i]["name"]
                energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
                price = sorted_demands[i]["price"]  # the price of energy
                price = min(price, max_price)

                try:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                    quantities_given.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served
                except:  # if it is a device
                    Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

        return [energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _distribute_production_full_service(self, aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside):
        i = 0

        if len(sorted_offers) >= 1:  # if there are offers
            while energy_available_production > - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
                device_name = sorted_offers[i]["name"]
                energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
                price = sorted_offers[i]["price"]  # the price of energy
                price = max(price, min_price)

                try:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")

                    quantities_given.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served

                except:  # if it is a device
                    Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

                money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy sold inside
                energy_available_production += energy

                i += 1

            # this line gives the remnant of energy to the last unserved device
            if sorted_offers[i]["quantity"]:  # if the demand really exists
                device_name = sorted_offers[i]["name"]
                energy = max(sorted_offers[i]["quantity"], - energy_available_production)  # the quantity of energy needed
                price = sorted_offers[i]["price"]  # the price of energy
                price = max(price, min_price)

                try:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")
                    quantities_given.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served
                except:  # if it is a device
                    Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

                money_spent_inside -= energy * price  # money spent by buying energy from the device
                energy_bought_inside -= energy  # the absolute value of energy bought inside

        return [energy_available_production, money_spent_inside, energy_bought_inside]

    def _distribute_consumption_partial_service(self, aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside):  # distribution among consumptions
        energy_total = 0
        for element in sorted_demands:  # we sum all the emergency and the energy of demands1
            energy_total += element["quantity"]

        if energy_total != 0:

            energy_ratio = min(1, energy_available_consumption / energy_total)  # the average rate of satisfaction, cannot be superior to 1

            for demand in sorted_demands:  # then we distribute a bit of energy to all demands
                device_name = demand["name"]
                energy = demand["energy"]  # the quantity of energy needed
                price = demand["price"]  # the price of energy
                price = min(price, max_price)
                energy *= energy_ratio

                try:  # if it is a subaggregator
                    Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})
                except:  # if it is a device
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")

                    quantities_given.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served

                money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

        return [energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _distribute_production_partial_service(self, aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside):
        # distribution among productions
        energy_total = 0

        for element in sorted_offers:  # we sum all the emergency and the energy of offers
            energy_total -= element["energy"]

        if energy_total != 0:

            energy_ratio = min(1, energy_available_production / energy_total)  # the average rate of satisfaction, cannot be superior to 1

            for offer in sorted_offers:  # then we distribute a bit of energy to all offers
                device_name = offer["name"]
                energy = offer["energy"]  # the quantity of energy needed
                price = offer["price"]  # the price of energy
                price = max(price, min_price)
                energy *= energy_ratio

                try:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{device_name}.quantities_given")

                    quantities_given.append([energy, price])
                    self._catalog.set(f"{device_name}.quantities_given", quantities_given)  # then it is served

                except:  # if it is a device
                    Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served

                    self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", {"quantity": Emin + energy, "price": price})

                money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy sold inside
                energy_available_production += energy

        return [energy_available_production, money_spent_inside, energy_bought_inside]

    # ##########################################################################################
    # results publication
    # ##########################################################################################

    def _update_balances(self, aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside):
        self._catalog.set(f"{aggregator.name}.energy_bought", {"inside": energy_bought_inside, "outside": energy_bought_outside})
        self._catalog.set(f"{aggregator.name}.energy_sold", {"inside": energy_sold_inside, "outside": energy_sold_outside})

        self._catalog.set(f"{aggregator.name}.money_spent", {"inside": money_spent_inside, "outside": money_spent_outside})
        self._catalog.set(f"{aggregator.name}.money_earned", {"inside": money_earned_inside, "outside": money_earned_outside})

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name


class SupervisorException(Exception):
    def __init__(self, message):
        super().__init__(message)


