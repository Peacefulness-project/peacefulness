# This sheet regroups all the subclasses of producers


# This subclass represents the main grid
# It corresponds to a producer of an infinite capacity
class MainGrid(Producer):

    def __init__(self, nature):
        Producer.__init__(self, nature)
        self.energy = mt.inf

    def update(self, world):
        pass

    def create(cls, n, dict_name, base_of_name, nature):
        Producer.create(n, dict_name, base_of_name, nature)

    create = classmethod(create)


# This subclass corresponds to PV panels
class PV(Producer):

    def __init__(self, nature):
        Producer.__init__(self, nature)

    def update(self, world):
        prod = [42, 42, 69]
        self.energy = prod[world.current_time]
        print('pouet', world.current_time, self.energy)

    def create(cls, n, dict_name, base_of_name, nature):
        Producer.create(n, dict_name, base_of_name, nature)

        for i in range(n):
            name = base_of_name + '_' + str(i)
            dict_name[name] = cls(nature)

    create = classmethod(create)


# This subclass corresponds to wind turbines
class WindTurbine(Producer):

    def __init__(self, nature):
        Producer.__init__(self, nature)

    def update(self, world):
        pass

    def create(cls, n, dict_name, base_of_name, nature):
        Producer.create(n, dict_name, base_of_name, nature)

        for i in range(n):
            name = base_of_name + '_' + str(i)
            dict_name[name] = cls(nature)

    create = classmethod(create)
