# ##############################################################################################
# Native packages
import numpy as np
import datetime as dt
# Current packages
from common.Core import Consumption, Production
from tools.Utilities import check_zero_one


class DummyConsumption(Consumption):

    def __init__(self, name, max_energy, grid_name, agent_name, filename, cluster_name=None):
        super().__init__(name, "LVE", max_energy, grid_name, agent_name, cluster_name)

        self._NomQuiPlairaPasAStephane = np.zeros((365, 24))
        self._filename = filename  # the name of the data file

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        self._NomQuiPlairaPasAStephane = np.loadtxt(self._filename, delimiter="\t")
        check_zero_one(self._NomQuiPlairaPasAStephane)  # check if all data belong to [0,1]

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # update the data to the current time step

        # getting the current moment as a datetime format
        current_time = self._catalog.get("physical_time")
        # the line of the data corresponds to the number of the day in the year
        # getting the number of the day in the year
        current_year = current_time.year
        current_year = dt.datetime(year=current_year, month=1, day=1)
        current_day = current_time - current_year  # getting the duration between 01/01 and the current date
        current_day = current_day.days  # converting this duration in days
        # the column of the data corresponds to the hour in the day
        # getting the current hour
        current_hour = current_time.hour

        current_consumption = self._NomQuiPlairaPasAStephane[current_day][current_hour] * self.max_energy
        self._catalog.set(f"{self._name}.energy", current_consumption)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, max_energy, world, grid_name, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyConsumption(entity_name, max_energy, grid_name, agent_name, filename, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


class DummyShiftableConsumption(Consumption):  # a consumption which is shiftable

    def __init__(self, name, max_energy, grid_name, agent_name, filename, cluster_name=None):
        super().__init__(name, "LVE", max_energy, grid_name, agent_name, cluster_name)

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

            check_zero_one(self._NomQuiPlairaPasAStephane[len(self._NomQuiPlairaPasAStephane)-1][2])  # check if all data belong to [0,1]

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # update the data to the current time step
        self._catalog.set(f"{self._name}.energy", 1)

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, max_energy, world, grid_name, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyShiftableConsumption(entity_name, max_energy, grid_name, agent_name, filename, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


class DummyAdjustableConsumption(Consumption):  # a consumption which is adjustable

    def __init__(self, name, max_energy, grid_name, agent_name, filename, cluster_name=None):
        super().__init__(name, "LVE", max_energy, grid_name, agent_name, cluster_name)

        self._NomQuiPlairaPasAStephane = []  # the list containing the scheduled periods of work
        self._filename = filename  # the name of the data file

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        # reading the data file
        file = open(self._filename, "r")
        file = file.read()
        file = file.split("\n")
        file.remove('')

        for line in file:  # converting the file into floats
            line = line.split("  ")
            line[0] = float(line[0])  # start date
            line[1] = line[1].strip("[]")
            line[1] = line[1].split(", ")
            line[1] = [float(element) for element in line[1]]  # consumption once started

            self._NomQuiPlairaPasAStephane.append(line)  # each line corresponds to one use

            check_zero_one(self._NomQuiPlairaPasAStephane[len(self._NomQuiPlairaPasAStephane)-1][1])  # check if all data belong to [0,1]

        # specific entries
        self._catalog.add(f"{self._name}.completeness", 0)  # the completeness of a usage

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # update the data to the current time step

        # getting the current moment as a datetime format
        current_time = self._catalog.get("physical_time")
        # the line of the data corresponds to the number of the day in the year
        # getting the number of the day in the year
        current_year = current_time.year
        current_year = dt.datetime(year=current_year, month=1, day=1)
        current_hour = current_time - current_year  # getting the duration between 01/01 and the current date
        current_hour = current_hour.seconds // 3600  # converting this duration in days

        # regler probleme doublons
        for use in self._NomQuiPlairaPasAStephane:
            if use[0] == current_hour:
                pass  # do smthg

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, max_energy, world, grid_name, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyShiftableConsumption(entity_name, max_energy, grid_name, agent_name, filename, cluster_name)
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
        check_zero_one(self._NomQuiPlairaPasAStephane)  # check if all data belong to [0,1]

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

