# This sheet describes a supervisor always refusing to trade with other
# It can correspond to the supervisor of an island, for example
from common.Supervisor import Supervisor
from tools.UserClassesDictionary import user_classes_dictionary

from math import inf


class AutarkyRevenues(Supervisor):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        self._catalog.set(f"{cluster.name}.quantities_asked", [[0, 0]])  # always refuses to exchange with outside

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        energy_bought_inside = 0  # the absolute value of energy bought inside
        energy_sold_inside = 0  # the absolute value of energy sold inside

        money_earned_inside = 0  # the absolute value of money earned inside
        money_spent_inside = 0  # the absolute value of money spent inside

        minimum_energy_consumed = 0  # the minimum quantity of energy needed to be consumed
        minimum_energy_produced = 0  # the minimum quantity of energy needed to be produced
        maximum_energy_consumed = 0  # the maximum quantity of energy needed to be consumed
        maximum_energy_produced = 0  # the maximum quantity of energy needed to be produced

        [min_price, max_price] = self._limit_prices(cluster)  # min and max prices allowed

        sort_function = self.get_revenue  # we choose a sort criteria

        # ##########################################################################################
        # calculus of the minimum and maximum quantities of energy involved in the cluster

        [minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced] = self._limit_quantities(cluster, max_price, min_price, minimum_energy_consumed, maximum_energy_consumed, minimum_energy_produced, maximum_energy_produced)

        # ##########################################################################################
        # distribution of energy

        if maximum_energy_produced <= minimum_energy_consumed or maximum_energy_consumed <= minimum_energy_produced:  # if there is no possibility to balance the grid
            # we consider that the gird falls
            # updates the balances
            self._catalog.set(f"{cluster.name}.energy_bought", {"inside": 0, "outside": 0})
            self._catalog.set(f"{cluster.name}.energy_sold", {"inside": 0, "outside": 0})

            self._catalog.set(f"{cluster.name}.money_spent", {"inside": 0, "outside": 0})
            self._catalog.set(f"{cluster.name}.money_earned", {"inside": 0, "outside": 0})

        else:  # if there is some possibility to balance the grid

            # formulation of needs
            [sorted_demands, sorted_offers] = self._sort_quantities(cluster, sort_function)  # sort the quantities according to their prices

            # demand side
            [sorted_demands, maximum_energy_produced, money_earned_inside, energy_sold_inside] = self._serve_emergency_demands(cluster, max_price, sorted_demands, maximum_energy_produced, money_earned_inside, energy_sold_inside)

            # offer side
            [sorted_offers, maximum_energy_consumed, money_spent_inside, energy_bought_inside] = self._serve_emergency_offers(cluster, min_price, sorted_offers, maximum_energy_consumed, money_spent_inside, energy_bought_inside)

            # then we distribute the remaining quantities according to our sort
            # distribution among consumptions
            [maximum_energy_produced, money_earned_inside, energy_sold_inside] = self._distribute_consumption_full_service(cluster, max_price, sorted_demands, maximum_energy_produced, money_earned_inside, energy_sold_inside)

            # distribution among productions
            [maximum_energy_consumed, money_spent_inside, energy_bought_inside] = self._distribute_production_full_service(cluster, min_price, sorted_offers, maximum_energy_consumed, money_spent_inside, energy_bought_inside)

        # ##########################################################################################
        # updates the balances
        self._update_balances(cluster, energy_bought_inside, 0, energy_sold_inside, 0, money_spent_inside, 0,
                              money_earned_inside, 0)


user_classes_dictionary[f"{AutarkyRevenues.__name__}"] = AutarkyRevenues



