# this datalogger exports the data considered as results for ECOS proceedings
from src.common.Datalogger import Datalogger
from src.tools.Utilities import adapt_path


class ECOSClusterDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, world, period=0):
        super().__init__(world, "ECOS_clusters_results", "ECOS_clusters_results", period)

    def _register(self, catalog):
        self._catalog = catalog

        self._clusters_list = self._catalog.get("dictionaries")['clusters'].keys()  # get all the names
        self._agents_list = self._catalog.get("dictionaries")['agents'].keys()  # get all the names
        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")

        for cluster_name in self._clusters_list:  # for each cluster registered into world, all the relevant keys are added
            file.write(f"{cluster_name}_self_consumption\t")
            file.write(f"{cluster_name}_grid_call\t")
            file.write(f"{cluster_name}_benefit\t")

        for nature_name in self._natures_list:
            file.write(f"ratio_canceled.{nature_name}\t")
            file.write(f"bill.{nature_name}\t")

        file.write(f"\t")

    def _save(self):
        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")

        # cluster data
        for cluster_name in self._clusters_list:
            energy_sold = self._catalog.get(f"{cluster_name}.energy_sold")
            energy_bought = self._catalog.get(f"{cluster_name}.energy_bought")
            benefit = sum(self._catalog.get(f"{cluster_name}.money_earned").values()) - sum(self._catalog.get(f"{cluster_name}.money_spent").values())

            if energy_sold["inside"] != 0:  # if some energy is sold
                self_consumption = energy_bought["inside"] / energy_sold["inside"]  # the ratio between the energy sold inside and the energy bought inside
            else:
                self_consumption = None

            grid_call = (energy_bought["outside"] - energy_sold["outside"])

            file.write(f"{self_consumption}\t")
            file.write(f"{grid_call}\t")
            file.write(f"{benefit}\t")

        # aggregated agent data
        quantity_erased = 0
        quantity_got = 0
        bill = 0
        for nature_name in self._natures_list:

            for agent_name in self._agents_list:
                try:  # if the nature is present in the agent
                    quantity_erased += abs(self._catalog.get(f"{agent_name}.{nature_name}.energy_erased"))
                    quantity_got += abs(self._catalog.get(f"{agent_name}.{nature_name}.energy_bought"))
                except:
                    pass
                bill += self._catalog.get(f"{agent_name}.money_spent")

            if (quantity_got + quantity_erased) != 0:
                canceled_ratio = quantity_erased / (quantity_got + quantity_erased)
            else:
                canceled_ratio = 0

            file.write(f"{canceled_ratio}\t")
            file.write(f"{bill}\t")

        file.write("\n")
        file.close()


class GlobalValuesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export values concerning the whole run

    def __init__(self, world, period=0):
        super().__init__(world, "global_values", "global_values", period)

        self._last_turn = None

    def _register(self, catalog):
        self._catalog = catalog

        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        self._peak = dict()
        self._overprod = dict()
        self._overconso = dict()
        for nature_name in self._natures_list:  # for each cluster registered into world, all the relevant keys are added
            self._peak[nature_name] = {"peak_consumption": 0, "peak_production": 0, "peak_unbalance": 0}
            self._overprod[nature_name] = 0  # the number of turn where there was too much prod
            self._overconso[nature_name] = 0  # the number of turns where there was too much conso

        self._last_turn = self._catalog.get("time_limit") - 1  # the number of the last iteration

    def _save(self):
        # at every turn, the peak are reactualized
        for nature_name in self._peak:
            if self._peak[nature_name]["peak_consumption"] < self._catalog.get(f"{nature_name}.energy_consumed"):
                self._peak[nature_name]["peak_consumption"] = self._catalog.get(f"{nature_name}.energy_consumed")
            if self._peak[nature_name]["peak_production"] > self._catalog.get(f"{nature_name}.energy_produced"):
                self._peak[nature_name]["peak_production"] = self._catalog.get(f"{nature_name}.energy_produced")
            if self._peak[nature_name]["peak_unbalance"] < self._catalog.get(f"{nature_name}.energy_consumed") + self._catalog.get(f"{nature_name}.energy_produced"):
                self._peak[nature_name]["peak_unbalance"] = self._catalog.get(f"{nature_name}.energy_consumed") + self._catalog.get(f"{nature_name}.energy_produced")

            if self._catalog.get(f"{nature_name}.energy_consumed") - self._catalog.get(f"{nature_name}.energy_produced") > 1e-6:
                self._overconso[nature_name] += 1
            elif self._catalog.get(f"{nature_name}.energy_produced") - self._catalog.get(f"{nature_name}.energy_consumed") > 1e-6:
                self._overprod[nature_name] += 1

        # at the last turn, the file is written
        if self._last_turn == self._catalog.get("simulation_time"):
            file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")

            for nature_name in self._peak:
                file.write(f" peak_consumption_{nature_name}: {self._peak[nature_name]['peak_consumption']}\n")
                file.write(f" peak_production_{nature_name}: {self._peak[nature_name]['peak_production']}\n")
                file.write(f" peak_unbalance_{nature_name}: {self._peak[nature_name]['peak_unbalance']}\n")
                file.write(f" over_production_{nature_name}: {self._overprod[nature_name]/(self._last_turn+1)}\n")
                file.write(f" over_consumption_{nature_name}: {self._overconso[nature_name]/(self._last_turn+1)}\n")

                file.write("\n")

            file.close()


