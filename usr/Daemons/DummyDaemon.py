from common.Daemon import Daemon


class DummyDaemon(Daemon):

    def __init__(self, name, period, parameters):
        super().__init__(name, period, parameters)

    def _user_register(self):
        self._catalog.add("tick", 0)

    def _process(self):
        tick = self.catalog.get("tick")
        self.catalog.set("tick", tick+1)

