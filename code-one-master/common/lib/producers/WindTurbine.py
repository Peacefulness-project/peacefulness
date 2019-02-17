from common.Core import Producer

# This subclass corresponds to wind turbines
class WindTurbine(Producer):

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

    def update(self, world):
        print("Update")

    def register(self, catalog):  # create a key in our catalog, without assigning a value
        catalog.add(f"{self.name}.price", None)
