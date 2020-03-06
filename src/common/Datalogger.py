# Datalogger role is to write desired data in a file at a given frequency
# from tools.Utilities import list_to_str
# from tools.DataProcessingFunctions import *

from numpy import mean

from src.tools.Utilities import adapt_path


class Datalogger:

    def __init__(self, name, filename, period=0, sum_over_time=False):
        self._name = name

        self._filename = filename  # the name of the file where the data will be written
        self._period = period  # number of rounds between 2 activations
        self._sum = sum_over_time  # enables integration of a data between 2 periods

        self._list = []  # list of catalog keys which has to be written

        self._buffer = dict()  # dict which stores data between each period of registering
        # allows to report info such as mean, min and max between two periods

        self._next_time = 0  # next time step for which data will be written

        self._catalog = None  # catalog from which data is extracted

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog

    def add(self, name):  # add 1 key of the catalog to the datalogger
        self._list.append(name)  # creates an entry in the buffer if needed

        if (type(self._catalog.get(name)) == float) and (self._period > 1):  # numeric keys are added to a buffer
            # it allows to return the mean, the min and the max
            self._buffer[name] = []  # creates an entry in the buffer

    def add_all(self):  # add all keys from the catalog to the datalogger
        for name in self._catalog.keys:
            self._list.append(name)  # creates an entry in the buffer if needed

            if (type(self._catalog.get(name)) == float) and (self._period > 1):  # numeric keys are added to a buffer
                # it allows to return the mean, the min and the max
                self._buffer[name] = []  # creates an entry in the buffer if needed

    # ##########################################################################################
    # Data processing
    # ##########################################################################################

    def _data_processing(self, key):  # function which returns the mean, the min and the max of a key between 2 periods
        processed_data = list()
        processed_data.append(mean(self._buffer[key]))  # mean
        processed_data.append(min(self._buffer[key]))  # min
        processed_data.append(max(self._buffer[key]))  # max
        return processed_data

    def _data_sum(self, name):  # if enabled, return the sum of the value over the time
        return sum(self._buffer[name])

    # ##########################################################################################
    # Writing in the file
    # ##########################################################################################

    def launch(self):  # write data at the given frequency
        current_time = self._catalog.get("simulation_time")  # the simulation time allows to know if it has to be called or not

        if self._period > 1:
            for key in self._buffer:  # for all relevant keys
                self._buffer[key].append(self._catalog.get(key))  # value is saved in the buffer
        if current_time >= self._next_time:  # data is saved only if the current time is a multiple of the defined period

            if current_time == 0:  # initialization of the file
                self._save_header()  # name of each piece of data is written at the top of the file
            self._save()  # writes the data in the file
            self._next_time += self._period  # calculates the next period of writing

    def _save(self):  # write all the chosen data in the catalog on a line
        file = open(adapt_path([self._catalog.get("path"), "outputs", self._filename]), "a+")

        for key in self._list:
            file.write(f"{self._catalog.get(key)}\t")
            if (type(self._catalog.get(key)) == float) and (self._period > 1):
                processed_data = self._data_processing(key)  # = [mean, min, max]
                file.write(f"{processed_data[0]}\t"  # saves the mean
                           f"{processed_data[1]}\t"  # saves the min
                           f"{processed_data[2]}\t"  # saves the max
                           )
                if self._sum:  # if sum is enabled, write the sum of the data over the time
                    file.write(f"{self._data_sum(key)}\t")
            self._buffer[key] = []  # Reinitialization of the buffer
        file.write("\n")
        file.close()

    def _save_header(self):  # create the headers of the column
        file = open(adapt_path([self._catalog.get('path'), "outputs", self._filename]), 'a+')

        for name in self._list:
            file.write(f"{name}\t")

            if name in self._buffer:
                file.write(f"Mean_{name}\t"
                           f"Min_{name}\t"
                           f"Max_{name}\t")
                if self._sum:  # if sum is enabled, add it to the file
                    file.write(f"Sum_{name}\t")
        file.write("\n")
        file.close()

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
