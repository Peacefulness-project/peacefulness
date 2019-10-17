# this daemon reduces a bit, at each round, the dissatisfaction of all agents
# it takes two special arguments, residual and duration_in_hours
# the function used is f(x) = x*A where A verifies A**duration_in_hours = residual
from common.Daemon import Daemon
from tools.UserClassesDictionary import user_classes_dictionary


class DissatisfactionErosionDaemon(Daemon):

    def __init__(self, name, period,  parameters):
        super().__init__(name, period, parameters)
        self._coefficient = parameters["coef_1"] ** (1 / parameters["coef_2"])

    def _process(self):
        for key in self.catalog.keys:
            if "dissatisfaction" in key:
                new_dissatisfaction = self.catalog.get(key)*self._coefficient
                self._catalog.set(key, new_dissatisfaction)


user_classes_dictionary[f"{DissatisfactionErosionDaemon.__name__}"] = DissatisfactionErosionDaemon

