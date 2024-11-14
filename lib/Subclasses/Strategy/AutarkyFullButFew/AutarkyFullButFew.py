# This sheet describes a strategy always refusing to trade with other
# It can correspond to the strategy of an island, for example
from src.common.Strategy import Strategy
from typing import Callable


class AutarkyFullButFew(Strategy):
    def __init__(self, distribution_ranking_function: Callable):
        super().__init__(f"autarky_strategy_{distribution_ranking_function.__name__}", "Never try to buy/sell energy from/to outside. During distribution, serves totally a restricted number of devices according to the distribution ranking function.")

        self._distribution_ranking_function = distribution_ranking_function

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def bottom_up_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        quantities_and_prices = [aggregator.information_message()]

        return quantities_and_prices

    def top_down_phase(self, aggregator):  # after having exchanged with the exterior, the aggregator
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

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
        energy_difference = maximum_energy_consumed - maximum_energy_produced

        # ##########################################################################################
        # distribution of energy

        if maximum_energy_produced < minimum_energy_consumed or maximum_energy_consumed < minimum_energy_produced:  # if there is no possibility to balance the grid
            # we consider that the gird falls
            # updates the balances
            self._catalog.set(f"{aggregator.name}.energy_bought", {"inside": 0, "outside": 0})
            self._catalog.set(f"{aggregator.name}.energy_sold", {"inside": 0, "outside": 0})

            self._catalog.set(f"{aggregator.name}.money_spent", {"inside": 0, "outside": 0})
            self._catalog.set(f"{aggregator.name}.money_earned", {"inside": 0, "outside": 0})

        else:  # if there is some possibility to balance the grid

            # formulation of needs
            [sorted_demands, sorted_offers, sorted_storage] = self._sort_quantities(aggregator, self._distribution_ranking_function)  # sort the quantities according to their prices

            # determination of storage usage
            if minimum_energy_consumed > minimum_energy_produced:  # if there is a lack of local production...
                self._allocate_storage_to_discharge(maximum_energy_produced, maximum_energy_discharge,
                                                    sorted_offers, sorted_storage)
            elif minimum_energy_produced > minimum_energy_consumed:  # if there is a lack of local consumption...
                self._allocate_storage_to_charge(maximum_energy_consumed, maximum_energy_charge,
                                                 sorted_demands, sorted_storage)

            # demand side
            [sorted_demands, maximum_energy_produced, money_earned_inside, energy_sold_inside] = self._serve_emergency_demands(aggregator, max_price, sorted_demands, maximum_energy_produced, money_earned_inside, energy_sold_inside)

            # offer side
            [sorted_offers, maximum_energy_consumed, money_spent_inside, energy_bought_inside] = self._serve_emergency_offers(aggregator, min_price, sorted_offers, maximum_energy_consumed, money_spent_inside, energy_bought_inside)

            # then we distribute the remaining quantities according to our sort
            # distribution among consumptions
            [maximum_energy_produced, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(aggregator, max_price, sorted_demands, maximum_energy_produced, money_earned_inside, energy_sold_inside)

            # distribution among productions
            [maximum_energy_consumed, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(aggregator, min_price, sorted_offers, maximum_energy_consumed, money_spent_inside, energy_bought_inside)

        # ##########################################################################################
        # updates the balances
        self._update_balances(aggregator, energy_bought_inside, 0, energy_sold_inside, 0, money_spent_inside, 0, money_earned_inside, 0, maximum_energy_consumed, maximum_energy_produced)





