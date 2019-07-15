# ##############################################################################################
# Native packages
import numpy as np
import datetime as dt
import json
# Current packages
from common.Core import Device


# ##############################################################################################
class DummyNonControllableDevice(Device):

    def __init__(self, name,  agent_name, clusters, filename):
        super().__init__(name, agent_name, clusters)

        self._filename = filename  # the name of the data file

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._user_profile = []  # user profile of utilisation, describing user's priority
        # hour since the beginning of the period : [ priority, usage ID ]
        # the user profile lasts 1 day and starts at 00:00 AM

        self._usage_profile = []  # energy and interruptibility for one usage
        # [ energy consumption, priority ]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        # getting the real hour
        self._hour = self._catalog.get("physical_time").hour  # getting the hour of the day

        # parsing the data
        file = open(self._filename, "r")
        data = json.load(file)

        # creation of the consumption data
        self._period = data["period"]

        # we randomize a bit in order to represent reality better
        start_time_variation = (self._catalog.get("float")() - 0.5) * data["start time variation"]  # creation of a displacement in the user profile
        for start_time in data["user profile"]:
            start_time += start_time_variation

        duration_variation = (self._catalog.get("float")() - 0.5) * data["duration variation"]  # modification of the duration
        consumption_variation = (self._catalog.get("float")() - 0.5) * data["consumption variation"]  # modification of the consumption
        for line in data["usage profile"]:
            line[0] += duration_variation
            for nature in line[1]:
                line[1][nature] += consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        for hour in data["user profile"]:
            self._user_profile.append((hour // time_step) * time_step)  # changing the hour fo fit the time step

        # usage profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        duration = 0
        consumption = {nature: 0 for nature in data["usage profile"][0][1]}  # consumption is a dictionary containing the consumption for each nature

        for i in range(len(data["usage profile"])):
            buffer = duration % time_step  # the time already taken by the line i-1 of data in the current time_step
            duration += data["usage profile"][i][0]

            if duration < time_step:  # as long as the next time step is not reached, consumption and duration are summed
                for nature in consumption:
                    consumption[nature] += data["usage profile"][i][1][nature]

            else:  # we add a part of the energy consumption on the current step and we report the other part and we store the values into the self

                # fulling the usage profile
                while duration // time_step:  # here we manage a constant consumption over several time steps

                    time_left = time_step - buffer  # the time available on the current time-step for the current consumption line i in data
                    ratio = min(time_left / data["usage profile"][i][0], 1)  # the min() ensures that a duration which doesn't reach the next time step is not overestimated
                    self._usage_profile.append({})
                    for nature in consumption:
                        self._usage_profile[-1][nature] = (consumption[nature] + data["usage profile"][i][1][nature] * ratio)

                    duration -= time_step  # we decrease the duration of 1 time step
                    # buffer and consumption were the residue of line i-1, so they are not relevant anymore
                    buffer = 0
                    for nature in consumption:
                        consumption[nature] = 0

                for nature in consumption:
                    consumption[nature] = data["usage profile"][i][1][nature] * duration / data["usage profile"][i][0]  # energy reported

        # then, we affect the residue of energy if one, with the appropriate priority, to the usage profile
        if duration:  # to know if the device need more time
            self._usage_profile.append(consumption)

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature not in self._usage_profile[0].keys():
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures.pop(nature)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # method updating needs of the devices before the supervision

        consumption = {nature: 0 for nature in self._usage_profile[0]}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # if the device is not running
            # then it's the user profile which is taken into account

            for hour in self._user_profile:
                if hour == self._hour:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in consumption:
                        consumption[nature] = self._usage_profile[0][nature]
                    self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration

            for nature in self.natures:
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", consumption[nature.name])

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor
        self._hour = self._hour + 1 - (self._hour // self._period)*self._period  # incrementing the hour in the period

        if self._remaining_time != 0:  # decrementing the remaining time of use
            self._remaining_time -= 1

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, agent_name, filename, cluster):
        for i in range(n):
            device_name = f"{name}_{str(i)}"
            device = DummyNonControllableDevice(device_name, agent_name, filename, cluster)
            world.register_device(device)

    mass_create = classmethod(mass_create)


# ##############################################################################################
class DummyShiftableConsumption(Device):  # a consumption which is shiftable

    def __init__(self, name, agent_name, clusters, filename):
        super().__init__(name, agent_name, clusters)

        self._filename = filename  # the name of the data file

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._use_ID = None  # this ID references the ongoing use
        self._is_done = []  # list of usage already done during one period
        self._hour = None  # the hour of the day
        self._period = 0  # this period represents a typical usage of a dishwasher (e.g 2 days)

        self._user_profile = []  # user profile of utilisation, describing user's priority
        # hour since the beginning of the period : [ priority, usage ID ]
        # the user profile lasts 1 day and starts at 00:00 AM

        self._usage_profile = []  # energy and interruptibility for one usage
        # [ energy consumption, priority ]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        # getting the real hour
        self._hour = self._catalog.get("physical_time").hour  # getting the hour of the day

        # parsing the data
        file = open(self._filename, "r")
        data = json.load(file)

        # creation of the consumption data
        self._period = data["period"]

        # we randomize a bit in order to represent reality better
        start_time_variation = (self._catalog.get("float")() - 0.5) * data["start time variation"]  # creation of a displacement in the user profile
        for line in data["user profile"]:
            line[0] += start_time_variation

        duration_variation = (self._catalog.get("float")() - 0.5) * data["duration variation"]  # modification of the duration
        consumption_variation = (self._catalog.get("float")() - 0.5) * data["consumption variation"]  # modification of the consumption
        for line in data["usage profile"]:
            line[0] += duration_variation
            for nature in line[1]:
                line[1][nature] = line[1][nature] + consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        # user profile
        self._user_profile = [[i * time_step, 0, 0] for i in range(self._period // time_step)]  # creation of an empty user_profile with all cases ready

        # adding a null priority at the beginning and the end of the period
        # the beginning and the end are chosen outside of the period in order to avoid possible confusions
        data["user profile"].reverse()
        data["user profile"].append([-1, 0])
        data["user profile"].reverse()
        data["user profile"].append([self._period+1, 0])

        j = 0  # the place where you are in the data
        previous_point = data["user profile"][j]  # the last point of data encountered
        next_point = data["user profile"][j+1]  # the last point of data that will be encountered
        usage_number = 0

        for line in self._user_profile:

            line[2] = usage_number  # adding the id of the usage

            while True:

                next_point_reached = False
                if next_point[0] < line[0] + time_step:  # when "next_point" is reached, it becomes "previous_point"
                    next_point_reached = True
                    j += 1
                    previous_point = data["user profile"][j]
                    next_point = data["user profile"][j + 1]

                # if not (next_point[1] + previous_point[1]):  # if the priority is null
                #     line[1] = 0  # then it is put to 0 to avoid problems due to numerical unaccuracy

                # linear interpolation in order to calculate the priority
                a = next_point[1] - previous_point[1]

                if next_point[0] > line[0] + time_step:  # if the next point is not reached during this time step
                    b = next_point[0] - previous_point[0]
                    c = (line[0] + time_step) - previous_point[0]
                else:  # if the next point is met during the time step, there is no nee for linear interpolation
                    b = 1
                    c = 1
                line[1] = max(previous_point[1] + a/b*c, previous_point[1], line[1])  # to avoid problems with the diminution of priority...
                # ... as priority is always the highest one encountered during the time step

                if next_point[1] < previous_point[1]:  # if priority has decreased...
                    usage_number += 1  # ...then it means a new usage will begin

                if next_point[0] > line[0] + time_step or not next_point_reached:
                    break

        # cleaning of the useless entries in the user_profile
        elements_to_keep = []
        for i in range(len(self._user_profile)):
            if self._user_profile[i][1]:  # if the priority is not null
                elements_to_keep.append(self._user_profile[i])
        self._user_profile = elements_to_keep

        # usage profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        duration = 0
        consumption = {nature: 0 for nature in data["usage profile"][0][1]}  # consumption is a dictionary containing the consumption for each nature
        priority = 0

        for i in range(len(data["usage profile"])):

            buffer = duration % time_step  # the time already taken by the line i-1 of data in the current time_step
            duration += data["usage profile"][i][0]

            if duration < time_step:  # as long as the next time step is not reached, consumption and duration are summed

                for nature in data["usage profile"][i][1]:  # consumption is added for each nature present
                    consumption[nature] = consumption[nature] + data["usage profile"][i][1][nature]
                priority = data["usage profile"][i][2]

            else:  # we add a part of the energy consumption on the current step and we report the other part and we store the values into the self

                # fulling the usage profile
                while duration // time_step:  # here we manage a constant consumption over several time steps

                    self._usage_profile.append([{}, 0])  # creation of the entry, with a dictionary for the different natures
                    time_left = time_step - buffer  # the time available on the current time-step for the current consumption line i in data
                    ratio = min(time_left / data["usage profile"][i][0], 1)  # the min() ensures that a duration which doesn't reach the next time step is not overestimated
                    for nature in data["usage profile"][i][1]:  # consumption is added for each nature present
                        self._usage_profile[-1][0][nature] = 0   # creation of the entry
                        self._usage_profile[-1][0][nature] = consumption[nature] + data["usage profile"][i][1][nature] * ratio

                    self._usage_profile[-1][1] = max(priority, data["usage profile"][i][2])
                    priority = 0

                    duration -= time_step  # we decrease the duration of 1 time step
                    # buffer and consumption were the residue of line i-1, so they are not relevant anymore
                    buffer = 0

                    for nature in consumption:  # consumption is added for each nature present
                        consumption[nature] = 0

                for nature in consumption:  # consumption is added for each nature present
                    consumption[nature] = data["usage profile"][i][1][nature] * duration / data["usage profile"][i][0]  # energy reported

        # then, we affect the residue of energy if one, with the appropriate priority, to the usage profile
        if duration:  # to know if the device need more time
            self._usage_profile.append([0, 0])  # creation of the entry
            self._usage_profile[-1][0] = consumption
            self._usage_profile[-1][1] = priority

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature not in self._usage_profile[0][0]:
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures.pop(nature)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):

        if self._hour == 0:  # if a new period is starting
            self._is_done = []  # the list of achieved appliances is reinitialized

        consumption = {nature: 0 for nature in self._usage_profile[0][0]}  # consumption which will be asked eventually
        priority = 0  # priority of the consumption

        if not self._remaining_time:  # if the device is not running
            # then it's the user profile which is taken into account

            for line in self._user_profile:
                if line[0] == self._hour and line[2] not in self._is_done:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in consumption:
                        consumption[nature] = self._usage_profile[0][0][nature]  # the energy needed by the device during the first hour of utilization
                    priority = line[1]  # the current priority
                    self._is_done.append(line[2])  # adding the usage to the list of already satisfied usages

        else:  # if the device is running
            # then it's the usage profile who matters
            for nature in consumption:
                consumption[nature] = self._usage_profile[-self._remaining_time][0][nature]  # energy needed
            priority = self._usage_profile[-self._remaining_time][1]  # priority associated

        for nature in self.natures:
            # print(consumption)
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", consumption[nature.name])
            self._catalog.set(f"{self.name}.priority", priority)

    def _user_react(self):

        self._hour = self._hour + self._catalog.get("time_step") - (self._hour // self._period)*self._period  # incrementing the hour in the period

        if self._remaining_time != 0:  # decrementing the remaining time of use
            self._remaining_time -= 1
        else:
            i = 0
            while self._hour != self._user_profile[i][0] and i < len(self._user_profile) - 1:  # if it can correspond to the beginning of an usage
                for nature in self._natures:
                    if self._catalog.get(f"{self.name}.{nature.name}.energy_accorded"):  # if it has started
                        self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration
                        self._is_done.append(self._user_profile[i][2])  # the usage is considered as done
                    else:
                        dissatisfaction = self._catalog.get(f"{self.agent.name}.dissatisfaction") + 1
                        self._catalog.set(f"{self.agent.name}.dissatisfaction", dissatisfaction)  # dissatisfaction increments
                i += 1

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, agent_name, filename, cluster):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyShiftableConsumption(entity_name, agent_name, filename, cluster)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


# ##############################################################################################
class DummyAdjustableConsumption(Device):  # a consumption which is adjustable

    def __init__(self, name, agent_name, clusters, filename):
        super().__init__(name, agent_name, clusters)

        self._filename = filename  # the name of the data file

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._use_ID = None  # this ID references the ongoing use
        self._is_done = []  # list of usage already done during one period
        self._hour = None  # the hour of the day
        self._period = 0  # this period represents a typical usage of a dishwasher (e.g 2 days)

        self._latent_demand = 0  # the energy in excess or in default after being served

        self._user_profile = []  # user profile of utilisation, describing user's priority
        # hour since the beginning of the period : [ priority, usage ID ]
        # the user profile lasts 1 day and starts at 00:00 AM

        self._usage_profile = []  # energy and interruptibility for one usage
        # [ energy consumption, priority ]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        # getting the real hour
        self._hour = self._catalog.get("physical_time").hour  # getting the hour of the day

        # parsing the data
        file = open(self._filename, "r")
        data = json.load(file)

        # creation of the consumption data
        self._period = data["period"]

        # we randomize a bit in order to represent reality better
        start_time_variation = (self._catalog.get("float")() - 0.5) * data["start time variation"]  # creation of a displacement in the user profile
        for start_time in data["user profile"]:
            start_time += start_time_variation

        duration_variation = (self._catalog.get("float")() - 0.5) * data["duration variation"]  # modification of the duration
        consumption_variation = (self._catalog.get("float")() - 0.5) * data["consumption variation"]  # modification of the consumption
        for line in data["usage profile"]:
            line[0] += duration_variation
            for nature in line[1]:
                for element in line[1][nature]:
                    element += consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        for hour in data["user profile"]:
            self._user_profile.append((hour // time_step) * time_step)  # changing the hour fo fit the time step

        # usage profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        duration = 0
        consumption = {nature: [0, 0, 0] for nature in data["usage profile"][0][1]}  # consumption is a dictionary containing the consumption for each nature

        for i in range(len(data["usage profile"])):
            buffer = duration % time_step  # the time already taken by the line i-1 of data in the current time_step
            duration += data["usage profile"][i][0]

            if duration < time_step:  # as long as the next time step is not reached, consumption and duration are summed
                for nature in consumption:
                    consumption[nature][0] += data["usage profile"][i][1][nature][0]
                    consumption[nature][1] += data["usage profile"][i][1][nature][1]
                    consumption[nature][2] += data["usage profile"][i][1][nature][2]

            else:  # we add a part of the energy consumption on the current step and we report the other part and we store the values into the self

                # fulling the usage profile
                while duration // time_step:  # here we manage a constant consumption over several time steps

                    time_left = time_step - buffer  # the time available on the current time-step for the current consumption line i in data
                    ratio = min(time_left / data["usage profile"][i][0], 1)  # the min() ensures that a duration which doesn't reach the next time step is not overestimated
                    self._usage_profile.append({})
                    for nature in consumption:
                        self._usage_profile[-1][nature] = [0, 0, 0]
                        self._usage_profile[-1][nature][0] = (consumption[nature][0] + data["usage profile"][i][1][nature][0] * ratio)
                        self._usage_profile[-1][nature][1] = (consumption[nature][1] + data["usage profile"][i][1][nature][1] * ratio)
                        self._usage_profile[-1][nature][2] = (consumption[nature][2] + data["usage profile"][i][1][nature][2] * ratio)

                    duration -= time_step  # we decrease the duration of 1 time step
                    # buffer and consumption were the residue of line i-1, so they are not relevant anymore
                    buffer = 0
                    for nature in consumption:
                        for element in consumption[nature]:
                            element = 0

                for nature in consumption:
                    consumption[nature][0] = data["usage profile"][i][1][nature][0] * duration / data["usage profile"][i][0]  # energy reported
                    consumption[nature][1] = data["usage profile"][i][1][nature][1] * duration / data["usage profile"][i][0]  # energy reported
                    consumption[nature][2] = data["usage profile"][i][1][nature][2] * duration / data["usage profile"][i][0]  # energy reported

        # then, we affect the residue of energy if one, with the appropriate priority, to the usage profile
        if duration:  # to know if the device need more time
            self._usage_profile.append(consumption)

        # Creation of specific entries
        for nature in self._natures:
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted_minimum")
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted_maximum")

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature not in self._usage_profile[0].keys():
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures.pop(nature)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # method updating needs of the devices before the supervision
        #
        # if self._remaining_time == 0:  # if the device is not running
        #
        #     for data in self._NomQuiPlairaPasAStephane:
        #         # initialization of the use
        #         if data[0] == current_hour:  # if the current hour corresponds to the beginning of a use
        #             self._current_line = self._NomQuiPlairaPasAStephane.index(data)  # saving the line of data
        #             self._remaining_time = len(data[1])  # setting the remaining time of use
        #         pass    # this means the "for" ends, no matter if other uses would have been relevant,
        #                 # as this is a problem in the construction of the data file
        #
        # if self._remaining_time != 0:  # if the device is running
        #     priority = list()  # a calculus of priority is made for each nature and then the max is kept
        #     for nature in self._natures:
        #         data = self._NomQuiPlairaPasAStephane[self._current_line]
        #         self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", data[1][-self._remaining_time])  # what the device asks
        #
        #         # calculus of the priority
        #         # what is still needed / what is possible to deliver
        #         if self._remaining_time == 1:  # if it is the last round
        #             priority.append(1)  # priority is set to one, as it won't be possible to deliver last time
        #         else:
        #             priority.append((sum(data[1][-self._remaining_time:]) + self._latent_demand)\
        #             / (self._catalog.get(f"{self.name}.{nature.name}.energy_wanted") * (self._remaining_time - 1)))
        #
        #     self._catalog.set(f"{self.name}.priority", min(max(priority), 1))
        #
        #     self._remaining_time -= 1
        #     if self._remaining_time == 0:  # if the device is shut down after
        #         self._catalog.set(f"{self.name}.priority", 0)  # its priority is reinitialized
        #         for nature in self._natures:
        #             self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", 0)  # its energy demand is reinitialized
        #         self._current_line = None  # the current line is reinitialized
        #         self._latent_demand = 0  # latent demand is reinitialized

        consumption = {nature: [0, 0, 0] for nature in self._usage_profile[0]}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # if the device is not running
            # then it's the user profile which is taken into account

            for hour in self._user_profile:
                if hour == self._hour:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in consumption:
                        consumption[nature] = self._usage_profile[0][nature][0]
                        consumption[nature] = self._usage_profile[0][nature][1]
                        consumption[nature] = self._usage_profile[0][nature][2]
                    self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration

            for nature in self.natures:
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted_minimum", consumption[nature.name][0])
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", consumption[nature.name][1])
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted_maximum", consumption[nature.name][2])

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor

        if self._remaining_time != 0:  # decrementing the remaining time of use
            self._remaining_time -= 1
            for nature in self._natures:
                energy_wanted = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")
                energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")
                if energy_wanted != energy_accorded:  # if it is not the nominal wanted energy...
                    dissatisfaction = self._catalog.get(f"{self.agent.name}.dissatisfaction")
                    dissatisfaction += abs(energy_wanted - energy_accorded) / energy_wanted  # ... dissatisfaction increases
                    self._catalog.set(f"{self.agent.name}.dissatisfaction", dissatisfaction)

                    self._latent_demand += energy_wanted - energy_accorded  # the energy in excess or in default

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, agent_name, filename, cluster):
        for i in range(n):
            entity_name = f"{name}_{str(i)}"
            entity = DummyShiftableConsumption(entity_name, agent_name, filename, cluster)
            world.register_device(entity)

    mass_create = classmethod(mass_create)


