# Datalogger role is to write desired data in a file at a given frequency
# from tools.Utilities import list_to_str
# from tools.DataProcessingFunctions import *
from numpy import mean
from math import inf

from src.tools.FilesExtensions import __text_extension__

from src.tools.GraphAndTex import GraphOptions, export
from src.tools.GlobalWorld import get_world


class Datalogger:

    def __init__(self, name, filename, period=0, graph_options="default", graph_labels={"xlabel": "X", "ylabel": "Y"}):
        self._name = name

        self._list = dict()  # list of catalog keys which has to be written

        self._buffer = dict()  # dict which stores data between each period of registering
        # allows to report info such as mean, min and max between two periods

        self._next_time = 0  # next time step for which data will be written

        world = get_world()  # get automatically the world defined for this case
        self._catalog = world.catalog  # catalog from which data is extracted

        self._path = self._catalog.get('path') + "/outputs/"
        self._filename = filename

        world.register_datalogger(self)  # register this datalogger into world dedicated dictionary

        if period == "global":  # when only a final view on the data is wanted
            self._period = 1
            self._type = "global"  #
            self._process = self._global_process
        elif period == "month":  # if a monthly record is required
            self._period = 1
            self._type = "month"
            self._month = self._catalog.get("physical_time").month  # the number of the ongoing month
            self._process = self._month_process
        else:  # when data must be recorded regularly
            self._period = period  # number of rounds between 2 activations
            self._type = "regular"
            self._process = self._regular_process

        self._x_values = {}
        self._y_values = {}

        if graph_options == "default":
            self._graph_options = GraphOptions(f"graph_options_{self.name}", [], "single_series")
        else:
            self._graph_options = graph_options
        self._graph_labels = graph_labels

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def add(self, name, function="default", graph_status="Y", graph_style="lines", graph_legend=False):  # add 1 key of the catalog to the datalogger
        if function == "default":  # the function parameter allows to export the result of a calculation directly during the simulation
            self._list[name] = self._catalog.get  # creates an entry in the buffer if needed
        else:
            self._list[name] = function  # creates an entry in the buffer if needed

        if "Y" in graph_status and (self._type != "regular" or self._period > 1):  # numeric keys are added to a buffer when it is not
            # it allows to return the mean, the min and the max
            self._buffer[name] = {"mean": 0, "min": inf, "max": -inf, "sum": 0, "active_rounds": 1}  # creates an entry in the buffer

        # todo: pas de graph_legend ni graph_type pour graph_status="X"... on les ignore ou on pète une erreur ?
        # todo: graph_status="X" ne doit apparaitre qu'une fois

        if not graph_legend:
            graph_legend = name

        if graph_status == "X":
            self._x_values[name] = {"values": []}
        elif graph_status == "Y":
            self._y_values[name] = {"values": [], "style": graph_style, "legend": graph_legend, "label": 1}
        elif graph_status == "Y2":
            self._y_values[name] = {"values": [], "style": graph_style, "legend": graph_legend, "label": 2}
        else:
            pass

    def add_all(self):  # add all keys from the catalog to the datalogger
        for name in self._catalog.keys:
            self.add(name)

    def initial_operations(self):  # create the headers of the column
        if self._type != "global":
            file = open(self._path+self._filename+__text_extension__, 'a+')

            for name in self._list:

                if name in self._buffer:
                    file.write(f"mean_{name}\t"
                               f"min_{name}\t"
                               f"max_{name}\t"
                               f"sum_{name}\t")
                else:
                    file.write(f"{name}\t")

            file.write("\n")
            file.close()

    # ##########################################################################################
    # Data processing
    # ##########################################################################################

    def _data_processing(self, key):  # function which returns the mean, the min and the max of a key between 2 periods
        current_value = self._list[key](key)  # the current value of the key

        if current_value is not None:  # if the value is relevant during this turn
            the_mean = (self._buffer[key]["mean"] * (self._buffer[key]["active_rounds"] - 1) / self._buffer[key]["active_rounds"]) \
                       + (current_value / self._buffer[key]["active_rounds"])
            active_rounds = self._buffer[key]["active_rounds"] + 1

            minimum = min(self._buffer[key]["min"], current_value)
            maximum = max(self._buffer[key]["max"], current_value)
            the_sum = self._buffer[key]["sum"] + current_value

            self._buffer[key] = {"mean": the_mean, "min": minimum, "max": maximum, "sum": the_sum, "active_rounds": active_rounds}

    # ##########################################################################################
    # Writing in the file
    # ##########################################################################################

    def launch(self):  # write data at the given frequency
        current_time = self._catalog.get("simulation_time")  # the simulation time allows to know if it has to be called or not

        if self._period > 1:
            for key in self._buffer:  # for all relevant keys
                self._data_processing(key)
        if current_time >= self._next_time:  # data is saved only if the current time is a multiple of the defined period

            self._process()  # writes the data in the file
            self._next_time += self._period  # calculates the next period of writing

    def _regular_process(self):  # record all the chosen key regularly in a file
        file = open(self._path+self._filename+__text_extension__, "a+")

        for key in self._list:
            value = self._list[key](key)

            # values saving for the figures
            if key in self._x_values:
                self._x_values[key]["values"].append(value)
            if key in self._y_values:
                self._y_values[key]["values"].append(value)

            if key in self._buffer:
                file.write(f"{self._buffer[key]['mean']}\t"  # saves the mean
                           f"{self._buffer[key]['min']}\t"  # saves the min
                           f"{self._buffer[key]['max']}\t"  # saves the max
                           f"{self._buffer[key]['sum']}\t"  # saves the sum
                           )

                self._buffer[key] = {"mean": 0, "min": inf, "max": -inf, "sum": 0, "active_rounds": 1}

            else:
                file.write(f"{value}\t")

        file.write("\n")
        file.close()

    def _month_process(self):  # seeks the min, the mean, the average, the max and the sum of the chosen key at the end of the simulation
        for key in self._buffer:
            self._data_processing(key)

        if self._month != self._catalog.get("physical_time").month:  # if it is a new month
            file = open(self._path + self._filename + __text_extension__, "a+")
            self._month += 1
            for key in self._list:

                value = self._list[key](key)

                # values saving for the figures
                if key in self._x_values:
                    self._x_values[key]["values"].append(value)
                if key in self._y_values:
                    self._y_values[key]["values"].append(value)

                if key in self._buffer:
                    file.write(f"{self._buffer[key]['mean']}\t"  # saves the mean
                               f"{self._buffer[key]['min']}\t"  # saves the min
                               f"{self._buffer[key]['max']}\t"  # saves the max
                               f"{self._buffer[key]['sum']}\t"
                               )

                    self._buffer[key] = {"mean": 0, "min": inf, "max": -inf, "sum": 0, "active_rounds": 1}
                else:
                    file.write(f"{value}\t")

            file.write("\n")
            file.close()

    def _global_process(self):  # seeks the min, the mean, the average, the max and the sum of the chosen key at the end of the simulation
        if self._catalog.get("simulation_time") >= 3:  # first rounds are ignored because unmeaningful peaks are reached at this moment
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

    # ##########################################################################################
    # Final operations
    # ##########################################################################################

    def final_process(self):
        if self._type == "global":  # if global values are wanted
            file = open(self._path+self._filename+__text_extension__, "a+")

            for key in self._buffer:
                file.write(f"for the key {key}:\n")
                file.write(f"\tmean: {self._buffer[key]['mean']}\n")
                file.write(f"\tmin: {self._buffer[key]['min']}\n")
                file.write(f"\tmax: {self._buffer[key]['max']}\n")
                file.write(f"\tsum: {self._buffer[key]['sum']}\n")
                file.write("\n")

            file.close()

        elif self._type == "month":
            file = open(self._path + self._filename + __text_extension__, "a+")
            for key in self._list:

                value = self._list[key](key)

                # values saving for the figures
                if key in self._x_values:
                    self._x_values[key]["values"].append(value)
                if key in self._y_values:
                    self._y_values[key]["values"].append(value)

                if key in self._buffer:
                    file.write(f"{self._buffer[key]['mean']}\t"  # saves the mean
                               f"{self._buffer[key]['min']}\t"  # saves the min
                               f"{self._buffer[key]['max']}\t"  # saves the max
                               f"{self._buffer[key]['sum']}\t"
                               )

                    self._buffer[key] = {"mean": 0, "min": inf, "max": -inf, "sum": 0, "active_rounds": 1}
                else:
                    file.write(f"{value}\t")

    def final_export(self):  # call the relevant export functions
        export(self._graph_options, self._path + self._filename, self._x_values, self._y_values, self._graph_labels)

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
