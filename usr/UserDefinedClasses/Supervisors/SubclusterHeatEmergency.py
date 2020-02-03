# This sheet describes a supervisor always wanting to buy all the energy lacking and to sell all the energy available
# It corresponds to the current "strategy" in France and can be used as a reference.
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import sign

from math import inf


class SubclusterHeatEmergency(Supervisor):

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

        [min_price, max_price] = self._limit_prices(cluster)  # min and max prices allowed

        # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        quantities_and_prices = []  # a list containing couples energy/prices

        self._get_quantities(cluster)  # updates the quantities the cluster has to manage

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the cluster

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(cluster, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # ##########################################################################################
        # management of grid call
        # this cluster can only ask two different quantities: the first for its urgent needs, associated to an infinite price
        # and another one, associated to non-urgent needs

        price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")  # as the cluster can't sell energy

        # calculate the quantities needed to fulfill its needs
        # make maximum two couples quantity/price: one for the urgent quantities and another one for the non-urgent quantities
        quantities_and_prices = self._prepare_quantitites_subcluster(maximum_energy_produced, maximum_energy_consumed, minimum_energy_produced, minimum_energy_consumed, price, quantities_and_prices)

        # as the cluster cannot sell energy, we remove the negative quantities
        lines_to_remove = list()
        for i in range(len(quantities_and_prices) - 1):
            if quantities_and_prices[i][0] < 0:  # if the cluster wants to sell energy
                lines_to_remove.append(i)  # we remove it form the list

        lines_to_remove.reverse()  # we reverse the list, otherwise the indices will move during the deletion

        for line_index in lines_to_remove:  # removing the already served elements
            quantities_and_prices.pop(line_index)

        # ##########################################################################################
        # publication of the needs

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

        sort_function = self.get_emergency  # we choose a sort criteria

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the cluster

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(cluster, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # balance of the exchanges made with outside
        [money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside] = self._exchanges_balance(cluster, money_spent_outside, energy_bought_outside, money_earned_outside, energy_sold_outside)

        # formulation of needs
        [sorted_demands, sorted_offers] = self._sort_quantities(cluster, sort_function)  # sort the quantities according to their prices

        # ##########################################################################################
        # balance of energy available

        energy_available_consumption = maximum_energy_produced + energy_bought_outside - energy_sold_outside  # the total energy available for consumptions
        energy_available_production = maximum_energy_consumed - energy_bought_outside + energy_sold_outside # the total energy available for productions

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

        print(energy_bought_outside - energy_sold_outside + energy_bought_inside - energy_sold_inside)  # must be null

        # ##########################################################################################
        # updates the balances
        self._update_balances(cluster, energy_bought_inside, energy_bought_outside, energy_sold_inside, energy_sold_outside, money_spent_inside, money_spent_outside, money_earned_inside, money_earned_outside)


user_classes_dictionary[f"{SubclusterHeatEmergency.__name__}"] = SubclusterHeatEmergency

