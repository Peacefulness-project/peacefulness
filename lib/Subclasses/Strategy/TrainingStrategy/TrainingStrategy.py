# This sheet describes a strategy always refusing to trade with other
# It can correspond to the strategy of an island, for example
from src.common.Strategy import Strategy
from typing import List, Dict
import pandas as pd


class TrainingStrategy(Strategy):

    def __init__(self, priorities_consumption: List[str], priorities_production: List[str]):
        super().__init__("training_strategy", "strategy with parameters used to train a ML algorithm")

        index = ["soft_DSM_conso", "hard_DSM_conso", "buy_outside_emergency", "store"]
        columns = ["assess", "exchange", "distribute"]
        data = [[self._assess_soft_DSM_conso, self._exchanges_soft_DSM_conso, self._distribution_soft_DSM_conso],
                [self._assess_hard_DSM_conso, self.exchanges_hard_DSM_conso, self._distribution_hard_DSM_conso],
                [self._assess_buy_outside, self._exchanges_buy_outside, self._distribution_buy_outside],
                [self._assess_storage, self._exchanges_storage, self._distribution_storage]
                ]
        self._priorities_management_consumption = pd.DataFrame(index=index, columns=columns, data=data)

        index = ["soft_DSM_prod", "hard_DSM_prod", "sell_outside_emergency", "unstore"]
        columns = ["assess", "exchange", "distribute"]
        data = [[self._assess_soft_DSM_conso, self._exchanges_soft_DSM_conso, self._distribution_soft_DSM_conso],  # TODO: mettre les bonnes méthodes quand elles seront prêtes
                [self._assess_hard_DSM_conso, self.exchanges_hard_DSM_conso, self._distribution_hard_DSM_conso],
                [self._assess_buy_outside, self._exchanges_buy_outside, self._distribution_buy_outside],
                [self._assess_storage, self._exchanges_storage, self._distribution_storage]
                ]
        self._priorities_management_production = pd.DataFrame(index=index, columns=columns, data=data)

        self._priorities_consumption = priorities_consumption
        self._priorities_production = priorities_production

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
        minimum_energy_consumption, maximum_energy_consumption, minimum_energy_production, maximum_energy_production = self._asses_quantities_available(aggregator)

        # affect available quantities
        quantities_prices = self._apply_priorities_exchanges()

        return quantities_and_prices

    def top_down_phase(self, aggregator):  # after having exchanged with the exterior, the aggregator
        energy_bought_outside = 0  # the absolute value of energy bought outside
        energy_sold_outside = 0  # the absolute value of energy sold outside
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_outside = 0  # the absolute value of money earned outside
        money_spent_outside = 0  # the absolute value of money spent outside
        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

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

        # ##########################################################################################
        # distribution of energy

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(aggregator, sort_function)  # sort the quantities according to their prices

        # demand side
        [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside] = self._serve_emergency_demands(aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

        # offer side
        [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside] = self._serve_emergency_offers(aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)

        # then we distribute the remaining quantities according to our sort
        # distribution among consumptions
        [energy_available_consumption, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

        # distribution among productions
        [energy_available_production, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)

        # ##########################################################################################
        # updates the balances
        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)

    # ##########################################################################################
    # Priorities functions
    # ##########################################################################################

    def _asses_quantities_available(self, aggregator: "Aggregator"):
        minimum_energy_consumption = 0
        maximum_energy_consumption = 0
        minimum_energy_production = 0
        maximum_energy_production = 0
        for priority in self._priorities_consumption:
            minimum_energy_consumption, maximum_energy_consumption = self._priorities_management_consumption[priority](aggregator)
        for priority in self._priorities_production:
            minimum_energy_production, maximum_energy_production = self._priorities_management_production[priority](aggregator)

        return minimum_energy_consumption, maximum_energy_consumption, minimum_energy_production, maximum_energy_production

    def apply_priorities_distribution(self, aggregator: "Aggregator", quantity: float, sorted_demands: List[Dict], sorted_offers: List[Dict]):
        for priority in self._priorities:
            quantity_affected, quantities_and_price = self._actions_means_function[priority](aggregator, quantity, sorted_demands, sorted_offers)
            quantity -= quantity_affected

    def _apply_priorities_exchanges(self):
        pass

    # consumption side
    # soft DSM

    def _assess_soft_DSM_conso(self):
        pass

    def _exchanges_soft_DSM_conso(self, aggregator: "Aggregator", quantity: float, sorted_demands: List[Dict], sorted_offers: List[Dict]):
        # relevant_demands = []
        # for demand in sorted_demands:
        #     if demand["emergency"] < 0.9:
        #         relevant_demands.append(demand)
        #
        # return quantity, {}
        pass

    def _distribution_soft_DSM_conso(self):
        pass

    # hard DSM

    def _assess_hard_DSM_conso(self):
        pass

    def exchanges_hard_DSM_conso(self, aggregator: "Aggregator", quantity: float, sorted_demands: List[Dict], sorted_offers: List[Dict]):
        # for demand in sorted_demands:
        #     if demand["emergency"] >= 0.9:
        #
        # return quantity, {}
        pass

    def _distribution_hard_DSM_conso(self):
        pass

    # outside energy

    def _assess_buy_outside(self):
        pass

    def _exchanges_buy_outside(self, aggregator, quantity):
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}

        message["energy_minimum"] = quantity
        message["energy_nominal"] = quantity
        message["energy_maximum"] = quantity
        
        message = self._publish_needs(aggregator, message)

        return quantity, message

    def _distribution_buy_outside(self):
        pass

    # def buy_outside_energy_shiftable(self, aggregator, quantity):  # maybe added later
    #     message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
    #
    #     message["energy_minimum"] = 0
    #     message["energy_nominal"] = 0
    #     message["energy_maximum"] = quantity
    #
    #     message = self._publish_needs(aggregator, message)
    #
    #     return quantity, message

    # store

    def _assess_storage(self, aggregator, quantity):
        pass

    def _exchanges_storage(self, aggregator, quantity):
        pass

    def _distribution_storage(self):
        pass

    # production

    def sell_to_outside_emergency(self, aggregator, quantity):
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}

        message["energy_minimum"] = - quantity
        message["energy_nominal"] = - quantity
        message["energy_maximum"] = - quantity

        message = self._publish_needs(aggregator, message)

        return quantity, message

    # def sell_to_outside_shiftable(self, aggregator, quantity):  # maybe added later
    #     message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
    #
    #     message["energy_minimum"] = 0
    #     message["energy_nominal"] = 0
    #     message["energy_maximum"] = - quantity
    #
    #     message = self._publish_needs(aggregator, message)
    #
    #     return quantity, message

    def unstore(self, aggregator, quantity):
        pass
