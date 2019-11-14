# This sheet describes a supervisor of a TSO
# It represents the higher level of energy management. Here, it is a black box: it both proposes and accepts unlimited amounts of energy
from common.Supervisor import Supervisor
from math import inf
from tools.UserClassesDictionary import user_classes_dictionary


class Grid(Supervisor):

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def ascendant_phase(self, cluster):  # the grid, as it has no devices, has no distribution to make
        pass

    def publish_quantities(self, cluster):  # the grid can always sell and buy an infinite quantity of energy
        selling_price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")
        buying_price = self._catalog.get(f"{cluster.nature.name}.grid_selling_price")

        grid_offer = [[-inf, selling_price], [inf, buying_price]]

        self._catalog.set(f"{cluster.name}.{cluster.nature.name}.energy_needs", grid_offer)

    def distribute_remote_energy(self, cluster):  # the grid, as it has no devices, has no distribution to make
        pass


user_classes_dictionary[f"{Grid.__name__}"] = Grid



