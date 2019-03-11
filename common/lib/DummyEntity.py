from common.Core import Consumption, Production


class DummyConsumption(Consumption):

    def __init__(self, name):
        super().__init__(name, "LVE")

# ##########################################################################################
# Entity management
# ##########################################################################################

    def mass_create(cls, n, name, world):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyConsumption(entity_name)
            world.add(entity)

    mass_create = classmethod(mass_create)

# ##########################################################################################
# Dynamic behaviour
# ##########################################################################################

    def update(self):  # update the data to the current time step
        self._energy = 1

    def register(self):  # create a key in our catalog, without assigning a value
        self._catalog.add(f"{self._name}.priority", None)


class DummyProduction(Production):

    def __init__(self, name):
        super().__init__(name, "LVE")

# ##########################################################################################
# Entity management
# ##########################################################################################

    def mass_create(cls, n, name, world):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyProduction(entity_name)
            world.add(entity)

    mass_create = classmethod(mass_create)

# ##########################################################################################
# Dynamic behaviour
# ##########################################################################################

    def update(self):  # update the data to the current time step
        self._energy = 1

    def register(self):  # create a key in our catalog, without assigning a value
        self._catalog.add(f"{self._name}.price", None)

