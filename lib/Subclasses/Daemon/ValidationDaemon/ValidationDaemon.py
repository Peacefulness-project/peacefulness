# This daemon is here to validate at each turn that calculation are made correctly.
from src.common.Daemon import Daemon
from src.tools.Utilities import adapt_path


class ValidationDaemon(Daemon):

    def __init__(self, name, parameters, period=1):
        super().__init__(name, period, parameters)

        self._reference_values = parameters["reference_values"]  # the reference values

        self._filename = parameters["filename"]  # the name of the file were results are written

        self._description = parameters["description"]

        self._problem = {key: [] for key in parameters["reference_values"].keys()}  # a list containing all the round when a problem occured

        # the message are both prompted and written in a file
        message = f"{self.name}: {self._description}\n" \
            f"The following keys are checked:{self._reference_values.keys()}\n"

        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")  # the file resuming the results of the test

        self._write_and_print(message, file)

        file.close()

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def add_key(self):
        pass

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _process(self):  # get the values of the catalog and compare them with the results
        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")  # the file resuming the results of the test
        data_to_check = {}
        iteration = self._catalog.get("simulation_time")

        file.write(f"iteration {iteration}\n")

        for key in self._reference_values.keys():  # put all the data to check in one dictionary
            data_to_check[key] = self._catalog.get(key)

            if data_to_check[key] == self._reference_values[key][iteration]:  # if the key are the same
                message = f"{key} : OK"
            else:  # if the results and the data in the catalog are different
                message = f"{key} : KO, reference value = {self._reference_values[key][iteration]} and simulation value = {data_to_check[key]}"
                self._problem[key].append(iteration)
                print(self._catalog.get("physical_time"))

            self._write_and_print(message, file)

        if self._catalog.get("time_limit") - 1 == self._catalog.get("simulation_time"):  # at the last iteration, a resume is written and printed
            message = "Resume of the test:"
            self._write_and_print(message, file)

            for key in self._reference_values.keys():
                if self._problem[key]:
                    message = f"a problem has been encountered for the key {key} at the iterations {self._problem[key]}"
                else:
                    message = f"no problem encountered for key {key}"

                self._write_and_print(message, file)

        file.close()

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    def _write_and_print(self, message, file):  # write in the chosen file and print the message
        file.write(message + "\n")
        print(message)





