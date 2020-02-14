# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign

from math import inf


class WhenProfitable(Supervisor):

    def __init__(self, name, description):
        super().__init__(name, description)

        self._quantities_exchanged_internally = dict()  # this dict contains the quantities exchanged internally

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced

        self._quantities_exchanged_internally[cluster.name] = [0, 0]  # reinitialization of the quantities exchanged internally

        # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        quantities_exchanged = 0  # the quantity of energy exchanged internally allowed by the supervisor
        quantities_and_prices = []  # a list containing couples energy/prices

        [min_price, max_price] = self._limit_prices(cluster)  # min and max prices allowed

        sort_function = self.get_price  # we choose a sort criteria

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(cluster, sort_function)  # sort the quantities according to their prices

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the cluster

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(cluster, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # initialization of prices:
        buying_price = min(sorted_demands[0][2], max_price)  # maximum price given by consumers
        selling_price = max(sorted_offers[0][2], min_price)  # minimum price given by producers
        final_price = (buying_price + selling_price) / 2  # initialization of the final price

        [quantities_exchanged, quantities_and_prices] = self._prepare_quantities_when_profitable(cluster, sorted_demands, sorted_offers, maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, quantities_and_prices, buying_price, selling_price, final_price)

        self._quantities_exchanged_internally[cluster.name] = [quantities_exchanged, final_price]  # we store this value for the descendant phase

        self._publish_needs(cluster, quantities_and_prices)  # this function manages the appeals to the superior cluster regarding capacity and efficiency

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
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

        [min_price, max_price] = self._limit_prices(cluster)  # min and max prices allowed

        sort_function = self.get_price  # we choose a sort criteria

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the cluster

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(cluster, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # balance of the exchanges made with outside
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(cluster, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(cluster, sort_function)  # sort the quantities according to their prices

        # ##########################################################################################
        # balance of energy available

        # calculating the energy available
        energy_available_consumption = self._quantities_exchanged_internally[cluster.name][0] + energy_bought_outside  # the total energy available for consumptions
        energy_available_production = self._quantities_exchanged_internally[cluster.name][0] + energy_sold_outside  # the total energy available for productions

        # ##########################################################################################
        # distribution

        # first we ensure the urgent quantities will be satisfied
        # demand side
        [sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside] = self._serve_emergency_demands(cluster, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

        # offer side
        [sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside] = self._serve_emergency_offers(cluster, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)

        # then we distribute the remaining quantities according to our sort
        # distribution among consumptions
        [energy_available_consumption, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(cluster, max_price, sorted_demands, energy_available_consumption, money_earned_inside, energy_sold_inside)

        # distribution among productions
        [energy_available_production, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(cluster, min_price, sorted_offers, energy_available_production, money_spent_inside, energy_bought_inside)

        # updates the balances
        self._update_balances(cluster, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside)


user_classes_dictionary[f"{WhenProfitable.__name__}"] = WhenProfitable

