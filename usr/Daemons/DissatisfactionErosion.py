# this daemon reduces a bit, at each round, the dissatisfaction of all agents
# it takes two special arguments, residual and duration_in_hours
# the function used is f(x) = x*A where A verifies A**duration_in_hours = residual
from common.Daemon import Daemon


class DissatisfactionErosionDaemon(Daemon):
    def __init__(self, name, period, residual, duration_in_hours):
        super().__init__(name, period)
        self._coefficient = residual ** (1 / duration_in_hours)

    def _process(self):
        for key in self.catalog.keys:
            if "dissatisfaction" in key:
                new_dissatisfaction = self.catalog.get(key)*self._coefficient
                self._catalog.set(key, new_dissatisfaction)
