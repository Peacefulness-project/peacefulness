# This sheet describes the supervisor
# It contains only the name of a file serving as a "main" for the supervisor and a description
from math import inf
from src.tools.GlobalWorld import get_world


class Strategy:

    def __init__(self, name, description):
        self._name = name  # the name of the supervisor  in the catalog
        self.description = description  # a description of the objective/choice/process of the supervisor

        self._messages = {"ascendant": {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None},
                          "descendant": {"quantity": 0, "price": 0},
                          "sorted_lists": {"emergency": 0, "quantity": 0, "price": 0, "name": ""}}

        world = get_world()  # get the object world
        self._catalog = world.catalog  # the catalog in which some data are stored

        world.register_strategy(self)  # register the strategy into world dedicated dictionary

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def complete_message(self, additional_elements):
        for message in self._messages:
            old_message = self._messages[message]
            self._messages[message] = {**old_message, **additional_elements}

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

    def _limit_prices(self, aggregator):  # set limit prices for selling and buying energy
        min_price = self._catalog.get(f"{aggregator.nature.name}.limit_selling_price")  # the price at which the grid sells energy
        max_price = self._catalog.get(f"{aggregator.nature.name}.limit_buying_price")  # the price at which the grid sells energy

        return [min_price, max_price]

    def _limit_quantities(self, aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters=0):  # compute the minimum an maximum quantities of energy needed to be consumed and produced locally
        # quantities concerning devices
        for device_name in aggregator.devices:
            energy_minimum = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
            energy_nominal = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]  # the nominal quantity of energy asked
            energy_maximum = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]  # the maximum quantity of energy asked

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
            quantities_and_prices = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")

            for element in quantities_and_prices:
                energy_minimum = element["energy_minimum"]  # the minimum quantity of energy asked
                energy_nominal = element["energy_nominal"]  # the nominal quantity of energy asked
                energy_maximum = element["energy_maximum"]  # the maximum quantity of energy asked

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

        return [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters]

    # ##########################################################################################
    # forecast
    # ##########################################################################################

    def call_to_converters(self, aggregator):
        aggregator.forecaster.get_predictions()

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

            else:  # if a min of energy is needed
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

            else:  # if a min of energy is needed
                energy_minimum = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                sorted_offers[i]["quantity"] -= energy_minimum

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            sorted_offers.pop(line_index)

        return [sorted_demands, sorted_offers]

    def _exchanges_balance(self, aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside):
        if aggregator.superior:
            for element in self._catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded"):
                if element["quantity"] > 0:  # energy bought by the aggregator
                    # making balances
                    # energy bought
                    money_spent_outside += element["quantity"] * element["price"]  # the absolute value of money spent outside
                    energy_bought_outside += element["quantity"] * aggregator.efficiency  # the absolute value of energy bought outside

                elif element["quantity"] < 0:  # energy sold by the aggregator
                    # making balances
                    # energy sold
                    money_earned_outside -= element["quantity"] * element["price"]  # the absolute value of money earned outside
                    energy_sold_outside -= element["quantity"] * aggregator.efficiency  # the absolute value of energy sold outside

        return [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside]

    def _prepare_quantitites_subaggregator(self, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices):  # this function prepare the quantities and prices asked or proposed to the grid
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}

        if maximum_energy_consumed > maximum_energy_produced:  # if energy is lacking
            energy_difference = max(minimum_energy_consumed - maximum_energy_produced, 0)
            energy_minimum = energy_difference  # the minimum required to balance the grid
            energy_nominal = energy_difference  # the nominal required to balance the grid

            energy_difference = maximum_energy_consumed - maximum_energy_produced  # this energy represents the unavailable part of non-urgent quantities of energy
            energy_maximum = energy_difference  # the minimum required to balance the grid

        else:  # if there is too much energy
            energy_difference = - max(minimum_energy_produced - maximum_energy_consumed, 0)
            energy_minimum = energy_difference  # the minimum required to balance the grid
            energy_nominal = energy_difference  # the nominal required to balance the grid

            energy_difference = maximum_energy_consumed - maximum_energy_produced  # this energy represents the unavailable part of non-urgent quantities of energy
            energy_maximum = energy_difference  # the minimum required to balance the grid

        message["energy_minimum"] = energy_minimum
        message["energy_nominal"] = energy_nominal
        message["energy_maximum"] = energy_maximum
        quantities_and_prices.append(message)

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
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}

        if maximum_energy_produced < minimum_energy_consumed or maximum_energy_consumed < minimum_energy_produced:  # if there is no possibility to balance the grid without help
            if minimum_energy_consumed > maximum_energy_produced:  # if there is a lack of production
                energy_difference = minimum_energy_consumed - maximum_energy_produced
                energy_minimum = energy_difference  # the minimum required to balance the grid
                energy_nominal = energy_difference  # the nominal required to balance the grid
                energy_maximum = energy_difference  # the maximum required to balance the grid

                quantity_remaining_offer = 0  # there is not enough production to satisfy even the urgent needs
                quantity_remaining_demand = maximum_energy_consumed - minimum_energy_consumed  # the non-urgent consumption
                quantities_exchanged = maximum_energy_produced  # there is no available energy to make intern exchanges, quantity exchanged internally is set to the maximum energy produced

            else:  # if there is a lack of consumption
                energy_difference = - (minimum_energy_produced - maximum_energy_consumed)
                energy_minimum = energy_difference  # the minimum required to balance the grid
                energy_nominal = energy_difference  # the nominal required to balance the grid
                energy_maximum = energy_difference  # the minimum required to balance the grid

                quantity_remaining_offer = maximum_energy_produced - minimum_energy_produced
                quantity_remaining_demand = 0  # there is not enough consumption to absorb the urgent production
                quantities_exchanged = maximum_energy_consumed  # there is no available energy to make intern exchanges, quantity exchanged internally is set to the maximum energy consumed

            message["energy_minimum"] = energy_minimum
            message["energy_nominal"] = energy_nominal
            message["energy_maximum"] = energy_maximum
            quantities_and_prices.append(message)

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
            quantity_remaining_demand = maximum_energy_consumed - quantities_exchanged  # the remaining quantity of energy

            # calculus of the remaining quantity of energy for production
            quantity_remaining_offer = maximum_energy_produced - quantities_exchanged  # the remaining quantity of energy

        # setting the call for above supervisor
        # demand
        if sorted_demands:  # if there is a demand
            price_remaining_demand = (final_price + sorted_demands[-1]["price"]) / 2  # the price used is the mean between the intern price and the lowest price
        else:
            price_remaining_demand = 0

        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        message["energy_maximum"] = quantity_remaining_demand
        quantities_and_prices.append(message)

        # offer
        if sorted_offers:  # if there is an offer
            price_remaining_offer = (final_price + sorted_offers[-1]["price"]) / 2  # the price used is the mean between the intern price and the highest price
        else:
            price_remaining_offer = 0

        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        message["energy_maximum"] = - quantity_remaining_offer
        quantities_and_prices.append(message)

        return [quantities_exchanged, quantities_and_prices]

    def _prepare_quantities_emergency_only(self, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices):  # put all the urgent needs in the quantities and prices asked to the superior aggregator
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}

        if maximum_energy_produced < minimum_energy_consumed or maximum_energy_consumed < minimum_energy_produced:  # if there is no possibility to balance the grid without help
            if minimum_energy_consumed > maximum_energy_produced:  # if there is a lack of production
                energy_difference = max(minimum_energy_consumed - maximum_energy_produced, 0)
                energy_minimum = energy_difference  # the minimum required to balance the grid
                energy_nominal = energy_difference  # the nominal required to balance the grid
                energy_maximum = energy_difference  # the minimum required to balance the grid

            else:  # if there is a lack of consumption
                energy_difference = - max(minimum_energy_produced - maximum_energy_consumed, 0)
                energy_minimum = energy_difference  # the minimum required to balance the grid
                energy_nominal = energy_difference  # the nominal required to balance the grid
                energy_maximum = energy_difference  # the minimum required to balance the grid

            message["energy_minimum"] = energy_minimum
            message["energy_nominal"] = energy_nominal
            message["energy_maximum"] = energy_maximum
            quantities_and_prices.append(message)

        return quantities_and_prices

    def _publish_needs(self, aggregator, quantities_and_prices):  # this function manages the appeals to the superior aggregator regarding capacity and efficiency
        energy_pullable = aggregator.capacity  # total energy obtainable from the superior through the connection
        energy_pushable = aggregator.capacity  # total energy givable from the superior through the connection

        # capacity and efficiency management
        # at this point, couples are formulated from this aggregator point of view (without the effect of capacity and of efficiency)
        for element in quantities_and_prices:
            if element["energy_maximum"] > 0:  # if it is a demand of energy
                element["energy_minimum"] = min(element["energy_minimum"], energy_pullable) / aggregator.efficiency  # the minimum between the need and the remaining quantity
                element["energy_nominal"] = min(element["energy_nominal"], energy_pullable) / aggregator.efficiency  # the minimum between the need and the remaining quantity
                element["energy_maximum"] = min(element["energy_maximum"], energy_pullable) / aggregator.efficiency  # the minimum between the need and the remaining quantity
                # couple["price"] = couple["price"] * aggregator.efficiency

                energy_pullable -= element["energy_maximum"] * aggregator.efficiency

            else:  # if it is an offer of energy
                element["energy_minimum"] = max(element["energy_minimum"], - energy_pushable) / aggregator.efficiency  # the minimum between the need and the remaining quantity, but values are negative
                element["energy_nominal"] = max(element["energy_nominal"], - energy_pushable) / aggregator.efficiency  # the minimum between the need and the remaining quantity, but values are negative
                element["energy_maximum"] = max(element["energy_maximum"], - energy_pushable) / aggregator.efficiency  # the minimum between the need and the remaining quantity, but values are negative
                # couple["price"] = couple["price"] * aggregator.efficiency

                energy_pushable += element["energy_maximum"] * aggregator.efficiency

        return quantities_and_prices

    # ##########################################################################################
    # sort functions
    # ##########################################################################################

    def get_emergency(self, line):
        return line["emergency"]

    def get_revenue(self, line):
        return line["quantity"] * line["price"]

    def get_price(self, line):
        return line["price"]

    def get_quantity(self, line):
        return line["quantity"]

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
                message = {element: self._messages["sorted_lists"][element] for element in self._messages["sorted_lists"]}
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["price"] = price
                message["name"] = device_name
                sorted_demands.append(message)
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                message = {element: self._messages["sorted_lists"][element] for element in self._messages["sorted_lists"]}
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["price"] = price
                message["name"] = device_name
                sorted_offers.append(message)
            # if the energy = 0, then there is no need to add it to one of the list

        for subaggregator in aggregator.subaggregators:
            quantities_and_prices = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")

            for element in quantities_and_prices:
                Emin = element["energy_minimum"]  # the minimum quantity of energy asked
                Enom = element["energy_nominal"]  # the nominal quantity of energy asked
                Emax = element["energy_maximum"]  # the maximum quantity of energy asked
                price = element["price"]

            if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                emergency = 1  # an indicator of how much the quantity is urgent
            else:
                emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

            if Emax > 0:  # if the energy is strictly positive, it means that the device or the aggregator is asking for energy
                message = {element: self._messages["sorted_lists"][element] for element in self._messages["sorted_lists"]}
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["price"] = price
                message["name"] = device_name
                sorted_demands.append(message)
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                message = {element: self._messages["sorted_lists"][element] for element in self._messages["sorted_lists"]}
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["price"] = price
                message["name"] = device_name
                sorted_offers.append(message)

        sorted_demands = sorted(sorted_demands, key=sort_function, reverse=True)
        sorted_offers = sorted(sorted_offers, key=sort_function, reverse=True)

        return [sorted_demands, sorted_offers]

    # ##########################################################################################
    # emergency distribution functions

    def _serve_emergency_demands(self, aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside):
        lines_to_remove = []  # a list containing the number of lines having to be removed
        for i in range(len(sorted_demands)):  # demands
            energy = sorted_demands[i]["quantity"]

            name = sorted_demands[i]["name"]
            price = sorted_demands[i]["price"]
            price = min(price, max_price)

            if sorted_demands[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

                if energy > energy_available_consumption:  # if the quantity demanded is superior to the rest of energy available
                    energy = energy_available_consumption  # it is served partially, even if it is urgent

                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = energy
                message["price"] = price

                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

            else:  # if it is a device, it may asks for a min of energy too
                energy_minimum = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = energy_minimum
                message["price"] = price

                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                energy_available_consumption -= energy_minimum
                money_earned_inside += energy_minimum * price  # money earned by selling energy to the device
                energy_sold_inside += energy_minimum  # the absolute value of energy sold inside
                sorted_demands[i]["quantity"] = energy - energy_minimum

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
            name = sorted_offers[i]["name"]

            if sorted_offers[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = energy
                message["price"] = price
                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_spent_inside -= energy * price  # money spent by buying energy from the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy bought inside
                energy_available_production += energy  # the difference between the max and the min is consumed

            else:  # if it is a device, it may asks for a min of energy too
                energy_minimum = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]  # the minimum quantity of energy asked
                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = energy_minimum
                message["price"] = price
                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                money_spent_inside -= energy_minimum * price  # money spent by buying energy from the subaggregator
                energy_bought_inside -= energy_minimum  # the absolute value of energy bought inside
                energy_available_production += energy_minimum  # the difference between the max and the min is consumed
                sorted_offers[i]["quantity"] = energy - energy_minimum

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
                name = sorted_demands[i]["name"]
                energy = sorted_demands[i]["quantity"]  # the quantity of energy needed
                price = sorted_demands[i]["price"]  # the price of energy
                price = min(price, max_price)

                Emin = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served
                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

                i += 1

            # this block gives the remaining energy to the last unserved device
            if sorted_demands[i]["quantity"]:  # if the demand really exists
                name = sorted_demands[i]["name"]
                energy = min(sorted_demands[i]["quantity"], energy_available_consumption)  # the quantity of energy needed
                price = sorted_demands[i]["price"]  # the price of energy
                price = min(price, max_price)

                Emin = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served
                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = Emin + energy
                message["price"] = price
                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

        return [energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _distribute_production_full_service(self, aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside):
        i = 0

        if len(sorted_offers) >= 1:  # if there are offers
            while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
                name = sorted_offers[i]["name"]
                energy = sorted_offers[i]["quantity"]  # the quantity of energy needed
                price = sorted_offers[i]["price"]  # the price of energy
                price = max(price, min_price)

                Emin = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served
                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_spent_inside -= energy * price  # money earned by selling energy to the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy sold inside
                energy_available_production += energy

                i += 1

            # this line gives the remnant of energy to the last unserved device
            if sorted_offers[i]["quantity"]:  # if the demand really exists
                name = sorted_offers[i]["name"]
                energy = max(sorted_offers[i]["quantity"], - energy_available_production)  # the quantity of energy needed
                price = sorted_offers[i]["price"]  # the price of energy
                price = max(price, min_price)

                Emin = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served
                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

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
                name = demand["name"]
                energy = demand["quantity"]  # the quantity of energy needed
                price = demand["price"]  # the price of energy
                price = min(price, max_price)
                energy *= energy_ratio

                Emin = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served
                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = Emin + energy
                message["price"] = price
                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_earned_inside += energy * price  # money earned by selling energy to the subaggregator
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

        return [energy_available_consumption, money_earned_inside, energy_sold_inside]

    def _distribute_production_partial_service(self, aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside):
        # distribution among productions
        energy_total = 0

        for element in sorted_offers:  # we sum all the emergency and the energy of offers
            energy_total -= element["quantity"]

        if energy_total != 0:

            energy_ratio = min(1, energy_available_production / energy_total)  # the average rate of satisfaction, cannot be superior to 1

            for offer in sorted_offers:  # then we distribute a bit of energy to all offers
                name = offer["name"]
                energy = offer["quantity"]  # the quantity of energy needed
                price = offer["price"]  # the price of energy
                price = max(price, min_price)
                energy *= energy_ratio

                Emin = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")["quantity"]  # we get back the minimum, which has already been served
                message = {element: self._messages["descendant"][element] for element in self._messages["descendant"]}
                message["quantity"] = Emin + energy
                message["price"] = price
                if name in aggregator.subaggregators:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

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


