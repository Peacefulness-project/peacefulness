from common.Core import Consumption


# This subclass corresponds to heating and cooling devices
class Heating(Consumption):

    def __init__(self, name):
        super().__init__(name)
        self.objective_temperature = -1  # User-defined temperature in °C
        # Negative temperature means that nothing is required
        self.indoor_temperature = 0  # temperature indoor in °C

# ##########################################################################################
# Entity management
# ##########################################################################################

#   def create(cls, n, dict_name, base_of_name, nature):
#       Consumer.create(n, dict_name, base_of_name, nature)
#
#       for i in range(n):
#           name = base_of_name + '_' + str(i)
#           dict_name[name] = cls(nature)
#
#   create = classmethod(create)

# ##########################################################################################
# Dynamic behaviour
# ##########################################################################################

    def update(self, world):  # update the data to the current time step
        print("Update")

    def register(self, catalog):  # create a key in our catalog, without assigning a value
        catalog.add(f"{self.name}.priority", None)
