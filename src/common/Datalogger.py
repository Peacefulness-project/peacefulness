# Datalogger role is to write desired data in a file at a given frequency
# from tools.Utilities import list_to_str
# from tools.DataProcessingFunctions import *
from numpy import mean
from math import inf

from src.tools.GraphAndTex import export
from src.tools.GlobalWorld import get_world


class Datalogger:

    def __init__(self, name, filename, period=0, sum_over_time=False):
        self._name = name

        self._filename = filename  # the name of the file where the data will be written
        self._sum = sum_over_time  # enables integration of a data between 2 periods

        self._list = dict()  # list of catalog keys which has to be written

        if period != "global":  # when data must be recorded regularly
            self._period = period  # number of rounds between 2 activations
            self._global = False
            self._process = self._regular_process
        else:  # when only a final view on the data is wanted
            self._period = 1
            self._global = True
            self._process = self._global_process

        self._buffer = dict()  # dict which stores data between each period of registering
        # allows to report info such as mean, min and max between two periods

        self._next_time = 0  # next time step for which data will be written

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # catalog from which data is extracted

        self._filename = self._catalog.get('path') + "/outputs/" + filename + ".txt"

        world.register_datalogger(self)  # register this datalogger into world dedicated dictionary

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def add(self, name, function="default"):  # add 1 key of the catalog to the datalogger
        if function == "default":
            self._list[name] = self._catalog.get  # creates an entry in the buffer if needed
        else:
            self._list[name] = function  # creates an entry in the buffer if needed

        if self._global:
            self._buffer[name] = {"mean": 0, "min": inf, "max": -inf, "sum": 0, "active_rounds": 1}
        elif type(self._list[name](name) == float) and (self._period > 1):  # numeric keys are added to a buffer
            # it allows to return the mean, the min and the max
            self._buffer[name] = []  # creates an entry in the buffer

    def add_all(self):  # add all keys from the catalog to the datalogger
        for name in self._catalog.keys:
            self.add(name)

    # ##########################################################################################
    # Data processing
    # ##########################################################################################

    def _data_processing(self, key):  # function which returns the mean, the min and the max of a key between 2 periods
        processed_data = dict()
        processed_data["mean"] = (mean(self._buffer[key]))  # mean
        processed_data["min"] = (min(self._buffer[key]))  # min
        processed_data["max"] = (max(self._buffer[key]))  # max
        return processed_data

    def _data_sum(self, name):  # if enabled, return the sum of the value over the time
        return sum(self._buffer[name])

    # ##########################################################################################
    # Writing in the file
    # ##########################################################################################

    def launch(self):  # write data at the given frequency
        current_time = self._catalog.get("simulation_time")  # the simulation time allows to know if it has to be called or not

        if current_time == 0 and not self._global:  # initialization of the file
            self._save_header()  # name of each piece of data is written at the top of the file

        if self._period > 1:
            for key in self._buffer:  # for all relevant keys
                self._buffer[key].append(self._catalog.get(key))  # value is saved in the buffer
        if current_time >= self._next_time:  # data is saved only if the current time is a multiple of the defined period

            self._process()  # writes the data in the file
            self._next_time += self._period  # calculates the next period of writing

    def _regular_process(self):  # record all the chosen key regularly in a file
        file = open(self._filename, "a+")
        # both physical date and time and iteration number are systematically added
        file.write(str(self._catalog.get("physical_time")))  # date time in string
        file.write(str(self._catalog.get("simulation_time")))  # iteration number as a string

        for key in self._list:
            value = self._list[key](key)

            file.write(f"{value}\t")
            if (type(value) == float) and (self._period > 1):
                processed_data = self._data_processing(value)  # returns the mean, the min and the max over the period for a key
                file.write(f"{processed_data['mean']}\t"  # saves the mean
                           f"{processed_data['min']}\t"  # saves the min
                           f"{processed_data['max']}\t"  # saves the max
                           )
                if self._sum:  # if sum is enabled, write the sum of the data over the time
                    file.write(f"{self._data_sum(value)}\t")
            self._buffer[key] = []  # Reinitialization of the buffer
        file.write("\n")
        file.close()

    def _global_process(self):  # seeks the min, the mean, the average, the max and the sum of the chosen key at the end of the simulation
        for key in self._list:
            current_value = self._list[key](key)  # the current value of the key

            if current_value is not None:  # if the value is relevant during this turn
                the_mean = (self._buffer[key]["mean"] * (self._buffer[key]["active_rounds"] - 1)/self._buffer[key]["active_rounds"])\
                           + (current_value / self._buffer[key]["active_rounds"])
                active_rounds = self._buffer[key]["active_rounds"] + 1

                minimum = min(self._buffer[key]["min"], current_value)
                maximum = max(self._buffer[key]["max"], current_value)
                the_sum = self._buffer[key]["sum"] + current_value

                self._buffer[key] = {"mean": the_mean, "min": minimum, "max": maximum, "sum": the_sum, "active_rounds": active_rounds}

    def _save_header(self):  # create the headers of the column
        file = open(self._filename, 'a+')

        # both physical date and time and iteration number are systematically added
        file.write("physical time\t")
        file.write("iteration\t")

        for name in self._list:
            file.write(f"{name}\t")

            if name in self._buffer:
                file.write(f"mean_{name}\t"
                           f"min_{name}\t"
                           f"max_{name}\t")
                if self._sum:  # if sum is enabled, add it to the file
                    file.write(f"sum_{name}\t")
        file.write("\n")
        file.close()

    # ##########################################################################################
    # Final operations
    # ##########################################################################################

    def final_process(self):
        if self._global:  # if global values are wanted
            file = open(self._filename, "a+")

            for key in self._buffer:
                file.write(f"for the key {key}:\n")
                file.write(f"\tmean: {self._buffer[key]['mean']}\n")
                file.write(f"\tmin: {self._buffer[key]['min']}\n")
                file.write(f"\tmax: {self._buffer[key]['max']}\n")
                file.write(f"\tsum: {self._buffer[key]['sum']}\n")
                file.write("\n")

            file.close()

    def final_export(self):  # call the relevant export functions
        for export_format in self._catalog.get("export_formats"):
            x_values = {}           # todo: remplir les deux trucs...
            y_values = {}
            export(export_format, x_values, y_values)

    # ##########################################################################################
    # Utilities
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name


# Exception
class DataLoggerException(Exception):
    def __init__(self, message):
        super().__init__(message)
