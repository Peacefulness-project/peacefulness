# This sheet describes a strategy always refusing to trade with other
# It can correspond to the strategy of an island, for example
from src.common.Strategy import Strategy


class LightAutarkyEmergency(Strategy):

    def __init__(self):
        super().__init__("light_autarky_emergency_strategy", "buy/sell energy from/to outside only when it cannot serve urgent demands. During distribution, serves by decreasing emergency.")

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        energy_available_from_converters = 0  # the quantity of energy available thanks to converters

        # once the aggregator has made made local arrangements, it publishes its needs (both in demand and in offer)
        quantities_and_prices = []  # a list containing couples energy/prices

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        sort_function = self.get_price  # we choose a sort criteria

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(aggregator, sort_function)  # sort the quantities according to their prices

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters] = self._limit_quantities(aggregator, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters)

        quantities_and_prices = self._prepare_quantities_emergency_only(aggregator, sorted_demands, sorted_offers, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices)  # minimal quantities of energy need to balance the grid are asked

        self._publish_needs(aggregator, quantities_and_prices)  # this function manages the appeals to the superior aggregator regarding capacity and efficiency

    def distribute_remote_energy(self, aggregator):  # after having exchanged with the exterior, the aggregator
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
        energy_available_from_converters = 0  # the quantity of energy available thanks to converters

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        sort_function = self.get_emergency  # we choose a sort criteria

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters] = self._limit_quantities(aggregator, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters)

        # balance of the exchanges made with outside
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # ##########################################################################################
        # balance of energy available

        # calculating the energy available
        energy_available_consumption = maximum_energy_produced + energy_bought_outside  # the total energy available for consumptions
        energy_available_production = maximum_energy_consumed + energy_sold_outside  # the total energy available for productions

        # ##########################################################################################
        # distribution of energy

        if maximum_energy_produced <= minimum_energy_consumed or maximum_energy_consumed <= minimum_energy_produced:  # if there is no possibility to balance the grid
            # we consider that the gird falls
            # updates the balances
            self._catalog.set(f"{aggregator.name}.energy_bought", {"inside": 0, "outside": 0})
            self._catalog.set(f"{aggregator.name}.energy_sold", {"inside": 0, "outside": 0})

            self._catalog.set(f"{aggregator.name}.money_spent", {"inside": 0, "outside": 0})
            self._catalog.set(f"{aggregator.name}.money_earned", {"inside": 0, "outside": 0})

        else:  # if there is some possibility to balance the grid

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
        self._update_balances(aggregator, energy_bought_inside, 0, energy_sold_inside, 0, money_spent_inside, 0, money_earned_inside, 0)





