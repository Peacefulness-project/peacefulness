# this datalogger exports the data considered as results for ECOS proceedings
from src.common.Datalogger import Datalogger
from src.tools.Utilities import adapt_path


class ECOSAggregatorDatalogger(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self, period=1):
        super().__init__("ECOS_aggregators_results", "ECOS_aggregators_results", period)

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names
        self._agents_list = self._catalog.get("dictionaries")['agents'].keys()  # get all the names
        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        file = open(self._filename, "a+")

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            file.write(f"{aggregator_name}_self_sufficiency_consumption\t")
            file.write(f"{aggregator_name}_self_sufficiency_production\t")
            file.write(f"{aggregator_name}_grid_call\t")
            file.write(f"{aggregator_name}_benefit\t")

        for nature_name in self._natures_list:
            file.write(f"ratio_canceled.{nature_name}\t")

        file.write(f"bill\t")

        file.write(f"\t")

    def _process(self):
        file = open(self._filename, "a+")

        # aggregator data
        for aggregator_name in self._aggregators_list:
            self_sufficiency = {"consumption": None, "production": None}  # the rate of energy consumed locally/total energy consumed and energy produced locally/ total energy consumed

            energy_sold = self._catalog.get(f"{aggregator_name}.energy_sold")
            energy_bought = self._catalog.get(f"{aggregator_name}.energy_bought")
            benefit = sum(self._catalog.get(f"{aggregator_name}.money_earned").values()) - sum(self._catalog.get(f"{aggregator_name}.money_spent").values())

            # self_sufficiency
            if energy_sold["inside"] != 0:  # if some energy is consumed locally
                self_sufficiency["consumption"] = min(energy_bought["inside"] / energy_sold["inside"], 1)  # the ratio of the energy consumed locally being produced locally
            else:
                self_sufficiency["consumption"] = None

            if energy_bought["inside"] != 0:  # if some energy is produced locally
                self_sufficiency["production"] = min(energy_sold["inside"] / energy_bought["inside"], 1)  # the ratio of the energy produced locally being consumed locally
            else:
                self_sufficiency["production"] = None

            # grid call
            grid_call = (energy_bought["outside"] - energy_sold["outside"])

            file.write(f"{self_sufficiency['consumption']}\t")
            file.write(f"{self_sufficiency['production']}\t")

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
                canceled_ratio = None

            file.write(f"{canceled_ratio}\t")

        file.write(f"{bill}\t")

        file.write("\n")
        file.close()


class GlobalValuesDatalogger(Datalogger):  # a sub-class of dataloggers designed to export values concerning the whole run

    def __init__(self, period=0):
        super().__init__("global_values", "global_values", period)

        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        self._peak = dict()
        self._overprod = dict()
        self._overconso = dict()
        for nature_name in self._natures_list:  # for each aggregator registered into world, all the relevant keys are added
            self._peak[nature_name] = {"peak_consumption": 0, "peak_production": 0, "peak_unbalance": 0}

        self._last_turn = self._catalog.get("time_limit") - 1  # the number of the last iteration

    def _process(self):
        # at every turn, the peak are reactualized
        for nature_name in self._peak:
            if self._peak[nature_name]["peak_consumption"] < self._catalog.get(f"{nature_name}.energy_consumed"):
                self._peak[nature_name]["peak_consumption"] = self._catalog.get(f"{nature_name}.energy_consumed")
            if self._peak[nature_name]["peak_production"] > self._catalog.get(f"{nature_name}.energy_produced"):
                self._peak[nature_name]["peak_production"] = self._catalog.get(f"{nature_name}.energy_produced")
            if self._peak[nature_name]["peak_unbalance"] < self._catalog.get(f"{nature_name}.energy_consumed") + self._catalog.get(f"{nature_name}.energy_produced"):
                self._peak[nature_name]["peak_unbalance"] = self._catalog.get(f"{nature_name}.energy_consumed") + self._catalog.get(f"{nature_name}.energy_produced")

        # at the last turn, the file is written
        if self._last_turn == self._catalog.get("simulation_time"):
            file = open(self._filename, "a+")

            for nature_name in self._peak:
                file.write(f" peak_consumption_{nature_name}: {self._peak[nature_name]['peak_consumption']}\n")
                file.write(f" peak_production_{nature_name}: {self._peak[nature_name]['peak_production']}\n")
                file.write(f" peak_unbalance_{nature_name}: {self._peak[nature_name]['peak_unbalance']}\n")
                file.write("\n")

            file.close()


