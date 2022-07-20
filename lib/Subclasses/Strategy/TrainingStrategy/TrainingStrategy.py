# This sheet describes a strategy always refusing to trade with other
# It can correspond to the strategy of an island, for example
from src.common.Strategy import Strategy
from typing import List, Dict, Tuple
import pandas as pd


class TrainingStrategy(Strategy):

    def __init__(self, priorities_consumption: List[str], priorities_production: List[str]):
        super().__init__("training_strategy", "strategy with parameters used to train a ML algorithm")

        index = ["min", "soft_DSM_conso", "hard_DSM_conso", "buy_outside_emergency", "store"]
        columns = ["assess", "exchange", "distribute"]
        data = [[self._assess_min_conso, self._exchanges_min_conso, self._serve_emergency_demands],
                [self._assess_soft_DSM_conso, self._exchanges_soft_DSM_conso, self._distribution_soft_DSM_conso],
                [self._assess_hard_DSM_conso, self.exchanges_hard_DSM_conso, self._distribution_hard_DSM_conso],
                [self._assess_buy_outside, self._exchanges_buy_outside, self._distribution_buy_outside],
                [self._assess_storage, self._exchanges_storage, self._distribution_storage]
                ]
        self._priorities_management_consumption = pd.DataFrame(index=index, columns=columns, data=data)

        index = ["min", "soft_DSM_prod", "hard_DSM_prod", "sell_outside_emergency", "unstore"]
        columns = ["assess", "exchange", "distribute"]
        data = [[self._assess_min_prod, self._exchanges_min_conso, self._serve_emergency_offers],
                [self._assess_soft_DSM_prod, self._exchanges_soft_DSM_prod, self._distribution_soft_DSM_prod],  # TODO: mettre les bonnes méthodes quand elles seront prêtes
                [self._assess_hard_DSM_prod, self.exchanges_hard_DSM_prod, self._distribution_hard_DSM_prod],
                [self._assess_sell_outside, self._exchanges_sell_outside, self._distribution_sell_outside],
                [self._assess_unstorage, self._exchanges_unstorage, self._distribution_unstorage]
                ]
        self._priorities_management_production = pd.DataFrame(index=index, columns=columns, data=data)

        self._priorities_consumption = ["min"] + priorities_consumption  # satisfying the minimum quantities is always, implicitly, the absolute priority
        self._priorities_production = ["min"] + priorities_production  # satisfying the minimum quantities is always, implicitly, the absolute priority

        self._sort_function = self.get_emergency  # TODO: à faire en fonction du critère de performance choisi

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def bottom_up_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced

        # once the aggregator has made made local arrangements, it publishes its needs (both in demand and in offer)
        quantities_and_prices = []  # a list containing couples energy/prices

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        # assess quantity for consumption and prod
        quantity_available_per_option = self._asses_quantities_for_each_option(aggregator)

        quantity_to_affect = min(
            sum(quantity_available_per_option["consumption"].values()),
            sum(quantity_available_per_option["production"].values())
        )

        # affect available quantities
        quantities_prices = self._apply_priorities_exchanges(aggregator, quantity_to_affect, quantity_available_per_option)

        return quantities_and_prices

    def top_down_phase(self, aggregator):  # after having exchanged with the exterior, the aggregator
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside

        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        sort_function = self.get_emergency  # we choose a sort criteria

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # balance of the exchanges made with outside
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # ##########################################################################################
        # balance of energy available

        # calculating the energy available
        energy_available_consumption = maximum_energy_produced + energy_bought_outside  # the total energy available for consumptions
        energy_available_production = maximum_energy_consumed + energy_sold_outside  # the total energy available for productions
        # print(energy_available_consumption, energy_available_production)

        # ##########################################################################################
        # distribution of energy

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(aggregator, sort_function)  # sort the quantities according to their prices

        energy_bought_inside, energy_sold_inside, money_spent_inside, money_earned_inside = self._apply_priorities_distribution(aggregator)

        # ##########################################################################################
        # updates the balances
        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)

    # ##########################################################################################
    # Priorities functions
    # ##########################################################################################

    def _asses_quantities_for_each_option(self, aggregator: "Aggregator"):
        [demands, offers] = self._sort_quantities(aggregator, self._sort_function)
        quantity_per_option = {"consumption": {}, "production": {}}

        for priority in self._priorities_consumption:
            quantity_per_option["consumption"][priority] = self._priorities_management_consumption.loc[priority]["assess"](aggregator, demands)
        for priority in self._priorities_production:
            quantity_per_option["production"][priority] = self._priorities_management_production.loc[priority]["assess"](aggregator, offers)
        print(quantity_per_option)

        # balances update
        min_cons = quantity_per_option["consumption"]["min"]
        min_prod = quantity_per_option["production"]["min"]
        if "store" in self._priorities_consumption:
            energy_storable = quantity_per_option["consumption"]["store"]
        else:
            energy_storable = 0
        if "unstore" in self._priorities_production:
            energy_unstorable = quantity_per_option["production"]["unstore"]
        else:
            energy_unstorable = 0
        max_cons = sum(quantity_per_option["consumption"].values()) - min_cons - energy_storable
        max_prod = sum(quantity_per_option["production"].values()) - min_prod - energy_unstorable
        self._catalog.set(f"{aggregator.name}.minimum_energy_consumption", min_cons)
        self._catalog.set(f"{aggregator.name}.maximum_energy_consumption", max_cons)
        self._catalog.set(f"{aggregator.name}.minimum_energy_production", min_prod)
        self._catalog.set(f"{aggregator.name}.maximum_energy_production", max_prod)

        return quantity_per_option

    def _apply_priorities_exchanges(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_per_option: Dict) -> List[Dict]:
        quantities_and_price = []
        for priority in self._priorities_consumption:
            quantity_available = quantity_available_per_option["consumption"][priority]
            quantity_affected, quantities_and_price = self._priorities_management_consumption.loc[priority]["exchange"](aggregator, quantity_to_affect, quantity_available, quantities_and_price)
            quantity_to_affect -= quantity_affected
        for priority in self._priorities_production:
            quantity_available = quantity_available_per_option["production"][priority]
            quantity_affected, quantities_and_price = self._priorities_management_production.loc[priority]["exchange"](aggregator, quantity_to_affect, quantity_available, quantities_and_price)
            quantity_to_affect -= quantity_affected

        return quantities_and_price

    def _apply_priorities_distribution(self, aggregator: "Aggregator", energy_available_consumption: float, enegy_available_production: float):
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside



        return energy_bought_inside, energy_sold_inside, money_spent_inside, money_earned_inside

    # ################################################################################################################
    # consumption side
    # min

    def _assess_min_conso(self, aggregator: "Aggregator", demands: List[Dict]) -> float:
        quantity_for_this_option = 0

        for demand in demands:
            quantity_for_this_option += demand["quantity_min"]

        return quantity_for_this_option

    def _exchanges_min_conso(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
        return quantity_to_affect, quantities_and_prices

    # no specific function for distribution, the canonical one is used

    # soft DSM

    def _assess_soft_DSM_conso(self, aggregator: "Aggregator", demands: List[Dict]) -> float:
        quantity_for_this_option = 0

        for demand in demands:
            if demand["emergency"] <= 0.9 and demand["type"] != "storage":
                quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

        return quantity_for_this_option

    def _exchanges_soft_DSM_conso(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
        return quantity_to_affect, quantities_and_prices

    def _distribution_soft_DSM_conso(self, aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
        i = 0

        if len(sorted_demands) >= 1:  # if there are offers
            while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
                if sorted_demands[i]["emergency"] <= 0.9 and sorted_demands[i]["type"] != "storage":
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
            if sorted_demands[i]["quantity"] and sorted_demands[i]["emergency"] <= 0.9 and sorted_demands[i]["type"] != "storage":  # if the demand really exists
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
                energy_available_consumption -= energy

        return energy_available_consumption, money_earned_inside, energy_sold_inside

    # hard DSM

    def _assess_hard_DSM_conso(self, aggregator: "Aggregator", demands: List[Dict]) -> float:
        quantity_for_this_option = 0

        for demand in demands:
            if demand["emergency"] > 0.9 and demand["type"] != "storage":
                quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

        return quantity_for_this_option

    def exchanges_hard_DSM_conso(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
        return quantity_to_affect, quantities_and_prices

    def _distribution_hard_DSM_conso(self, aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
        i = 0

        if len(sorted_demands) >= 1:  # if there are offers
            while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
                if sorted_demands[i]["emergency"] > 0.9 and sorted_demands[i]["type"] != "storage":
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
            if sorted_demands[i]["quantity"] and sorted_demands[i]["emergency"] > 0.9 and sorted_demands[i]["type"] != "storage":  # if the demand really exists
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

                self._catalog.set(f"{name}.{aggregator.nature.name}.energy_accorded",
                                  quantities_given)  # it is served

                money_earned_inside += energy * price  # money earned by selling energy to the device
                energy_sold_inside += energy  # the absolute value of energy sold inside
                energy_available_consumption -= energy

        return energy_available_consumption, money_earned_inside, energy_sold_inside

    # outside energy

    def _assess_buy_outside(self, aggregator: "Aggregator", demands: List[Dict]) -> float:
        quantity_for_this_option = aggregator.capacity["buying"] / aggregator.efficiency

        return quantity_for_this_option

    def _exchanges_buy_outside(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        quantity_remaining = max(0, quantity_to_affect - quantity_available_for_this_option)
        quantity_bought = quantity_to_affect - quantity_remaining

        message["energy_minimum"] = quantity_bought
        message["energy_nominal"] = quantity_bought
        message["energy_maximum"] = quantity_bought

        message = self._publish_needs(aggregator, [message])
        quantities_and_prices.append(message)

        return quantity_remaining, quantities_and_prices

    def _distribution_buy_outside(self, aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
        return energy_available_consumption, money_earned_inside, energy_sold_inside

    # store

    def _assess_storage(self, aggregator: "Aggregator", demands: List[Dict]) -> float:  # TODO: séparer stockage du reste (et corrgier plus haut)
        quantity_for_this_option = 0

        for demand in demands:
            if demand["type"] == "storage":
                quantity_for_this_option += demand["quantity"] - demand["quantity_min"]

        return quantity_for_this_option

    def _exchanges_storage(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        quantity_to_affect = max(0, quantity_to_affect - quantity_available_for_this_option)
        return quantity_to_affect, quantities_and_prices

    def _distribution_storage(self, aggregator: "Aggregator", max_price: float, sorted_demands: List[Dict], energy_available_consumption: float, money_earned_inside: float, energy_sold_inside: float):
        i = 0

        if len(sorted_demands) >= 1:  # if there are offers
            while energy_available_consumption > sorted_demands[i]["quantity"] and i < len(sorted_demands) - 1:  # as long as there is energy available
                if sorted_demands[i]["type"] == "storage":
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
            if sorted_demands[i]["quantity"] and sorted_demands[i][
                "type"] != "storage":  # if the demand really exists
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
                energy_available_consumption -= energy

        return energy_available_consumption, money_earned_inside, energy_sold_inside

    # ################################################################################################################
    # production
    # min

    def _assess_min_prod(self, aggregator: "Aggregator", offers: List[Dict]) -> float:
        quantity_for_this_option = 0

        for demand in offers:
            quantity_for_this_option -= demand["quantity_min"]

        return quantity_for_this_option

    def _exchanges_min_prod(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
        return quantity_to_affect, quantities_and_prices

    # no specific function for distribution, the canoncial one is used

    # soft DSM

    def _assess_soft_DSM_prod(self, aggregator: "Aggregator", offers: List[Dict]) -> float:
        quantity_for_this_option = 0

        for demand in offers:
            if demand["emergency"] <= 0.9 and demand["type"] != "storage":
                quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

        return quantity_for_this_option

    def _exchanges_soft_DSM_prod(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
        return quantity_to_affect, quantities_and_prices

    def _distribution_soft_DSM_prod(self, aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
        i = 0

        if len(sorted_offers) >= 1:  # if there are offers
            while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
                if sorted_offers[i]["emergency"] <= 0.9 and sorted_offers[i]["type"] != "storage":
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
            if sorted_offers[i]["quantity"] and sorted_offers[i]["emergency"] <= 0.9 and sorted_offers[i]["type"] != "storage":  # if the demand really exists
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

        return energy_available_production, money_spent_inside, energy_bought_inside

    # hard DSM

    def _assess_hard_DSM_prod(self, aggregator: "Aggregator", offers: List[Dict]) -> float:
        quantity_for_this_option = 0

        for demand in offers:
            if demand["emergency"] > 0.9 and demand["type"] != "storage":
                quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

        return quantity_for_this_option

    def exchanges_hard_DSM_prod(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
        return quantity_to_affect, quantities_and_prices

    def _distribution_hard_DSM_prod(self, aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
        i = 0

        if len(sorted_offers) >= 1:  # if there are offers
            while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
                if sorted_offers[i]["emergency"] > 0.9 and sorted_offers[i]["type"] != "storage":
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
            if sorted_offers[i]["quantity"] and sorted_offers[i]["emergency"] > 0.9 and sorted_offers[i]["type"] != "storage":  # if the demand really exists
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

        return energy_available_production, money_spent_inside, energy_bought_inside

    # outside energy

    def _assess_sell_outside(self, aggregator: "Aggregator", offers: List[Dict]) -> float:
        quantity_for_this_option = aggregator.capacity["selling"] * aggregator.efficiency

        return quantity_for_this_option

    def _exchanges_sell_outside(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        quantity_remaining = max(0, quantity_to_affect - quantity_available_for_this_option)
        quantity_sold = quantity_to_affect - quantity_remaining

        message["energy_minimum"] = - quantity_sold
        message["energy_nominal"] = - quantity_sold
        message["energy_maximum"] = - quantity_sold

        message = self._publish_needs(aggregator, [message])
        quantities_and_prices.append(message)

        return quantity_remaining, quantities_and_prices

    def _distribution_sell_outside(self, aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
        return energy_available_production, money_spent_inside, energy_bought_inside

    # unstore

    def _assess_unstorage(self, aggregator: "Aggregator", offers: List[Dict]) -> float:  # TODO: séparer stockage du reste (et corrgier plus haut)
        quantity_for_this_option = 0

        for demand in offers:
            if demand["type"] == "storage":
                quantity_for_this_option -= demand["quantity"] - demand["quantity_min"]

        return quantity_for_this_option

    def _exchanges_unstorage(self, aggregator: "Aggregator", quantity_to_affect: float, quantity_available_for_this_option: float, quantities_and_prices: List[Dict]) -> Tuple:
        quantity_to_affect = - max(0, quantity_to_affect - quantity_available_for_this_option)
        return quantity_to_affect, quantities_and_prices

    def _distribution_unstorage(self, aggregator: "Aggregator", min_price: float, sorted_offers: List[Dict], energy_available_production: float, money_spent_inside: float, energy_bought_inside: float):
        i = 0

        if len(sorted_offers) >= 1:  # if there are offers
            while energy_available_production >= - sorted_offers[i]["quantity"] and i < len(sorted_offers) - 1:  # as long as there is energy available
                if sorted_offers[i]["type"] == "storage":
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
            if sorted_offers[i]["quantity"] and sorted_offers[i]["type"] == "storage":  # if the demand really exists
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

        return energy_available_production, money_spent_inside, energy_bought_inside

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def _device_is_storage(self, device_name):
        device_type = self._catalog.get("dictionaries")['devices'][device_name].type
        if device_type == "storage":
            return True
        else:
            return False
