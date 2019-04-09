from common.Core import Producer

# This subclass corresponds to PV panels
class PV(Producer):

    def __init__(self, nature):
        Producer.__init__(self, nature)

# ##########################################################################################
# Entity management
# ##########################################################################################

    # def create(cls, n, dict_name, base_of_name, nature):
    #     Producer.create(n, dict_name, base_of_name, nature)
    #
    #     for i in range(n):
    #         name = base_of_name + '_' + str(i)
    #         dict_name[name] = cls(nature)
    #
    # create = classmethod(create)

# ##########################################################################################
# Dynamic behaviour
# ##########################################################################################

    def update(self, world):  # update the data to the current time step
        print("Update")
        #prod = [42, 42, 69]
        #self.energy = prod[world.current_time]
        #print('pouet', world.current_time, self.energy)

    def register(self, catalog):  # create a key in our catalog, without assigning a value
        catalog.add(f"{self.name}.price", None)
