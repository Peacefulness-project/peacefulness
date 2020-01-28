from common.Daemon import Daemon
from tools.UserClassesDictionary import user_classes_dictionary


class DummyDaemon(Daemon):

    def __init__(self, name, period, parameters=None):
        super().__init__(name, period, parameters)

    def _user_register(self):
        self._catalog.add("tick", 0)

    def _process(self):
        tick = self.catalog.get("tick")
        self.catalog.set("tick", tick+1)


user_classes_dictionary[f"{DummyDaemon.__name__}"] = DummyDaemon

