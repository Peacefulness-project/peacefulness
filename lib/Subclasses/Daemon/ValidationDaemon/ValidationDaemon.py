# This daemon is here to validate at each turn that calculation are made correctly.
from src.common.Daemon import Daemon
from src.common.Datalogger import Datalogger

from src.tools.GraphAndTex import GraphOptions, write_and_print, export
from src.tools.Utilities import adapt_path

from lib.Subclasses.Daemon.ValidationDaemon.GlobalProblem import set_problem


class ValidationDaemon(Daemon):

    def __init__(self, name, parameters, period=1):
        super().__init__(name, period, parameters)

        self._description = parameters["description"]

        self._filename = parameters["filename"] + ".txt"  # the name of the file were results are written

        self._reference_values = parameters["reference_values"]  # the reference values

        self._x_values = {"iteration": [], "physical_time": []}
        self._y_values = {f"{key_checked}_reference": parameters["reference_values"][key_checked] for key_checked in parameters["reference_values"]}
        for key in parameters["reference_values"].keys():
            self._y_values[f"{key}_simulation"] = []

        self._tolerance = parameters["tolerance"]  # the tolerance to accept or reject a value

        self._problem = {key: [] for key in parameters["reference_values"].keys()}  # a list containing all the round when a problem occured

        self._export_plots = parameters["export_plots"]

        # the message are both prompted and written in a file
        message = f"{self.name}: {self._description}\n" \
            f"The following keys are checked: {self._reference_values.keys()}\n"

        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")  # the file resuming the results of the test

        write_and_print(message, file)

        file.close()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):  # get the values of the catalog and compare them with the results
        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")  # the file resuming the results of the test
        data_to_check = {}
        iteration = self._catalog.get("simulation_time") - 1

        self._x_values["iteration"].append(self._catalog.get("simulation_time"))
        self._x_values["physical_time"].append(self._catalog.get('physical_time'))

        for key in self._reference_values.keys():  # put all the data to check in one dictionary
            data_to_check[key] = self._catalog.get(key)
            self._y_values[f"{key}_simulation"].append(self._catalog.get(key))

            if abs(data_to_check[key] - self._reference_values[key][iteration]) < self._tolerance:  # if the key are the same
                pass
            else:  # if the results and the data in the catalog are different
                file.write(f"\niteration {iteration}\n")
                message = f"{self._catalog.get('physical_time')}\n" \
                    f"{key} : KO, reference value = {self._reference_values[key][iteration]} and simulation value = {data_to_check[key]}"
                self._problem[key].append(iteration)
                set_problem(True)  # reports to the upper level that a problem occured

                write_and_print(message, file)

        file.close()

    # ##########################################################################################
    # Final operations
    # ##########################################################################################

    def final_process(self):
        # List of the checked keys
        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")  # the file resuming the results of the test

        message = "\nResume of the test:"
        write_and_print(message, file)

        for key in self._reference_values.keys():
            if self._problem[key]:
                message = f"a problem has been encountered for the key {key} at the iterations {self._problem[key]}"
            else:
                message = f"no problem encountered for key {key}"

            write_and_print(message, file)

        message = ""
        write_and_print(message, file)

        file.close()

        # Export
        for elt in self._export_plots:
            x_exported_values = {}
            y_exported_values = {}

            x_exported_values[elt["X"]["catalog_name_entry"]] = {"values": self._x_values[elt["X"]["catalog_name_entry"]]}

            for list in elt["Y"]["graphs"]:
                y_exported_values[list["catalog_name_entry"]] = {"values": self._y_values[list["catalog_name_entry"]],
                                                                 "style": list["style"],
                                                                 "legend": list["legend"],
                                                                 "label": 1}
            if "Y2" in elt.keys():
                for list in elt["Y2"]["graphs"]:
                    y_exported_values[list["catalog_name_entry"]] = {
                        "values": self._y_values[list["catalog_name_entry"]],
                        "style": list["style"],
                        "legend": list["legend"],
                        "label": 2}

            labels = {"xlabel": elt["X"]["label"], "ylabel": elt["Y"]["label"]}
            if "Y2" in elt.keys():
                labels.update({"y2label": elt["Y2"]["label"]})

            export(elt["options"], self._catalog.get('path')+"/outputs/"+elt["filename"], x_exported_values, y_exported_values, labels)
