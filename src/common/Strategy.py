# This sheet describes the supervisor
# It contains only the name of a file serving as a "main" for the supervisor and a description
from math import inf
from src.tools.GlobalWorld import get_world


class Strategy:

    def __init__(self, name, description):
        self._name = name  # the name of the supervisor  in the catalog
        self.description = description  # a description of the objective/choice/process of the supervisor

        self._messages = {"bottom-up": {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None},
                          "top-down": {"quantity": 0, "price": 0},
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

    def bottom_up_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        # once the aggregator has made made local arrangements, it publishes its needs (both in demand and in offer)
        pass

    def top_down_phase(self, aggregator):  # after having exchanged with the exterior, the aggregator ditribute the energy among the devices and the subaggregators it has to manage
        pass

    def check(self, aggregator):  # verification that decisions taken by supervisors are compatible for multi-energy devices

        [demands, offers] = self.make_energy_balances(aggregator)

        demands_total = 0
        offers_total = 0
        for element in demands:
            demands_total += element["quantity"]
        for element in offers:
            offers_total += element["quantity"]

        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside

        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)
        demands_total += energy_sold_outside
        offers_total -= energy_bought_outside

        if abs(demands_total + offers_total) >= 1e-6:  # if balances do not match, a second round of distribution is performed
            self._catalog.set("incompatibility", True)
            self._reinitialise_decisions(aggregator)

    # ##########################################################################################
    # Strategy blocks
    # ##########################################################################################

    def _limit_prices(self, aggregator):  # set limit prices for selling and buying energy
        min_price = self._catalog.get(f"{aggregator.nature.name}.limit_selling_price")  # the price at which the grid sells energy
        max_price = self._catalog.get(f"{aggregator.nature.name}.limit_buying_price")  # the price at which the grid sells energy

        return [min_price, max_price]

    def _limit_quantities(self, aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced):  # compute the minimum an maximum quantities of energy needed to be consumed and produced locally
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

        # mismatch calculation
        # mismatch = minimum_energy_consumed + maximum_energy_consumed - minimum_energy_produced - maximum_energy_produced

        return [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced]

    # ##########################################################################################
    # forecast
    # ##########################################################################################

    def call_to_forecast(self, aggregator):
        aggregator.forecaster.get_predictions()

    # ##########################################################################################
    # bottom-up phase functions
    # ##########################################################################################

    def make_energy_balances(self, aggregator):
        demands = []  # a list where the demands of energy are sorted by emergency
        offers = []  # a list where the offers of energy are sorted by emergency

        for device_name in aggregator.devices:  # if there is missing energy
            energy = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_accorded")["quantity"]
            price = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_accorded")["price"]

            if energy > 0:  # if the energy is strictly positive, it means that the device or the aggregator is asking for energy
                data = dict()
                data["quantity"] = energy
                data["price"] = price
                data["name"] = device_name
                demands.append(data)
            elif energy < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                data = dict()
                data["quantity"] = energy
                data["price"] = price
                data["name"] = device_name
                offers.append(data)
            # if the energy = 0, then there is no need to add it to one of the list

        for subaggregator in aggregator.subaggregators:
            quantities_and_prices = self._catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded")

            for element in quantities_and_prices:
                energy = element["quantity"]  # the minimum quantity of energy asked
                price = element["price"]

                if energy > 0:  # if the energy is strictly positive, it means that the device or the aggregator is asking for energy
                    data = dict()
                    data["quantity"] = energy
                    data["price"] = price
                    data["name"] = subaggregator.name
                    demands.append(data)
                elif energy < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                    data = dict()
                    data["quantity"] = energy
                    data["price"] = price
                    data["name"] = subaggregator.name
                    offers.append(data)

        return [demands, offers]

    def _reinitialise_decisions(self, aggregator):  # a method used when a second round is necessary to reset the decisions taken by the aggregator
        message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}

        for device_name in aggregator.devices:  # if there is missing energy
            self._catalog.set(f"{device_name}.{aggregator.nature.name}.energy_accorded", message)

        for subaggregator in aggregator.subaggregators:
            self._catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", [])

    def _remove_emergencies(self, aggregator, sorted_demands, sorted_offers):  # remove all the demands and offers who are urgent
        lines_to_remove = []  # a list containing the number of lines having to be removed

        # removing of urgent demands
        for i in range(len(sorted_demands)):  # demands
            device_name = sorted_demands[i]["name"]

            if sorted_demands[i]["emergency"] == 1:  # if it is urgent
                lines_to_remove.append(i)

            else:  # if a min of energy is needed
                energy_minimum = sorted_demands[i]["quantity_min"]  # the minimum quantity of energy asked
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
                energy_minimum = sorted_offers[i]["quantity_min"]   # the minimum quantity of energy asked
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
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}

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
            buying_boolean = 1
        else:
            buying_price = 0
            buying_boolean = 0

        if sorted_offers:
            selling_price = max(sorted_offers[0]["price"], min_price)  # minimum price given by producers
            final_price = selling_price
            selling_boolean = 1
        else:
            selling_price = 0
            selling_boolean = 0

        final_price = (buying_price * buying_boolean + selling_price * selling_boolean) / 2  # initialization of the final price

        return [buying_price, selling_price, final_price]

    def _update_quantities_exchanged(self, quantities_exchanged_internally, quantities_bought_from_outside, quantities_sold_to_outside, quantity_to_affect, demands, offers):
        if offers["name"] == "outside":  # if the energy is bought from outside
            quantities_bought_from_outside += quantity_to_affect
        elif demands["name"] == "outside":  # if energy is sold to outside
            quantities_sold_to_outside += quantity_to_affect
        else:
            quantities_exchanged_internally += abs(quantity_to_affect)

        return quantities_exchanged_internally, quantities_bought_from_outside, quantities_sold_to_outside

    def _prepare_quantities_when_profitable(self, aggregator, sorted_demands, sorted_offers, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices):

        # first, urgent quantities are removed from the demands and offers list
        [sorted_demands, sorted_offers] = self._remove_emergencies(aggregator, sorted_demands, sorted_offers)  # the mininum of energy, both for demands and offers, is removed from the corresponding lists
        quantities_exchanged_internally = min(minimum_energy_produced, minimum_energy_consumed)  # the urgent quantities have obligatory been satisfied
        urgent_quantity_to_cover = minimum_energy_consumed - minimum_energy_produced  # the remaining urgent quantities that not has not been served yet

        # second, profitable exchanges are made
        i = 0
        j = 0

        # adding the buying capacity to the other aggregator as a standard offer
        outside_selling_price = aggregator.contract.buying_price
        outside_selling_capacity = - aggregator.capacity["buying"]
        outside_offer = {"emergency": 0, "quantity": outside_selling_capacity, "price": outside_selling_price, "name": "outside"}

        sorted_offers.append(outside_offer)
        sorted_offers = sorted(sorted_offers, key=self.get_price, reverse=False)

        # adding the selling capacity to the other aggregator as a standard demand
        outside_buying_price = aggregator.contract.selling_price
        outside_buying_capacity = aggregator.capacity["selling"]
        outside_demand = {"emergency": 0, "quantity": outside_buying_capacity, "price": outside_buying_price, "name": "outside"}

        sorted_demands.append(outside_demand)
        sorted_demands = sorted(sorted_demands, key=self.get_price, reverse=True)

        energy_bought_outside = 0
        energy_sold_outside = 0

        # the minimum to keep available to satisfy the urgent needs
        if urgent_quantity_to_cover > 0:
            energy_available = maximum_energy_produced + outside_buying_capacity - urgent_quantity_to_cover
        else:
            energy_available = maximum_energy_consumed - outside_selling_price + urgent_quantity_to_cover

        while i < len(sorted_demands) and j < len(sorted_offers) and energy_available:
            buying_price = sorted_demands[i]["price"]
            selling_price = sorted_offers[j]["price"]

            if buying_price >= selling_price:
                if sorted_demands[i]["quantity"] > - sorted_offers[j]["quantity"]:  # if the producer cannot serve totally
                    quantity_served = min(-sorted_offers[j]["quantity"], energy_available)
                    sorted_demands[i]["quantity"] -= quantity_served  # the part served
                    quantities_exchanged_internally, energy_bought_outside, energy_sold_outside = self._update_quantities_exchanged(quantities_exchanged_internally, energy_bought_outside, energy_sold_outside, -quantity_served, sorted_demands[i], sorted_offers[j])
                    j += 1  # next producer
                    energy_available -= quantity_served

                else:  # if the producer can serve totally
                    quantity_served = min(sorted_demands[i]["quantity"], energy_available)
                    sorted_offers[j]["quantity"] += quantity_served
                    quantities_exchanged_internally, energy_bought_outside, energy_sold_outside = self._update_quantities_exchanged(quantities_exchanged_internally, energy_bought_outside, energy_sold_outside, quantity_served, sorted_demands[i], sorted_offers[j])
                    i += 1  # next consumer
                    energy_available -= quantity_served

            else:
                break

        # non critical exchanges
        # note that the aggregator can both buy and sell energy to outside
        # while being not physically possible, it can be financially interesting
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        message["energy_maximum"] = energy_bought_outside
        quantities_and_prices.append(message)

        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        message["energy_maximum"] = energy_sold_outside
        quantities_and_prices.append(message)

        # third, the difference between urgent production and consumption is affected
        urgent_energy_with_outside = 0

        if urgent_quantity_to_cover > 0:  # if there is more consumption
            while urgent_quantity_to_cover > 0:  # as long as there is too much consumption, production is used to cover it
                if j >= len(sorted_offers):
                    raise StrategyException(f"The minimum consumption cannot be served.")
                elif - sorted_offers[j]["quantity"] > urgent_quantity_to_cover:  # if the cheapest production is sufficient to fill the gap
                    sorted_offers[j]["quantity"] += urgent_quantity_to_cover  # the production available is reduced
                    if sorted_offers[j]["name"] == "outside":  # if the energy is bought from outside
                        urgent_energy_with_outside += urgent_quantity_to_cover
                    else:
                        quantities_exchanged_internally += abs(urgent_quantity_to_cover)
                    urgent_quantity_to_cover = 0

                else:  # if the cheapest production is not sufficient to fill the gap
                    urgent_quantity_to_cover += sorted_offers[j]["quantity"]
                    if sorted_offers[j]["name"] == "outside":  # if the energy is bought from outside
                        urgent_energy_with_outside += sorted_offers[j]["quantity"]
                    else:
                        quantities_exchanged_internally += abs(sorted_offers[j]["quantity"])
                    j += 1

        elif urgent_quantity_to_cover < 0:  # if there is more production
            while urgent_quantity_to_cover < 0:  # as long as there is too much consumption, production is used to cover it
                if i >= len(sorted_demands):
                    raise StrategyException(f"The minimum production cannot be absorbed.")
                elif sorted_demands[i]["quantity"] > - urgent_quantity_to_cover:  # if the most expensive consumption is sufficient to fill the gap
                    sorted_demands[i]["quantity"] += urgent_quantity_to_cover  # the consumption available is reduced
                    if sorted_demands[i]["name"] == "outside":  # if energy is sold to outside
                        urgent_energy_with_outside += urgent_quantity_to_cover
                    else:
                        quantities_exchanged_internally += abs(urgent_quantity_to_cover)
                    urgent_quantity_to_cover = 0

                else:  # if the most expensive consumption is not sufficient to fill the gap
                    urgent_quantity_to_cover += sorted_demands[i]["quantity"]
                    if sorted_demands[i]["name"] == "outside":  # if energy is sold to outside
                        urgent_energy_with_outside += sorted_demands[i]["quantity"]
                    else:
                        quantities_exchanged_internally += abs(sorted_demands[i]["quantity"])
                    i += 1

        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        message["energy_maximum"] = urgent_energy_with_outside
        message["energy_minimum"] = urgent_energy_with_outside
        quantities_and_prices.append(message)

        return [quantities_exchanged_internally, quantities_and_prices]

    def _prepare_quantities_emergency_only(self, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices):  # put all the urgent needs in the quantities and prices asked to the superior aggregator
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}

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
        energy_pullable = aggregator.capacity["buying"]  # total energy obtainable from the superior through the connection
        energy_pushable = aggregator.capacity["selling"]  # total energy givable from the superior through the connection

        # capacity and efficiency management
        # at this point, couples are formulated from this aggregator point of view (without the effect of capacity and of efficiency)
        # here, capacity and efficiency are managed
        for element in quantities_and_prices:
            if element["energy_maximum"] > 0:  # if it is a demand of energy
                element["energy_minimum"] = min(element["energy_minimum"], energy_pullable) / aggregator.efficiency  # the minimum between the need and the remaining quantity
                element["energy_nominal"] = min(element["energy_nominal"], energy_pullable) / aggregator.efficiency  # the minimum between the need and the remaining quantity
                element["energy_maximum"] = min(element["energy_maximum"], energy_pullable) / aggregator.efficiency  # the minimum between the need and the remaining quantity
                element = aggregator._contract.contract_modification(element, self.name)

                energy_pullable -= element["energy_maximum"] * aggregator.efficiency

            else:  # if it is an offer of energy
                element["energy_minimum"] = max(element["energy_minimum"], - energy_pushable) / aggregator.efficiency  # the minimum between the need and the remaining quantity, but values are negative
                element["energy_nominal"] = max(element["energy_nominal"], - energy_pushable) / aggregator.efficiency  # the minimum between the need and the remaining quantity, but values are negative
                element["energy_maximum"] = max(element["energy_maximum"], - energy_pushable) / aggregator.efficiency  # the minimum between the need and the remaining quantity, but values are negative
                element = aggregator._contract.contract_modification(element, self.name)

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
                message["quantity_min"] = Emin
                message["price"] = price
                message["name"] = device_name
                sorted_demands.append(message)
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                message = {element: self._messages["sorted_lists"][element] for element in self._messages["sorted_lists"]}
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["quantity_min"] = Emin
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
                    message["quantity_min"] = Emin
                    message["price"] = price
                    message["name"] = subaggregator.name
                    sorted_demands.append(message)
                elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                    message = {element: self._messages["sorted_lists"][element] for element in self._messages["sorted_lists"]}
                    message["emergency"] = emergency
                    message["quantity"] = Emax
                    message["quantity_min"] = Emin
                    message["price"] = price
                    message["name"] = subaggregator.name
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

                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside

            else:
                energy_minimum = sorted_demands[i]["quantity_min"]  # the minimum quantity of energy asked
                energy_maximum = sorted_demands[i]["quantity"]  # the maximum quantity of energy asked

                if energy_minimum > energy_available_consumption:  # if the quantity demanded is superior to the rest of energy available
                    energy = energy_available_consumption  # it is served partially, even if it is urgent
                else:
                    energy = energy_minimum

                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                    sorted_demands[i]["quantity_min"] = 0
                    sorted_demands[i]["quantity"] = energy_maximum-energy_minimum  # the need is updated
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                energy_available_consumption -= energy
                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside
                sorted_demands[i]["quantity"] = energy_maximum - energy

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

                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                else:  # if it is a device
                    quantities_given = message

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded", quantities_given)  # it is served

                money_spent_inside -= energy * price  # money spent by buying energy from the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy bought inside
                energy_available_production += energy  # the difference between the max and the min is consumed

            else:  # if there is a demand for a min of energy too
                energy_minimum = sorted_offers[i]["quantity_min"]  # the minimum quantity of energy asked
                energy_maximum = sorted_offers[i]["quantity"]  # the maximum quantity of energy asked

                if energy_minimum < - energy_available_production:  # if the quantity offered is superior to the rest of energy available
                    energy = - energy_available_production  # it is served partially, even if it is urgent
                else:
                    energy = energy_minimum

                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = energy
                message["price"] = price
                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
                    quantities_given = self._catalog.get(f"{name}.{aggregator.nature.name}.energy_accorded")
                    quantities_given.append(message)
                    sorted_offers[i]["quantity_min"] = 0
                    sorted_offers[i]["quantity"] = energy_maximum - energy_minimum  # the need is updated
                else:  # if it is a device
                    quantities_given = message

                money_spent_inside -= energy * price  # money spent by buying energy from the subaggregator
                energy_bought_inside -= energy  # the absolute value of energy bought inside
                energy_available_production += energy  # the difference between the max and the min is consumed
                sorted_offers[i]["quantity"] = energy_maximum - energy

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

                Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
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

                Emin = sorted_demands[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = Emin + energy
                message["price"] = price
                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
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

                Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
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

                Emin = sorted_offers[i]["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = Emin + energy
                message["price"] = price

                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
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

                Emin = demand["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = Emin + energy
                message["price"] = price
                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
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

                Emin = offer["quantity_min"]  # we get back the minimum, which has already been served
                message = {element: self._messages["top-down"][element] for element in self._messages["top-down"]}
                message["quantity"] = Emin + energy
                message["price"] = price
                if name in [subaggregator.name for subaggregator in aggregator.subaggregators]:  # if it is a subaggregator
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

    def _update_balances(self, aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced):
        self._catalog.set(f"{aggregator.name}.energy_bought", {"inside": 0, "outside": energy_bought_outside})
        self._catalog.set(f"{aggregator.name}.energy_sold", {"inside": 0, "outside": energy_sold_outside})

        self._catalog.set(f"{aggregator.name}.money_spent", {"inside": 0, "outside": money_spent_outside})
        self._catalog.set(f"{aggregator.name}.money_earned", {"inside": 0, "outside": money_earned_outside})

        self._catalog.set(f"{aggregator.name}.energy_erased", {"production": maximum_energy_produced - energy_bought_inside, "consumption": maximum_energy_consumed - energy_sold_inside})

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name


class StrategyException(Exception):
    def __init__(self, message):
        super().__init__(message)


