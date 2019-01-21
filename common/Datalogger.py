class Datalogger:

    def __init__(self, catalog, filename, period=0):
        self._catalog = catalog

        self._filename  = filename
        self._period = period

        self._list = []

        self._next_time = 0

    def add(self,name):
        self._list.append(name)

    def add_all(self):
        for name in self._catalog.keys:
            self._list.append(name)


    def process(self,time):
        if time>=self._next_time:
            if time==0:
                self._save_header()
            self._save()
            self._next_time += self._period


    def _save(self):
        file = open(self._filename, 'a+')
        for key in self._list:
            file.write(f"{self._catalog.get(key)}\t")
        file.write("\n")
        file.close()


    def _save_header(self):
        file = open(self._filename, 'w')
        for key in self._list:
            file.write(key+"\t")
        file.write("\n")
        file.close()