# management of the creation of a case directory
import os
import datetime


class CaseDirectory:

    def __init__(self, path):
        instant_date = datetime.datetime.now()  # get the current time
        instant_date = instant_date.strftime("%d_%m_%Y-%H_%M_%S")
        # put it into an adapted format
        self._date = instant_date  # keep it for later

        self._path = path + "/Case" + self._date  # path is the root for all the files relative to the case
        # It is named after the date

        self._catalog = None

    def create(self):  # create a directory corresponding to the specified file
        os.makedirs(self._path)
        os.makedirs(f"{self._path}/inputs")
        os.makedirs(f"{self._path}/outputs")

        self._catalog.add("path", self._path)

