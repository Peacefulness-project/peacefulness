# ##############################################################################################
# Native packages
import numpy as np
# Current packages
from common.Core import Consumption, Production


class DummyConsumption(Consumption):

    def __init__(self, name, grid_name, agent_name, filename, cluster_name=None):
        super().__init__(name, "LVE", grid_name, agent_name, cluster_name)

        self._NomQuiPlairaPasAStephane = np.zeros((365, 24))
        self._filename = filename  # the name of the data file

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        self._NomQuiPlairaPasAStephane = np.loadtxt(self._filename, delimiter="\t")

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # update the data to the current time step
        self._catalog.set(f"{self._name}.energy", 1)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, grid_name, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyConsumption(entity_name, grid_name, agent_name, filename, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


class DummyShiftableConsumption(Consumption):  # a consumption which is shiftable

    def __init__(self, name, grid_name, agent_name, filename, cluster_name=None):
        super().__init__(name, "LVE", grid_name, agent_name, cluster_name)

        self._NomQuiPlairaPasAStephane = []  # the list containing the scheduled periods of work
        self._filename = filename  # the name of the data file

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        file = open(self._filename, "r")
        file = file.read()
        file = file.split("\n")
        file.remove('')

        for line in file:  # converting the file into floats
            line = line.split("  ")
            line[0] = float(line[0])  # early start date
            line[1] = float(line[1])  # last start date
            line[2] = line[2].strip("[]")
            line[2] = line[2].split(", ")
            line[2] = [float(element) for element in line[2]]  # consumption once started

            self._NomQuiPlairaPasAStephane.append(line)  # each line corresponds to one use

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # update the data to the current time step
        self._catalog.set(f"{self._name}.energy", 1)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, grid_name, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyShiftableConsumption(entity_name, grid_name, agent_name, filename, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


class DummyProduction(Production):

    def __init__(self, name, grid_name, agent_name, filename, cluster_name=None):
        super().__init__(name, "LVE", grid_name, agent_name, cluster_name)

        self._NomQuiPlairaPasAStephane = []  # the list containing the scheduled periods of work
        self._filename = filename  # the name of the data file

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        self._NomQuiPlairaPasAStephane = np.loadtxt(self._filename, delimiter="\t")

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _update(self):  # update the data to the current time step
        self._catalog.set(f"{self._name}.energy", 1)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, grid_name, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyProduction(entity_name, grid_name, agent_name, filename, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)

