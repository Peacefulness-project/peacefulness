# this datalogger exports the data considered as results for ECOS proceedings
from common.Datalogger import Datalogger
from tools.UserClassesDictionary import user_classes_dictionary
from tools.Utilities import adapt_path


class ECOS(Datalogger):  # a sub-class of dataloggers designed to export the balances

    def __init__(self):
        super().__init__("ECOS_results", "ECOS_results")

    def _register(self, catalog):
        self._catalog = catalog

        self._clusters_list = self._catalog.get("dictionaries")['clusters'].keys()  # get all the names
        self._natures_list = self._catalog.get("dictionaries")['natures'].keys()  # get all the names
        self._devices_list = self._catalog.get("dictionaries")['devices'].keys()  # get all the names

        for cluster_name in self._clusters_list:  # for each cluster registered into world, all the relevant keys are added
            self.add(f"{cluster_name}.energy_sold")
            self.add(f"{cluster_name}.energy_bought")
            self.add(f"{cluster_name}.money_spent")
            self.add(f"{cluster_name}.money_earned")

    def _save(self):
        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")

        for cluster_name in self._clusters_list:
            energy_sold = self._catalog.get(f"{cluster_name}.energy_sold")
            energy_bought = self._catalog.get(f"{cluster_name}.energy_bought")

            try:
                self_consumption = energy_bought["inside"] / energy_sold["inside"]  # the ratio between the energy sold inside and the energy bought inside
            except:
                self_consumption = "no_consumption"

            try:
                grid_call = (energy_bought["outside"] - energy_sold["outside"]) / energy_sold["inside"]
            except:
                grid_call = "no_grid_call"

            file.write(f"{self_consumption}\t")
            file.write(f"{grid_call}\t")

        for devices in self._devices_list:
            erased_quantity = 0

        for nature in self._natures_list:
            peak_power = 0

        file.write("\n")
        file.close()


user_classes_dictionary[f"{ECOS.__name__}"] = ECOS

