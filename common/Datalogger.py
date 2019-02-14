# Dataloggers role is to write desired data in a file at a given frequency
from tools.Utilities import list_to_str
from tools.DataProcessingFunctions import *


class Datalogger:

    def __init__(self, name, filename, period=0):
        self._name = name
        self._catalog = None  # catalog from which data are extracted
        self._filename = filename
        self._period = period  # frequency of writing in the file
        self._data_dict = dict()  # this dictionary associates keys with the
        # desired operation

        # initially, 5 operations are defined:
        self._data_dict[""] = [[], [], identity]  # this basic operation
        # returns the raw value
        self._data_dict["sum"] = [[], [], sum_over_time, []]  # sum a value over the
        # time. first list = headers, second list = keys to sum, third list = current sum
        # /!\ sums only at each period
        self._data_dict["mean"] = [[], [], mean]  # make the mean between the specified keys
        self._data_dict["min"] = [[], [], data_min]
        self._data_dict["max"] = [[], [], data_max]

        self._next_time = 0  # next time step for which data will be written

# ##########################################################################################
# Initialization
# ##########################################################################################

    def add(self, name, operation="", header=""):  # add 1 key of the catalog to
        # the datalogger
        if operation not in self._data_dict:  # checking if the operation already exists
            raise DataLoggerException(f"operation {name} does not exist")
        self.headers(operation).append(header)
        self.keys(operation).append(name)

# methode pour enlever les donnees ? pour simplifier quand on veut tout sauf une ou deux lignes ?

    def add_all(self, operation="", header=""):  # add all keys from the catalog to
        # the datalogger
        for name in self._catalog.keys:
            self.headers(operation).append(header)
            self.keys(operation).append(name)

    def add_operation(self, operation, function, complement=None):
        if operation in self._data_dict:  # checking if the operation already exists
            raise DataLoggerException(f"operation {operation} already exists")
        self._data_dict[operation] = [[], [], function, complement]

# ##########################################################################################
# Writing in the file
# ##########################################################################################

    def launch(self, time):  # write data at the given frequency
        if time >= self._next_time:  # data is saved only if the current time is a
            # multiple of the defined period
            if time == 0:  # initialization of the file
                self._save_header()  # name of each piece of data is written at the top of
                # the file
            self._save()
            self._next_time += self._period  # update of the next time for writing

    def _save(self):  # write all the chosen data in the catalog on a line
        file = open(self._filename, 'a+')
        for operation in self._data_dict:
            if self.headers(operation) != []:
                        processed_data = self.function(operation)(self._data_dict[operation], self._catalog)
                        file.write(f"{list_to_str(processed_data)}\t")
        file.write("\n")
        file.close()

    def _save_header(self):  # create the headers of the column
        file = open(self._filename, 'w')
        for operation in self._data_dict:
            for i in range(len(self.headers(operation))):  # for each piece of data, the corresponding is written
                # in the file as a column header
                if self.headers(operation)[i] is "":
                    file.write(f"{operation}_{str(self.keys(operation)[i])}\t")
                else:
                    file.write(f"{self.headers(operation)[i]}\t")
        file.write("\n")
        file.close()

# ##########################################################################################
# Utilities
# ##########################################################################################

    def headers(self, operation=""):
        return self._data_dict[operation][0]

    def keys(self, operation=""):
        return self._data_dict[operation][1]

    def function(self, operation):
        return self._data_dict[operation][2]

    def set_catalog(self, catalog):
        self._catalog = catalog

    @property
    def name(self):
        return self._name


# Exception
class DataLoggerException(Exception):
    def __init__(self, message):
        super().__init__(message)

