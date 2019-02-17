from common.Core import Consumer, Producer


class DummyConsumer(Consumer):

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

    def register(self):  # create a key in our catalog, without assigning a value
        self._catalog.add(f"{self.name}.priority", None)


class DummyProducer(Producer):

    def __init__(self, name):
        super().__init__(name)

# ##########################################################################################
# Entity management
# ##########################################################################################

#    def create(cls, n, dict_name, base_of_name, nature):
#        Consumer.create(n, dict_name, base_of_name, nature)
#
#        for i in range(n):
#           name = base_of_name + '_' + str(i)
#           dict_name[name] = cls(nature)
#
#   create = classmethod(create)

# ##########################################################################################
# Dynamic behaviour
# ##########################################################################################

    def update(self, world):  # update the data to the current time step
        print("Update")

    def register(self):  # create a key in our catalog, without assigning a value
        self._catalog.add(f"{self.name}.price", None)
