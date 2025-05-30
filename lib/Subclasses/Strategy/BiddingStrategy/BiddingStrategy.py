# This sheet describes a strategy always refusing to trade with other
# It can correspond to the strategy of an island, for example
from src.common.Strategy import Strategy
from typing import Callable, Dict, List


class BiddingStrategy(Strategy):

    def __init__(self, name: float, distribution_ranking_function: Callable):
        super().__init__(f"bidding_strategy_{name}", "makes bids when it comes to exchanging energy with outside.")

        self._distribution_ranking_function = distribution_ranking_function

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def create_bids(self, minimum_energy_consumed: float, maximum_energy_consumed: float, minimum_energy_produced: float, maximum_energy_produced: float, maximum_energy_charge: float, maximum_energy_discharge: float) -> List[Dict]:
        pass

    def bottom_up_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        maximum_energy_charge = 0  # the maximum quantity of energy acceptable by storage charge
        maximum_energy_discharge = 0  # the maximum quantity of energy available from storage discharge

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge] = \
            self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge)

        quantities_and_prices = self.create_bids(minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced,
                                                                        maximum_energy_charge, maximum_energy_discharge)  # storage

        self._publish_needs(aggregator, quantities_and_prices)  # this function manages the appeals to the superior aggregator regarding capacity and efficiency

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
        maximum_energy_charge = 0  # the maximum quantity of energy acceptable by storage charge
        maximum_energy_discharge = 0  # the maximum quantity of energy available from storage discharge

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge] = self._limit_quantities(aggregator, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, maximum_energy_charge, maximum_energy_discharge)

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
        [sorted_demands, sorted_offers, sorted_storage] = self._sort_quantities(aggregator, self._distribution_ranking_function)  # sort the quantities according to their prices

        # determination of storage usage
        if minimum_energy_consumed > minimum_energy_produced:  # if there is a lack of local production...
            self._allocate_storage_to_discharge(energy_available_production, maximum_energy_discharge,
                                                sorted_offers, sorted_storage)
        elif minimum_energy_produced > minimum_energy_consumed:  # if there is a lack of local consumption...
            self._allocate_storage_to_charge(energy_available_consumption, maximum_energy_charge,
                                             sorted_demands, sorted_storage)

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





