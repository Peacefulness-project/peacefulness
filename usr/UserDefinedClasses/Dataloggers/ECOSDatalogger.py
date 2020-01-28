# this datalogger exports the data considered as results for ECOS proceedings
from common.Datalogger import Datalogger
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import adapt_path


class ECOSClusterDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self):
        super().__init__("ECOS_clusters_results", "ECOS_clusters_results")

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

            try:
                self_consumption = energy_bought["inside"] / energy_sold["inside"]  # the ratio between the energy sold inside and the energy bought inside
            except:
                self_consumption = 0

            grid_call = (energy_bought["outside"] - energy_sold["outside"])

            file.write(f"{self_consumption}\t")
            file.write(f"{grid_call}\t")
            file.write(f"{benefit}\t")

        # aggregated agent data
        quantity_erased = 0
        quantity_given = 0
        bill = 0
        for nature_name in self._natures_list:

            for agent_name in self._agents_list:
                try:  # if the nature is present in the agent
                    quantity_erased += abs(self._catalog.get(f"{agent_name}.{nature_name}.energy_erased"))
                    quantity_given += abs(self._catalog.get(f"{agent_name}.{nature_name}.energy_bought") + 0 * self._catalog.get(f"{agent_name}.{nature_name}.energy_sold"))
                except:
                    pass
                bill += self._catalog.get(f"{agent_name}.money_spent")

            if quantity_given != 0:
                canceled_ratio = quantity_erased / ( quantity_given + quantity_erased)
            else:
                canceled_ratio = 1

            file.write(f"{canceled_ratio}\t")
            file.write(f"{bill}\t")

        file.write("\n")
        file.close()


class ECOSAgentDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, name):
        super().__init__(f"{name}_ECOS_agents_results", f"{name}_ECOS_agents_results")

    def _register(self, catalog):
        self._catalog = catalog

        self._agents_list = self._catalog.get("dictionaries")['agents'].keys()  # get all the names

        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")

        for agent_name in self._agents_list:
            file.write(f"Mean_{agent_name}_accorded_quantity\t"
                       f"Min_{agent_name}_accorded_quantity\t"
                       f"Max_{agent_name}_accorded_quantity\t")
            file.write(f"Sum_{agent_name}_accorded_quantity\t")

            file.write(f"Mean_{agent_name}_erased_quantity\t"
                       f"Min_{agent_name}_erased_quantity\t"
                       f"Max_{agent_name}_erased_quantity\t")
            file.write(f"Sum_{agent_name}_erased_quantity\t")
            
            self._buffer[f"{agent_name}_accorded_quantity"] = []  # creates an entry in the buffer
            self._buffer[f"{agent_name}_erased_quantity"] = []  # creates an entry in the buffer

        file.write("\n")
        file.close()

        self._next_time = self._catalog.get("physical_time").month + 1  # the +1 serves to write balances at the end of the month

    # def launch(self):  # write data at the given frequency
        # current_time = self._catalog.get("physical_time").month  # the simulation time allows to know if it has to be called or not
        #
        # for agent_name in self._agents_list:
        #     self._buffer[f"{agent_name}_accorded_quantity"].append(self._catalog.get(f"{agent_name}.energy_bought") + self._catalog.get(f"{agent_name}.energy_sold"))
        #     self._buffer[f"{agent_name}_erased_quantity"].append(self._catalog.get(f"{agent_name}.energy_erased"))
        #
        # if current_time == self._next_time:  # data is saved only if the current time is a multiple of the defined period
        #     self._save()  # writes the data in the file
        #     self._next_time = (self._catalog.get("physical_time").month + 1) % 12   # delays the next info the following month

    # def _save(self):
        # file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")
        #
        # for agent_name in self._agents_list:
        #
        #     # accorded quantity
        #     processed_data = self._data_processing(f"{agent_name}_accorded_quantity")  # = [mean, min, max]
        #     file.write(f"{processed_data[0]}\t"  # saves the mean
        #                f"{processed_data[1]}\t"  # saves the min
        #                f"{processed_data[2]}\t"  # saves the max
        #                )
        #     file.write(f"{self._data_sum(f'{agent_name}_accorded_quantity')}\t")
        #     self._buffer[f"{agent_name}_accorded_quantity"] = []  # Reinitialization of the buffer
        #
        #     # erased quantity
        #     processed_data = self._data_processing(f"{agent_name}_erased_quantity")  # = [mean, min, max]
        #     file.write(f"{processed_data[0]}\t"  # saves the mean
        #                f"{processed_data[1]}\t"  # saves the min
        #                f"{processed_data[2]}\t"  # saves the max
        #                )
        #     file.write(f"{self._data_sum(f'{agent_name}_erased_quantity')}\t")
        #     self._buffer[f"{agent_name}_erased_quantity"] = []  # Reinitialization of the buffer
        #
        # file.write("\n")
        # file.close()


class GlobalValuesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export values concerning the whole run

    def __init__(self):
        super().__init__("global_values", "global_values")

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


user_classes_dictionary[f"{ECOSClusterDatalogger.__name__}"] = ECOSClusterDatalogger
user_classes_dictionary[f"{ECOSAgentDatalogger.__name__}"] = ECOSAgentDatalogger
user_classes_dictionary[f"{GlobalValuesDatalogger.__name__}"] = GlobalValuesDatalogger

