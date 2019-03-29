from common.Core import Consumption, Production


class DummyConsumption(Consumption):

    def __init__(self, name, grid_name, agent_name, cluster_name=None):
        super().__init__(name, "LVE", grid_name, agent_name, cluster_name)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
        self._register_consumption(catalog)  # make the operations relevant for all kind of consumption points

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _update(self):  # update the data to the current time step
        self._catalog.set(f"{self._name}.energy", 1)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, grid_name, agent_name, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyConsumption(entity_name, grid_name, agent_name, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


class DummyProduction(Production):

    def __init__(self, name, grid_name, agent_name, cluster_name=None):
        super().__init__(name, "LVE", grid_name, agent_name, cluster_name)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
        self._register_production(catalog)  # make the operations relevant for all kind of production points

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _update(self):  # update the data to the current time step
        self._catalog.set(f"{self._name}.energy", 1)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, grid_name, agent_name, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyProduction(entity_name, grid_name, agent_name, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)

