# This strategy is the mother class for strategies able to apply succesively different options.
from src.common.Strategy import *
from typing import List, Dict, Tuple, Callable


class TrainingStrategy(Strategy):

    def __init__(self, priorities_consumption: Callable, priorities_production: Callable, strat_name=None):
        if not strat_name:
            name = "training_strategy"
        else:
            name = strat_name
        super().__init__(name, "strategy with parameters used to train a ClusteringAndStrategy algorithm")
        self._priorities_consumption = priorities_consumption

        self._priorities_production = priorities_production

        self._sort_function = get_emergency  # laisser le choix: à déterminer par l'algo de ClusteringAndStrategy, je pense

        self._options_consumption: Callable = None
        self._options_production: Callable = None

        self._catalog.add(f"unwanted_delivery_cuts_{self.name}", 0)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _get_priorities_consumption(self) -> List[str]:
        ordered_list = ["min"] + self._priorities_consumption(self)  # satisfying the minimum quantities is always, implicitly, the absolute priority
        return ordered_list

    def _get_priorities_production(self) -> List[str]:
        ordered_list = ["min"] + self._priorities_production(self)  # satisfying the minimum quantities is always, implicitly, the absolute priority
        return ordered_list

    def _assess_quantities_for_each_option(self, aggregator: "Aggregator") -> Dict:
        pass

    def _apply_priorities_exchanges(self, aggregaor: "Aggregator", quantity_to_affect: float,
                                    quantity_available_per_option: Dict, quantities_and_prices: List, cons_or_prod: str) -> List[Dict]:
        pass

    def bottom_up_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        # once the aggregator has made local arrangements, it publishes its needs (both in demand and in offer)
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside

        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        maximum_energy_charge = 0
        maximum_energy_discharge = 0

        # assess quantity for consumption and prod
        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge)
        quantity_available_per_option = self._assess_quantities_for_each_option(aggregator)
        quantity_to_affect = sum(quantity_available_per_option["consumption"].values()) - sum(quantity_available_per_option["production"].values())

        # affect available quantities
        quantities_and_prices = []
        if quantity_to_affect > 0:
            self._apply_priorities_exchanges(aggregator, quantity_to_affect, quantity_available_per_option, quantities_and_prices, "production")
        else:
            self._apply_priorities_exchanges(aggregator, quantity_to_affect, quantity_available_per_option, quantities_and_prices, "consumption")

        # send the demand to the other aggregator
        self._publish_needs(aggregator, quantities_and_prices)  # this function manages the appeals to the superior aggregator regarding capacity and efficiency

        return quantities_and_prices

    def _apply_priorities_distribution(self, aggregator: "Aggregator", min_price: float, max_price: float,
                                       sorted_demands,
                                       sorted_offers, energy_available_consumption: float,
                                       energy_available_production: float) -> Tuple:
        pass

    def top_down_phase(self, aggregator):  # after having exchanged with the exterior, the aggregator
        self._catalog.set(f"unwanted_delivery_cuts_{self.name}", 0)
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside

        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        maximum_energy_charge = 0
        maximum_energy_discharge = 0

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        sort_function = self._sort_function  # we choose a sort criteria

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge)

        # balance of the exchanges made with outside
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # assess quantity for consumption and prod
        quantity_available_per_option = self._assess_quantities_for_each_option(aggregator)

        # ##########################################################################################
        # balance of energy available

        energy_available_consumption = min(sum(quantity_available_per_option["consumption"].values()), sum(quantity_available_per_option["production"].values())) + energy_bought_outside
        energy_available_production = min(sum(quantity_available_per_option["consumption"].values()), sum(quantity_available_per_option["production"].values())) + energy_sold_outside

        # ##########################################################################################
        # distribution of energy

        # formulation of needs
        [sorted_demands, sorted_offers, sorted_storage] = self._sort_quantities(aggregator, sort_function)  # sort the quantities according to their prices
        # storage management
        sorted_demands = sorted_demands + sorted_storage
        sorted_offers = sorted_offers + sorted_storage
        if self._catalog.get('simulation_time') == 5900:
            print("toto")

        energy_bought_inside, energy_sold_inside, money_spent_inside, money_earned_inside = self._apply_priorities_distribution(aggregator, min_price, max_price, sorted_demands, sorted_offers, energy_available_consumption, energy_available_production)

        # ##########################################################################################
        # updates the balances
        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)

    def _limit_quantities(self, aggregator: "Aggregator",
                          minimum_energy_consumed: float, maximum_energy_consumed: float,
                          minimum_energy_produced: float, maximum_energy_produced: float,
                          maximum_energy_charge: float, maximum_energy_discharge: float):  # compute the minimum an maximum quantities of energy needed to be consumed and produced locally
        energy_stored = 0  # kWh
        energy_storable = 0  # kWh

        # quantities concerning devices
        for device_name in aggregator.devices:
            if isinstance(self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted"), dict):
                message = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")
            else:  # for dummy converters (with the same energy nature)
                for element in self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted"):
                    if element['aggregator'] == aggregator.name:
                        message = element
                        break
            energy_minimum = message["energy_minimum"]  # the minimum quantity of energy asked
            energy_nominal = message["energy_nominal"]  # the nominal quantity of energy asked
            energy_maximum = message["energy_maximum"]  # the maximum quantity of energy asked

            # balances
            if message["type"] == "storage" and energy_minimum < 0 < energy_maximum:  # it is both consumer and producer
                # storage
                maximum_energy_charge += energy_maximum
                maximum_energy_discharge -= energy_minimum
                energy_stored += message["state_of_charge"] * message["capacity"]
                energy_storable += (1 - message["state_of_charge"]) * message["capacity"]

            elif energy_maximum > 0:  # the device wants to consume energy
                if energy_nominal == energy_maximum:  # if it is urgent
                    minimum_energy_consumed += energy_maximum

                else:  # if there is a minimum
                    minimum_energy_consumed += energy_minimum
                maximum_energy_consumed += energy_maximum

            elif energy_maximum < 0:  # the device wants to sell energy
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

                elif energy_maximum < 0:  # the device wants to sell energy
                    if energy_nominal == energy_maximum:  # if it is urgent
                        minimum_energy_produced -= energy_maximum
                    else:
                        minimum_energy_produced -= energy_minimum
                    maximum_energy_produced -= energy_maximum

        # decision-making values recording
        self._catalog.set(f"{aggregator.name}.minimum_energy_consumption", minimum_energy_consumed)
        self._catalog.set(f"{aggregator.name}.maximum_energy_consumption", maximum_energy_consumed)
        self._catalog.set(f"{aggregator.name}.minimum_energy_production", minimum_energy_produced)
        self._catalog.set(f"{aggregator.name}.maximum_energy_production", maximum_energy_produced)
        self._catalog.set(f"{aggregator.name}.energy_stored", energy_stored)
        self._catalog.set(f"{aggregator.name}.energy_storable", energy_storable)

        return [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge]

    def _separe_quantities(self, aggregator: "Aggregator") -> List[List]:  # a function calculating the emergency associated, without sort, with devices and returning 2 sorted lists: one for the demands and one for the offers
        sorted_demands = []  # a list where the demands of energy are gathered
        sorted_offers = []  # a list where the offers of energy are gathered
        sorted_storage = []  # a list where the offers of storage are gathered

        for device_name in aggregator.devices:  # if there is missing energy
            if isinstance(self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted"), dict):
                Emin = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
                Enom = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_nominal"]
                Emax = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
                price = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["price"]
                device_type = self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted")["type"]
            else:
                for element in self._catalog.get(f"{device_name}.{aggregator.nature.name}.energy_wanted"):
                    if element['aggregator'] == aggregator.name:
                        Emin = element["energy_minimum"]
                        Enom = element["energy_nominal"]
                        Emax = element["energy_maximum"]
                        price = element["price"]
                        device_type = element["type"]
                        break

            if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                emergency = 1  # an indicator of how much the quantity is urgent
            else:
                emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

            if device_type == "storage" and Emin < 0 < Emax:  # it is both consumer and producer
                message = self._create_empty_sorted_lists()
                message["emergency"] = 0
                message["quantity"] = Emax
                message["quantity_min"] = Emin
                message["price"] = price
                message["name"] = device_name
                message["type"] = "storage"
                sorted_storage.append(message)
            elif Emax > 0:  # if the energy is strictly positive, it means that the device or the aggregator is asking for energy
                message = self._create_empty_sorted_lists()
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["quantity_min"] = Emin
                message["price"] = price
                message["name"] = device_name
                message["type"] = "consumption" if not device_type == "converter" else device_type
                sorted_demands.append(message)
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                message = self._create_empty_sorted_lists()
                message["emergency"] = emergency
                message["quantity"] = Emax
                message["quantity_min"] = Emin
                message["price"] = price
                message["name"] = device_name
                message["type"] = "production" if not device_type == "converter" else device_type
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
                    message = self._create_empty_sorted_lists()
                    message["emergency"] = emergency
                    message["quantity"] = Emax
                    message["quantity_min"] = Emin
                    message["price"] = price
                    message["name"] = subaggregator.name
                    sorted_demands.append(message)
                elif Emax < 0:  # if the energy is strictly negative, it means that the device or the aggregator is proposing energy
                    message = self._create_empty_sorted_lists()
                    message["emergency"] = emergency
                    message["quantity"] = Emax
                    message["quantity_min"] = Emin
                    message["price"] = price
                    message["name"] = subaggregator.name
                    sorted_offers.append(message)

        return [sorted_demands, sorted_offers, sorted_storage]

    # def multi_energy_balance_check(self, aggregator):  # todo verifier avec Timothé que ça ne pose pas de problème
    #     pass
