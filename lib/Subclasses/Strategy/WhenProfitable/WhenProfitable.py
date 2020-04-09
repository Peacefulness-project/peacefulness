# This sheet describes a strategy always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from src.common.Strategy import Strategy


class WhenProfitable(Strategy):

    def __init__(self):
        super().__init__("when_profitable_strategy", "Distributes energy only when the aggregator makes a profit.")

        self._quantities_exchanged_internally = dict()  # this dict contains the quantities exchanged internally

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, aggregator):  # before communicating with the exterior, the aggregator makes its local balances
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced
        energy_available_from_converters = 0  # the quantity of energy available thanks to converters

        self._quantities_exchanged_internally[aggregator.name] = {"quantity": 0, "price": 0}  # reinitialization of the quantities exchanged internally

        # once the aggregator has made made local arrangements, it publishes its needs (both in demand and in offer)
        quantities_exchanged = 0  # the quantity of energy exchanged internally allowed by the strategy
        quantities_and_prices = {}  # a list containing couples energy/prices

        [min_price, max_price] = self._limit_prices(aggregator)  # min and max prices allowed

        sort_function = self.get_price  # we choose a sort criteria

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(aggregator, sort_function)  # sort the quantities according to their prices

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters] = self._limit_quantities(aggregator, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters)

        # initialization of prices:
        if sorted_demands:  # if there is at least one demand
            buying_price = min(sorted_demands[0]["price"], max_price)  # maximum price given by consumers
        else:
            buying_price = 0

        if sorted_offers:  # if there is at least one offer
            selling_price = max(sorted_offers[0]["price"], min_price)  # minimum price given by producers
        else:
            selling_price = 0

        final_price = (buying_price + selling_price) / 2  # initialization of the final price

        [quantities_exchanged, quantities_and_prices] = self._prepare_quantities_when_profitable(aggregator, sorted_demands, sorted_offers, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices, buying_price, selling_price, final_price)

        self._quantities_exchanged_internally[aggregator.name] = [quantities_exchanged, final_price]  # we store this value for the descendant phase

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

        sort_function = self.get_price  # we choose a sort criteria

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the aggregator

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters] = self._limit_quantities(aggregator, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced, energy_available_from_converters)

        # balance of the exchanges made with outside
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(aggregator, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(aggregator, sort_function)  # sort the quantities according to their prices

        # ##########################################################################################
        # balance of energy available

        # calculating the energy available
        energy_available_consumption = self._quantities_exchanged_internally[aggregator.name]["quantity"] + energy_bought_outside  # the total energy available for consumptions
        energy_available_production = self._quantities_exchanged_internally[aggregator.name]["quantity"] + energy_sold_outside  # the total energy available for productions

        # ##########################################################################################
        # distribution

        # first we ensure the urgent quantities will be satisfied
        # demand side
        [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside] = self._serve_emergency_demands(aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

        # offer side
        [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside] = self._serve_emergency_offers(aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)

        # then we distribute the remaining quantities according to our sort
        # distribution among consumptions
        [energy_available_consumption, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(aggregator, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

        # distribution among productions
        [energy_available_production, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(aggregator, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)

        # updates the balances
        self._update_balances(aggregator, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside)



