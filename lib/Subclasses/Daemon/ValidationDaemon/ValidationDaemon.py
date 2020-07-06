# This daemon is here to validate at each turn that calculation are made correctly.
from src.common.Daemon import Daemon
from src.tools.GraphAndTex import export
from src.tools.Utilities import adapt_path

from lib.Subclasses.Daemon.ValidationDaemon.GlobalProblem import set_problem


class ValidationDaemon(Daemon):

    def __init__(self, name, parameters, period=1):
        super().__init__(name, period, parameters)

        self._reference_values = parameters["reference_values"]  # the reference values

        self._filename = parameters["filename"] + ".txt"  # the name of the file were results are written

        self._description = parameters["description"]

        self._tolerance = parameters["tolerance"]  # the tolerance to accept or reject a value

        self._problem = {key: [] for key in parameters["reference_values"].keys()}  # a list containing all the round when a problem occured

        self._x_values = {"iteration": []}
        self._y_values = {f"reference value of {key_checked}": parameters["reference_values"][key_checked] for key_checked in parameters["reference_values"]}
        for key in parameters["reference_values"].keys():
            self._y_values[f"simulation value of {key}"] = []

        # the message are both prompted and written in a file
        message = f"{self.name}: {self._description}\n" \
            f"The following keys are checked: {self._reference_values.keys()}\n"

        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")  # the file resuming the results of the test

        self._write_and_print(message, file)

        file.close()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):  # get the values of the catalog and compare them with the results
        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")  # the file resuming the results of the test
        data_to_check = {}
        iteration = self._catalog.get("simulation_time")

        for key in self._reference_values.keys():  # put all the data to check in one dictionary
            data_to_check[key] = self._catalog.get(key)
            self._x_values["iteration"].append(self._catalog.get("simulation_time"))
            self._y_values[f"simulation value of {key}"].append(self._catalog.get(key))

            if abs(data_to_check[key] - self._reference_values[key][iteration]) < self._tolerance:  # if the key are the same
                pass
            else:  # if the results and the data in the catalog are different
                file.write(f"\niteration {iteration}\n")
                message = f"{self._catalog.get('physical_time')}\n" \
                    f"{key} : KO, reference value = {self._reference_values[key][iteration]} and simulation value = {data_to_check[key]}"
                self._problem[key].append(iteration)
                set_problem(True)  # reports to the upper level that a problem occured

                self._write_and_print(message, file)

        file.close()

    # ##########################################################################################
    # Final operations
    # ##########################################################################################

    def final_process(self):
        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")  # the file resuming the results of the test
        data_to_check = {}
        iteration = self._catalog.get("simulation_time")

        message = "\nResume of the test:"
        self._write_and_print(message, file)

        for key in self._reference_values.keys():
            if self._problem[key]:
                message = f"a problem has been encountered for the key {key} at the iterations {self._problem[key]}"
            else:
                message = f"no problem encountered for key {key}"

            self._write_and_print(message, file)

        file.close()

        for export_format in self._catalog.get("export_formats"):
            export(export_format, self._x_values, self._y_values)

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def _write_and_print(self, message, file):  # write in the chosen file and print the message
        file.write(message + "\n")
        print(message)





