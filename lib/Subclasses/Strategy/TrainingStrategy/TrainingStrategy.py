# This strategy is the mother class for strategies able to apply succesively different options.
from src.common.Strategy import *
from typing import List, Dict, Tuple, Callable


class TrainingStrategy(Strategy):

    def __init__(self, priorities_consumption: Callable, priorities_production: Callable):
        super().__init__("training_strategy", "strategy with parameters used to train a ClusteringAndStrategy algorithm")
        self._priorities_consumption = priorities_consumption

        self._priorities_production = priorities_production

        self._sort_function = get_emergency  # laisser le choix: à déterminer par l'algo de ClusteringAndStrategy, je pense

        self._options_consumption: Callable = None
        self._options_production: Callable = None

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _get_priorities_consumption(self) -> List[str]:
        ordered_list = ["min"] + self._priorities_consumption(self)  # satisfying the minimum quantities is always, implicitly, the absolute priority
        return ordered_list

    def _get_priorities_production(self) -> List[str]:
        ordered_list = ["min"] + self._priorities_production(self)  # satisfying the minimum quantities is always, implicitly, the absolute priority
        return ordered_list

    def _asses_quantities_for_each_option(self, aggregator: "Aggregator") -> Dict:
        pass

    def _apply_priorities_exchanges(self, aggregaor: "Aggregator", quantity_to_affect: float,
                                    quantity_available_per_option: Dict) -> List[Dict]:
        pass

    def bottom_up_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        # once the aggregator has made local arrangements, it publishes its needs (both in demand and in offer)
        quantities_and_prices = []  # a list containing couples energy/prices

        # assess quantity for consumption and prod
        quantity_available_per_option = self._asses_quantities_for_each_option(aggregator)

        quantity_to_affect = min(
            sum(quantity_available_per_option["consumption"].values()),
            sum(quantity_available_per_option["production"].values())
        )

        # affect available quantities
        quantities_and_prices = self._apply_priorities_exchanges(aggregator, quantity_to_affect, quantity_available_per_option)
        self._publish_needs(aggregator, quantities_and_prices)  # this function manages the appeals to the superior aggregator regarding capacity and efficiency

        return quantities_and_prices

    def _apply_priorities_distribution(self, aggregator: "Aggregator", min_price: float, max_price: float,
                                       sorted_demands,
                                       sorted_offers, energy_available_consumption: float,
                                       energy_available_production: float) -> Tuple:
        pass

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

        sort_function = self._sort_function  # we choose a sort criteria

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

        energy_bought_inside, energy_sold_inside, money_spent_inside, money_earned_inside = self._apply_priorities_distribution(aggregator, min_price, max_price, sorted_demands, sorted_offers, energy_available_consumption, energy_available_production)

        # ##########################################################################################
        # updates the balances
        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside, maximum_energy_consumed, maximum_energy_produced)


