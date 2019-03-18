from common.Core import Consumption, Production


class DummyConsumption(Consumption):

    def __init__(self, name):
        super().__init__(name, "LVE")

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def register(self):  # make the initialization operations undoable without a catalog
        self.register_consumption()  # make the operations relevant for all kind of consumption points

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self):  # update the data to the current time step
        self._catalog.set(f"{self._name}.energy", 1)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyConsumption(entity_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


class DummyProduction(Production):

    def __init__(self, name):
        super().__init__(name, "LVE")

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def register(self):  # make the initialization operations undoable without a catalog
        self.register_production()  # make the operations relevant for all kind of production points

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self):  # update the data to the current time step
        self._catalog.set(f"{self._name}.energy", 1)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyProduction(entity_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)

