# This sheet regroups all the subclasses of consumptions
from common.Core import Consumer


# The "Baseload" class regroups all applications which are non schedulable...
# ... i.e all non-interruptible and always primary for the grid
# It contains lights, TVs, computers, ovens, refrigerators, etc
class Baseload(Consumer):

    def __init__(self, name):
        super().__init__(name)

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
        #conso = [42, 69, 42]  # consommation de test
        #self.energy = conso[world.current_time]

    def register(self, catalog):  # create a key in our catalog, without assigning a value
        catalog.add(f"{self.name}.priority", None)

