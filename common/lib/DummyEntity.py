from common.Core import Consumer, Producer


class DummyConsumer(Consumer):

    def __init__(self, name):
        super().__init__(name)  # always primary, non-interruptible

    def update(self, world):
        print("Update")
#        conso = [42, 69, 42]  # consommation de test
#        self.energy = conso[world.current_time]

    def register(self,catalog):
        catalog.add(f"{self.name}.priority",None)

#    def create(cls, n, dict_name, base_of_name, nature):
#        Consumer.create(n, dict_name, base_of_name, nature)
#
 #       for i in range(n):
  #          name = base_of_name + '_' + str(i)
   #         dict_name[name] = cls(nature)

   # create = classmethod(create)



class DummyProducer(Producer):

    def __init__(self, name):
        super().__init__(name)  # always primary, non-interruptible

    def update(self, world):
        print("Update")

    def register(self,catalog):
        catalog.add(f"{self.name}.price",None)


#        conso = [42, 69, 42]  # consommation de test
#        self.energy = conso[world.current_time]

#    def create(cls, n, dict_name, base_of_name, nature):
#        Consumer.create(n, dict_name, base_of_name, nature)
#
 #       for i in range(n):
  #          name = base_of_name + '_' + str(i)
   #         dict_name[name] = cls(nature)

   # create = classmethod(create)
