# This sheet describes a strategy always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from src.common.Strategy import Strategy


class WhenProfitablePartial(Strategy):

    def __init__(self, name, description):
        super().__init__(name, description)

        self._quantities_exchanged_internally = dict()  # this dict contains the quantities exchanged internally

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        # once the aggregator has made made local arrangements, it publishes its needs (both in demand and in offer)
        quantities_and_prices = []  # a list containing couples energy/prices

        self._get_quantities(aggregator)  # updates the quantities the aggregator has to manage

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(aggregator, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # ##########################################################################################
        # management of grid call
        # this aggregator can only ask two different quantities: the first for its urgent needs, associated to an infinite price
        # and another one, associated to non-urgent needs

        price = self._catalog.get(f"{aggregator.nature.name}.grid_buying_price")  # as the aggregator can't sell energy

        # calculate the quantities needed to fulfill its needs
        # make maximum two couples quantity/price: one for the urgent quantities and another one for the non-urgent quantities
        quantities_and_prices = self._prepare_quantitites_subaggregator(maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, price, quantities_and_prices)

        # as the aggregator cannot sell energy, we remove the negative quantities
        lines_to_remove = list()
        for i in range(len(quantities_and_prices) - 1):
            if quantities_and_prices[i][0] < 0:  # if the aggregator wants to sell energy
                lines_to_remove.append(i)  # we remove it form the list

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            quantities_and_prices.pop(line_index)

        # ##########################################################################################
        # publication of the needs

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

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        sort_function = self.get_emergency  # we choose a sort criteria

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(aggregator, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # balance of the exchanges made with outside
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(aggregator, sort_function)  # sort the quantities according to their prices

        # ##########################################################################################
        # balance of energy available

        energy_available_consumption = maximum_energy_produced + energy_bought_outside - energy_sold_outside  # the total energy available for consumptions
        energy_available_production = maximum_energy_consumed - energy_bought_outside + energy_sold_outside # the total energy available for productions

        # ##########################################################################################
        # distribution

        # first we ensure the urgent quantities will be satisfied
        # demand side
        [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside] = self._serve_emergency_demands(aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

        # offer side
        [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside] = self._serve_emergency_offers(aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)

        # then we distribute the remaining quantities equally to all demands and offers
        # distribution among consumptions
        [energy_available_consumption, money_earned_inside, energy_sold_inside] = self._distribute_consumption_partial_service(aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

        # distribution among productions
        [energy_available_production, money_spent_inside, energy_bought_inside] = self._distribute_production_partial_service(aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)

        # ##########################################################################################
        # updates the balances
        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside)



