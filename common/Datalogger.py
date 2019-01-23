# Dataloggers role is to write desired data in a file at a given frequency


class Datalogger:

    def __init__(self, catalog, filename, period=0):
        self._catalog = catalog  # catalog from which data are extracted
        self._filename = filename
        self._period = period  # frequency of writing in the file
        self._list = []  # contain the data we want to extract from the catalog
        self._next_time = 0  # next time step for which data will be written

# ##########################################################################################
# Initialization
# ##########################################################################################

    def add(self, name):  # add 1 key of the catalog to the datalogger
        self._list.append(name)

# methode pour enlever les donnees ? pour simplifier quand on veut tout sauf une ou deux lignes ?

    def add_all(self):  # add all keys from the catalog to the datalogger
        for name in self._catalog.keys:
            self._list.append(name)

# ##########################################################################################
# Writing in the file
# ##########################################################################################

    def process(self, time):  # write data at the given frequency
        if time >= self._next_time:
            if time == 0:
                self._save_header()
            self._save()
            self._next_time += self._period

    def _save(self):  # write all the data in the catalog on a line
        file = open(self._filename, 'a+')
        for key in self._list:
            file.write(f"{self._catalog.get(key)}\t")
        file.write("\n")
        file.close()

    def _save_header(self):  # create the headers of the column
        file = open(self._filename, 'w')
        for key in self._list:
            file.write(key+"\t")
        file.write("\n")
        file.close()

# Exception
