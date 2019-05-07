# ##############################################################################################
# Native packages
import numpy as np
import datetime as dt
# Current packages
from common.Core import Device


class DummyConsumption(Device):

    def __init__(self, name, natures, agent_name, filename, cluster_names=None):
        super().__init__(name, natures, agent_name, cluster_names)

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

    def _update(self):  # method updating needs of the devices before the supervision

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

        current_consumption = self._NomQuiPlairaPasAStephane[current_day][current_hour]

        for nature in self.natures:
            self._catalog.set(f"{self.name}.{nature.name}.asked_energy", current_consumption)

    def react(self):  # method updating the device according to the decisions taken by the supervisor
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, natures, world, agent_name, filename, cluster_name=None):
        for i in range(n):
            device_name = f"{name}_{str(i)}"
            device = DummyConsumption(device_name, natures, agent_name, filename, cluster_name)
            world.register_device(device)

    mass_create = classmethod(mass_create)


class DummyShiftableConsumption(Device):  # a consumption which is shiftable

    def __init__(self, name, natures, agent_name, filename, cluster_names=None):
        super().__init__(name, natures, agent_name, cluster_names)

        self._NomQuiPlairaPasAStephane = list()  # the list containing the scheduled periods of work
        self._filename = filename  # the name of the data file

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._current_line = None  # this counter saves the line corresponding to the ongoing use

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

            # recovering the consumption over time
            line[2] = line[2].strip("[]")
            line[2] = line[2].split(", ")
            line[2] = [float(element) for element in line[2]]  # consumption once started

            self._NomQuiPlairaPasAStephane.append(line)  # each line corresponds to one use

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # method updating needs of the devices before the supervision

        # getting the current moment as a datetime format
        current_time = self._catalog.get("physical_time")
        # the line of the data corresponds to the number of the day in the year
        # getting the number of the day in the year
        current_year = current_time.year
        current_year = dt.datetime(year=current_year, month=1, day=1)
        current_hour = current_time - current_year  # getting the duration between 01/01 and the current date
        current_hour = current_hour.days*24 + current_hour.seconds // 3600  # converting this duration in hours

        if self._remaining_time == 0:  # if the device is not running

            for data in self._NomQuiPlairaPasAStephane:
                if data[0] <= current_hour <= data[1]:  # if the current hour belongs to an interval

                    for nature in self._natures:
                        self._catalog.set(f"{self.name}.{nature.name}.asked_energy", data[2][0])  # what the device asks

                    # calculus of the priority
                    priority = (current_hour - data[0]) / (data[1] - data[0])
                    self._catalog.set(f"{self.name}.priority", priority)

                    self._current_line = self._NomQuiPlairaPasAStephane.index(data)  # saving the line of data
                pass    # this means the "for" ends, no matter if other uses would have been relevant,
                        # as this is a problem in the construction of the data file

        else:  # if the device is running
            for nature in self._natures:
                data = self._NomQuiPlairaPasAStephane[self._current_line]
                self._catalog.set(f"{self.name}.{nature.name}.asked_energy", data[2][-self._remaining_time])

    def react(self):

        if self._current_line is not None:  # if there is a need ongoing
            data = self._NomQuiPlairaPasAStephane[self._current_line]

            if self._remaining_time == 0:  # if the device is not running
                for nature in self._natures:
                    if self._catalog.get(f"{self.name}.{nature.name}.asked_energy") == data[2][0]:
                        # if it has been served
                        self._remaining_time = len(data[2]) - 1  # setting the remaining time of use
                        self._catalog.set(f"{self.name}.priority", 1)  # its priority is blocked to 1 (can't be interrupted)

                    else:  # if it has not been served
                        dissatisfaction = self._catalog.get(f"{self.agent.name}.dissatisfaction") + 1
                        self._catalog.set(f"{self.agent.name}.dissatisfaction", dissatisfaction)  # dissatisfaction increments

            else:  # if the device is running
                self._remaining_time -= 1

                if self._remaining_time == 0:  # if the device is shut down after
                    self._catalog.set(f"{self.name}.priority", 0)  # its priority is reinitialized
                    for nature in self._natures:
                        self._catalog.set(f"{self.name}.{nature.name}.asked_energy", 0)  # its energy demand is reinitialized
                    self._current_line = None  # the current line is reinitialized

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, nature, world, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyShiftableConsumption(entity_name, nature, agent_name, filename, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


class DummyAdjustableConsumption(Device):  # a consumption which is adjustable

    def __init__(self, name, natures, agent_name, filename, cluster_names=None):
        super().__init__(name, natures, agent_name, cluster_names)

        self._NomQuiPlairaPasAStephane = []  # the list containing the scheduled periods of work
        self._filename = filename  # the name of the data file

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._current_line = None  # this counter saves the line corresponding to the ongoing use
        self._max_energy = 0  # the maximum energy the device can receive
        self._latent_demand = 0  # the energy that has not been served yet meanwhile it was asked

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        # reading the data file
        file = open(self._filename, "r")
        file = file.read()
        file = file.split("\n")

        for nature in self.natures:
            self._catalog.set(f"{self.name}.{nature.name}.max_energy", float(file[-1]))  # recovering of the max energy, on the last line
        del file[-1]  # deleting the last line

        for line in file:  # converting the file into floats
            line = line.split("  ")
            line[0] = float(line[0])  # start date

            # recovering the consumption over time
            line[1] = line[1].strip("[]")
            line[1] = line[1].split(", ")
            line[1] = [float(element) for element in line[1]]  # consumption once started

            self._NomQuiPlairaPasAStephane.append(line)  # each line corresponds to one use

        # specific entries
        self._catalog.add(f"{self._name}.completeness", 0)  # the completeness of a usage

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # method updating needs of the devices before the supervision

        if self._remaining_time == 0:  # if the device is not running

            # getting the current moment as a datetime format
            current_time = self._catalog.get("physical_time")
            # the line of the data corresponds to the number of the day in the year
            # getting the number of the day in the year
            current_year = current_time.year
            current_year = dt.datetime(year=current_year, month=1, day=1)
            current_hour = current_time - current_year  # getting the duration between 01/01 and the current date
            current_hour = current_hour.days * 24 + current_hour.seconds // 3600  # converting this duration in hours

            for data in self._NomQuiPlairaPasAStephane:
                # initialization of the use
                if data[0] == current_hour:  # if the current hour corresponds to the beginning of a use
                    self._current_line = self._NomQuiPlairaPasAStephane.index(data)  # saving the line of data
                    self._remaining_time = len(data[1])  # setting the remaining time of use
                pass    # this means the "for" ends, no matter if other uses would have been relevant,
                        # as this is a problem in the construction of the data file

        if self._remaining_time != 0:  # if the device is running
            priority = list()  # a calculus of priority is made for each nature and then the max is kept
            for nature in self._natures:
                data = self._NomQuiPlairaPasAStephane[self._current_line]
                self._catalog.set(f"{self.name}.{nature.name}.asked_energy", data[1][-self._remaining_time])  # what the device asks

                # calculus of the priority
                # what is still needed / what is possible to deliver
                if self._remaining_time == 1:  # if it is the last round
                    priority.append(1)  # priority is set to one, as it won't be possible to deliver last time
                else:
                    priority.append((sum(data[1][-self._remaining_time:]) + self._latent_demand)\
                    / (self._catalog.get(f"{self.name}.{nature.name}.max_energy") * (self._remaining_time - 1)))

            self._catalog.set(f"{self.name}.priority", min(max(priority), 1))

            self._remaining_time -= 1
            if self._remaining_time == 0:  # if the device is shut down after
                self._catalog.set(f"{self.name}.priority", 0)  # its priority is reinitialized
                for nature in self._natures:
                    self._catalog.set(f"{self.name}.{nature.name}.asked_energy", 0)  # its energy demand is reinitialized
                self._current_line = None  # the current line is reinitialized
                self._latent_demand = 0  # latent demand is reinitialized

    def react(self):  # method updating the device according to the decisions taken by the supervisor

        if self._current_line is not None:  # if there is a need ongoing
            data = self._NomQuiPlairaPasAStephane[self._current_line]

            if self._remaining_time != 0:  # if the device is running
                for nature in self._natures:
                    if self._catalog.get(f"{self.name}.{nature.name}.asked_energy") != data[1][0]:  # if it has not been served or partially
                        dissatisfaction = self._catalog.get(f"{self.agent.name}.dissatisfaction") \
                                        + self._catalog.get(f"{self.name}.{nature.name}.asked_energy") / data[1][0]  # served/asked
                        self._catalog.set(f"{self.agent.name}.dissatisfaction", dissatisfaction)  # dissatisfaction increments

                    self._latent_demand += data[1][0] - self._catalog.get(f"{self.name}.{nature.name}.asked_energy")  # latent demand is updated

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, nature, world, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyShiftableConsumption(entity_name, nature, agent_name, filename, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


class DummyProduction(Device):

    def __init__(self, name, natures, agent_name, filename, cluster_names=None):
        super().__init__(name, natures, agent_name, cluster_names)

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

    def _update(self):  # method updating needs of the devices before the supervision

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

        current_consumption = self._NomQuiPlairaPasAStephane[current_day][current_hour]

        for nature in self.natures:
            self._catalog.set(f"{self.name}.{nature.name}.proposed_energy", current_consumption)

    def react(self):  # method updating the device according to the decisions taken by the supervisor
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, nature, world, agent_name, filename, cluster_name=None):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyProduction(entity_name, nature, agent_name, filename, cluster_name)
            world.register_device(entity)

    mass_create = classmethod(mass_create)



