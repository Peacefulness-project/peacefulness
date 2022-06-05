# These dataloggers exports the balances for aggregators
from src.common.Datalogger import Datalogger
# from src.tools.GraphAndTex import __default_graph_options__


class ClusteringMetricsDatalogger(Datalogger):  # a sub-class of dataloggers dedicated to aliment clustering process

    def __init__(self, period=1, graph_options="default"):
        if period == "global":
            super().__init__("aggregator_clustering_metrics_global", "AggregatorsClusteringMetrics_global", period)
        else:
            super().__init__(f"aggregator_clustering_metrics_frequency_{period}", f"AggregatorsClusteringMetrics_frequency_{period}", period)

    # ##############################################################################################
    # functions-defining methods

        def create_get_minimum_consumption_ratio(aggregator_name):

            def get_minimum_consumption_ratio(name):
                minimum_consumption = self._catalog.get(f"{aggregator_name}.minimum_energy_consumption")
                maximum_consumption = self._catalog.get(f"{aggregator_name}.maximum_energy_consumption")

                return minimum_consumption / maximum_consumption

            return get_minimum_consumption_ratio

        def create_get_minimum_production_ratio(aggregator_name):

            def get_minimum_production_ratio(name):
                minimum_production = self._catalog.get(f"{aggregator_name}.minimum_energy_production")
                maximum_consumption = self._catalog.get(f"{aggregator_name}.maximum_energy_consumption")

                return minimum_production / maximum_consumption

            return get_minimum_production_ratio

        def create_get_maximum_production_ratio(aggregator_name):

            def get_maximum_production_ratio(name):
                maximum_consumption = self._catalog.get(f"{aggregator_name}.maximum_energy_consumption")
                maximum_production = self._catalog.get(f"{aggregator_name}.maximum_energy_production")

                return maximum_production / maximum_consumption

            return get_maximum_production_ratio

        def create_get_energy_stored_ratio(aggregator_name):

            def get_energy_stored_ratio(name):
                maximum_consumption = self._catalog.get(f"{aggregator_name}.maximum_energy_consumption")
                energy_stored = self._catalog.get(f"{aggregator_name}.energy_stored")

                return energy_stored / maximum_consumption

            return get_energy_stored_ratio

        def create_get_energy_storable_ratio(aggregator_name):

            def get_energy_storable_ratio(name):
                maximum_consumption = self._catalog.get(f"{aggregator_name}.maximum_energy_consumption")
                energy_storable = self._catalog.get(f"{aggregator_name}.energy_stored")

                return energy_storable / maximum_consumption

            return get_energy_storable_ratio

        # ##############################################################################################

        self._aggregators_list = self._catalog.get("dictionaries")['aggregators'].keys()  # get all the names

        if self._type != "global":
            self.add(f"simulation_time", graph_status="X")
            self.add(f"physical_time", graph_status="")

        for aggregator_name in self._aggregators_list:  # for each aggregator registered into world, all the relevant keys are added
            self.add(f"{aggregator_name}.minimum_consumption_ratio", create_get_minimum_consumption_ratio(aggregator_name))
            self.add(f"{aggregator_name}.minimum_production_ratio", create_get_minimum_production_ratio(aggregator_name))
            self.add(f"{aggregator_name}.maximum_production_ratio", create_get_maximum_production_ratio(aggregator_name))
            self.add(f"{aggregator_name}.energy_stored_ratio", create_get_energy_stored_ratio(aggregator_name))
            self.add(f"{aggregator_name}.energy_storable_ratio", create_get_energy_storable_ratio(aggregator_name))

