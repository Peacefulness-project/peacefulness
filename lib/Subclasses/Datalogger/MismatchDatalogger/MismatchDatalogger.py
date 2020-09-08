# this datalogger exports the data considered as results for ECOS proceedings
from src.common.Datalogger import Datalogger
from src.tools.GraphAndTex import __default_graph_options__


class MismatchDatalogger(Datalogger):  # a sub-class of dataloggers designed to export values concerning the whole run

    def __init__(self, period=1, graph_options=__default_graph_options__):
        if period == "global":
            super().__init__("mismatch_global", "Mismatch_global", period)
        else:
            super().__init__(f"mismatch_frequency_{period}", f"Mismatch_frequency_{period}", period, graph_options=graph_options, graph_labels={"xlabel": "time", "ylabel": f"mismatch"})

        if not self._global:
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status=None)

        natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names

        def create_energy_mismatch_function(nature_name):

            def get_energy_mismatch(name):
                energy_mismatch = self._catalog.get(f"{nature_name}.energy_consumed") - self._catalog.get(f"{nature_name}.energy_produced")

                return energy_mismatch

            return get_energy_mismatch

        for nature_name in natures_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{nature_name}.energy_mismatch", create_energy_mismatch_function(nature_name))



