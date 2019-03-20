# management of the creation of a case directory
import os
import datetime
from tools.Utilities import adapt_path  # this function allows to choose / or \ in a path accordingly to user os


class CaseDirectory:

    def __init__(self, path):
        instant_date = datetime.datetime.now()  # get the current time
        instant_date = instant_date.strftime("%d_%m_%Y-%H_%M_%S")  # the directory is named after the date

        self._path = adapt_path([path, f"Case_{instant_date}"])  # path is the root for all files relative to the case
        # It is named after the date

        self._catalog = None

    def create(self):  # create a directory corresponding to the specified file (and adapted to the os)
        os.makedirs(self._path)
        os.makedirs(adapt_path([self._path, "inputs"]))
        os.makedirs(adapt_path([self._path, "outputs"]))

        self._catalog.add("path", self._path)

    def _add_catalog(self, catalog):  # add a catalog
        self._catalog = catalog

