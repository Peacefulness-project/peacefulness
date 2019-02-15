from common.Daemon import Deamon


class DummyDeamon(Deamon):
    def __init__(self, name, period):
        super().__init__(name, period)

    def init(self):
        self._catalog.add("tick", 0)

    def process(self):
        tick = self.catalog.get("tick")
        self.catalog.set("tick", tick+1)

