# This sheet regroups all the subclasses of consumers


# The "Baseload" class regroups all applications which are non schedulable...
# ... i.e all non-interruptible and always primary for the grid
# It contains lights, TVs, computers, ovens, refrigerators, etc
class Baseload(Consumer):

    def __init__(self, nature=''):
        Consumer.__init__(self, nature, 0)  # always primary, non-interruptible

    def update(self, world):
        conso = [42, 69, 42]  # consommation de test
        self.energy = conso[world.current_time]

    def create(cls, n, dict_name, base_of_name, nature):
        Consumer.create(n, dict_name, base_of_name, nature)

        for i in range(n):
            name = base_of_name + '_' + str(i)
            dict_name[name] = cls(nature)

    create = classmethod(create)


# This subclass corresponds to heating and cooling devices
class Heating(Consumer):

    def __init__(self, nature='', ):
        Consumer.__init__(self, nature)
        self.objective_temperature = -1  # User-defined temperature in °C
        # Negative temperature means that nothing is required
        self.indoor_temperature = 0  # temperature indoor in °C

    def update(self, world):
        pass

    def create(cls, n, dict_name, base_of_name, nature):
        Consumer.create(n, dict_name, base_of_name, nature)

        for i in range(n):
            name = base_of_name + '_' + str(i)
            dict_name[name] = cls(nature)

    create = classmethod(create)
