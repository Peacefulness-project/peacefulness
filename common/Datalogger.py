# Dataloggers role is to write desired data in a file at a given frequency
# from tools.Utilities import list_to_str
# from tools.DataProcessingFunctions import *

import numpy as np


class Datalogger:

    def __init__(self, name, filename, period=0, sum_over_time=False):
        self._name = name
        self._catalog = None  # catalog from which data are extracted
        self._filename = filename
        self._period = period  # frequency of writing in the file
        self._sum = sum_over_time
        # self._data_dict = dict()  # this dictionary associates keys with the
        # # desired operation

        self._list = []  # list of catalog keys which has to be written

        self._buffer = dict()  # dict which stores data between two periods
        # allows to report info such as mean, min and max between two periods

        # # initially, 5 operations are defined:
        # self._data_dict[""] = [[], [], identity]  # this basic operation
        # # returns the raw value
        # self._data_dict["sum"] = [[], [], sum_over_time, []]  # sum a value over the
        # # time. first list = headers, second list = keys to sum, third list = current sum
        # # /!\ sums only at each period
        # self._data_dict["mean"] = [[], [], mean]  # make the mean between the specified keys
        # self._data_dict["min"] = [[], [], data_min]
        # self._data_dict["max"] = [[], [], data_max]

        self._next_time = 0  # next time step for which data will be written

# ##########################################################################################
# Initialization
# ##########################################################################################

    def add(self, name):  # add 1 key of the catalog to
        # the datalogger
        self._list.append(name)
        self._buffer[name] = []

        # if operation not in self._data_dict:  # checking if the operation already exists
        #     raise DataLoggerException(f"operation {name} does not exist")
        # self.headers(operation).append(header)
        # self.keys(operation).append(name)


# methode pour enlever les donnees ? pour simplifier quand on veut tout sauf une ou deux lignes ?

    def add_all(self):  # add all keys from the catalog to
        # the datalogger
        for name in self._catalog.keys:
            self._list.append(name)
            self._buffer[name] = []
            # self.headers(operation).append(header)
            # self.keys(operation).append(name)

    # def add_operation(self, operation, function, complement=None):
    #     if operation in self._data_dict:  # checking if the operation already exists
    #         raise DataLoggerException(f"operation {operation} already exists")
    #     self._data_dict[operation] = [[], [], function, complement]

# ##########################################################################################
# Data processing
# ##########################################################################################

    def data_processing(self, key):
        processed_data = list()
        processed_data.append(np.mean(self._buffer[key]))
        processed_data.append(min(self._buffer[key]))
        processed_data.append(max(self._buffer[key]))
        return processed_data

    def data_sum(self, name):
        return sum(self._buffer[name])

# ##########################################################################################
# Writing in the file
# ##########################################################################################

    def launch(self, time):  # write data at the given frequency
        if self._period > 1:
            for key in self._list:
                if type(self._catalog.get(key)) == float:
                    self._buffer[key].append(self._catalog.get(key))
        if time >= self._next_time:  # data is saved only if the current time is a
            # multiple of the defined period
            if time == 0:  # initialization of the file
                self._save_header()  # name of each piece of data is written at the top of
                # the file
            self._save()
            self._next_time += self._period  # update of the next time for writing

    def _save(self):  # write all the chosen data in the catalog on a line
        file = open(self._filename, 'a+')
        # for operation in self._data_dict:
        #     if self.headers(operation) != []:
        #                 processed_data = self.function(operation)(self._data_dict[operation], self._catalog)
        #                 file.write(f"{list_to_str(processed_data)}\t")

        for key in self._list:
            file.write(f"{self._catalog.get(key)}\t")
            if (type(self._catalog.get(key)) == float) and (self._period > 1):
                processed_data = self.data_processing(key)
                file.write(f"{processed_data[0]}\t"
                           f"{processed_data[1]}\t"
                           f"{processed_data[2]}\t")
                if self._sum:
                    file.write(f"{self.data_sum(key)}\t")
            self._buffer[key] = []  # Reinitialization of the buffer
        file.write("\n")
        file.close()

    def _save_header(self):  # create the headers of the column
        file = open(self._filename, 'w')
        # for operation in self._data_dict:
        #     for i in range(len(self.headers(operation))):  # for each piece of data, the
        #         # corresponding is written in the file as a column header
        #         if self.headers(operation)[i] is "":
        #             file.write(f"{operation}_{str(self.keys(operation)[i])}\t")
        #         else:
        #             file.write(f"{self.headers(operation)[i]}\t")

        for name in self._list:
            file.write(f"{name}\t")
            if (type(self._catalog.get(name)) == float) and (self._period > 1):
                file.write(f"Mean_{name}\t"
                           f"Min_{name}\t"
                           f"Max_{name}\t")
                if self._sum:
                    file.write(f"sum_{name}\t")
        file.write("\n")
        file.close()

# ##########################################################################################
# Utilities
# ##########################################################################################

    # def headers(self, operation=""):
    #     return self._data_dict[operation][0]
    #
    # def keys(self, operation=""):
    #     return self._data_dict[operation][1]
    #
    # def function(self, operation):
    #     return self._data_dict[operation][2]

    @property
    def name(self):
        return self._name


# Exception
class DataLoggerException(Exception):
    def __init__(self, message):
        super().__init__(message)

