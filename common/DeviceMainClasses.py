# ##############################################################################################
# Native packages
from json import load
from datetime import datetime
# Current packages
from common.Core import Device, DeviceException
from common.Contract import Contract


# ##############################################################################################
class NonControllableDevice(Device):

    def __init__(self, name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters):
        super().__init__(name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        pass

    def _get_consumption(self):

        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        beginning = self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        start_time_variation = self._catalog.get("gaussian")(data_user["start_time_variation"])  # creation of a displacement in the user_profile
        duration_variation = self._catalog.get("gaussian")(data_user["duration_variation"])  # modification of the duration
        for line in data_user["profile"]:  # modification of the basic user_profile according to the results of random generation
            line[0] += start_time_variation
            line[1] *= duration_variation

        consumption_variation = self._catalog.get("gaussian")(data_device["consumption_variation"])  # modification of the consumption
        for nature in data_device["usage_profile"]:
            data_device["usage_profile"][nature] *= consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        # user profile
        for line in data_user["profile"]:
            current_moment = int(line[0] // time_step)  # the moment when the device will be turned on

            # creation of the user profile, where there are hours associated with the use of the device
            # first time step

            ratio = (beginning % time_step - line[0] % time_step) / time_step  # the percentage of use at the beginning (e.g for a device starting at 7h45 with an hourly time step, it will be 0.25)
            if ratio <= 0:  # in case beginning - start is negative
                ratio += 1
            self._user_profile.append([current_moment, ratio])  # adding the first time step when it will be turned on

            # intermediate time steps
            duration_residue = line[1] - (ratio * time_step)  # the residue of the duration is the remnant time during which the device is operating
            while duration_residue >= 1:  # as long as there is at least 1 full time step of functioning...
                current_moment += 1
                duration_residue -= 1
                self._user_profile.append([current_moment, 1])  # ...a new entry is created with a ratio of 1 (full use)

            # final time step
            current_moment += 1
            ratio = duration_residue/time_step  # the percentage of use at the end (e.g for a device ending at 7h45 with an hourly time step, it will be 0.75)
            self._user_profile.append([current_moment, ratio])  # adding the final time step before it wil be turned off

        # usage profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        self._usage_profile = dict()
        for nature in data_device["usage_profile"]:  # data_usage is then added for each nature used by the device
            self._usage_profile[nature] = data_device["usage_profile"][nature]

        self._unused_nature_removal()  # remove unused natures

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision

        consumption = {nature: 0 for nature in self._usage_profile}  # consumption that will be asked eventually

        for line in self._user_profile:
            if line[0] == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet
                for nature in consumption:
                    consumption[nature] = self._usage_profile[nature] * line[1]  # energy needed for all natures used by the device

        for nature in self.natures:  # publication of the consumption in the catalog
            energy_wanted = [[consumption[nature.name] for i in range(3)], None]  # Emin, Enom, Emax (which are the same as it is urgent) and the price
            energy_wanted = self.natures[nature][1].quantity_modification(energy_wanted, self.agent.name)
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted)

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor
        self._moment = (self._moment + 1) % self._period  # incrementing the hour in the period

        # effort management
        energy_wanted = dict()
        energy_accorded = dict()
        for nature in self.natures:
            energy_wanted[nature] = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")
            energy_accorded[nature] = sum([self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"] for nature in self.natures])
            if energy_wanted != energy_accorded:  # if it is not the nominal wanted energy...
                effort = 42  # j'ai mis 42 en attendant qu'on se mette d'accord
                effort = self.natures[nature][1].effort_modification(effort, self.agent.name)  # here, the contract may modify effort
                self.agent.add_effort(effort, nature)  # effort increments

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def type(self):
        return "non_controllable"


# ##############################################################################################
class ShiftableDevice(Device):  # a consumption which is shiftable

    def __init__(self, name, contracts,  agent_name, clusters, filename, user_type, consumption_device, parameters):
        super().__init__(name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters)

        self._use_ID = None  # this ID references the ongoing use
        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._is_done = []  # list of usage already done during one period
        # a list containing the data necessary to manage priority if the device is interrupted
        self._interruption_data = [False,  # if the device has been interrupted
                                   0,  # last time step to launch the device initially
                                   0]  # duration during which the device has functioned

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        pass

    def _get_consumption(self):
        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        start_time_variation = self._catalog.get("gaussian")(data_user["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data_user["profile"]:
            line[0] += start_time_variation

        duration_variation = self._catalog.get("gaussian")(data_device["duration_variation"])  # modification of the duration
        consumption_variation = self._catalog.get("gaussian")(data_device["consumption_variation"])  # modification of the consumption
        for line in data_device["usage_profile"]:
            line[0] *= duration_variation
            for nature in line[1]:
                line[1][nature] *= consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        # user_profile
        self._user_profile = [[i * time_step, 0, 0] for i in range(self._period)]  # creation of an empty user_profile with all cases ready

        # adding a null priority at the beginning and the end of the period
        # the beginning and the end are chosen outside of the period in order to avoid possible confusions
        data_user["profile"].reverse()
        data_user["profile"].append([-1, 0])
        data_user["profile"].reverse()
        data_user["profile"].append([self._period*time_step+1, 0])

        j = 0  # the place where you are in the data
        previous_point = data_user["profile"][j]  # the last point of data encountered
        next_point = data_user["profile"][j+1]  # the last point of data that will be encountered
        usage_number = 0

        for line in self._user_profile:  # filling the user profile with priority

            line[2] = usage_number  # adding the id of the usage

            while True:  # the loop is shut down when all the data on the line has been recorded

                next_point_reached = False  # a flag indicating when the next time step is beyond the scope of the "line"
                if next_point[0] < line[0] + time_step:  # when "next_point" is reached, it becomes "previous_point"
                    next_point_reached = True
                    j += 1
                    previous_point = data_user["profile"][j]
                    next_point = data_user["profile"][j + 1]

                # linear interpolation in order to calculate the priority
                a = next_point[1] - previous_point[1]

                if next_point[0] > line[0] + time_step:  # if the next point is not reached during this time step
                    b = next_point[0] - previous_point[0]
                    c = (line[0] + time_step) - previous_point[0]
                else:  # if the next point is met during the time step, there is no need for linear interpolation
                    b = 1
                    c = 1
                line[1] = max(previous_point[1] + a/b*c, previous_point[1], line[1])  # to avoid problems with the diminution of priority...
                # ... as priority is always the highest one encountered during the time step

                if not next_point[1]:  # if priority becomes null...
                    usage_number += 1  # ...then it means a new usage will begin

                if next_point[0] > line[0] + time_step or not next_point_reached:
                    break

        # cleaning of the useless entries in the user_profile
        elements_to_keep = []
        for i in range(len(self._user_profile)):
            if self._user_profile[i][1]:  # if the priority is not null
                elements_to_keep.append(self._user_profile[i])
        self._user_profile = elements_to_keep

        # usage_profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        duration = 0
        consumption = {nature: 0 for nature in data_device["usage_profile"][0][1]}  # consumption is a dictionary containing the consumption for each nature
        priority = 0

        for i in range(len(data_device["usage_profile"])):

            buffer = duration % time_step  # the time already taken by the line i-1 of data in the current time_step
            duration += data_device["usage_profile"][i][0]  # duration represents the time not affected yet in a line of data of usage profile

            if duration < time_step:  # as long as the next time step is not reached, consumption and duration are summed

                for nature in data_device["usage_profile"][i][1]:  # consumption is added for each nature present
                    consumption[nature] = consumption[nature] + data_device["usage_profile"][i][1][nature]
                priority = data_device["usage_profile"][i][2]

            else:  # we add a part of the energy consumption on the current step and we report the other part and we store the values into the self

                # fulling the usage_profile
                while duration // time_step:  # here we manage a constant consumption over several time steps

                    self._usage_profile.append([{}, 0])  # creation of the entry, with a dictionary for the different natures
                    time_left = time_step - buffer  # the time available on the current time-step for the current consumption line i in data
                    ratio = min(time_left / data_device["usage_profile"][i][0], 1)  # the min() ensures that a duration which doesn't reach the next time step is not overestimated
                    for nature in data_device["usage_profile"][i][1]:  # consumption is added for each nature present
                        self._usage_profile[-1][0][nature] = 0  # creation of the entry
                        self._usage_profile[-1][0][nature] = consumption[nature] + data_device["usage_profile"][i][1][nature] * ratio

                    self._usage_profile[-1][1] = max(priority, data_device["usage_profile"][i][2])  # the priority is the max betwwen the former priority and the new
                    priority = 0

                    duration -= time_step  # we decrease the duration of 1 time step
                    # buffer and consumption were the residue of line i-1, so they are not relevant anymore
                    buffer = 0

                    for nature in consumption:  # consumption is added for each nature present
                        consumption[nature] = 0

                for nature in consumption:  # consumption is added for each nature present
                    consumption[nature] = data_device["usage_profile"][i][1][nature] * duration / data_device["usage_profile"][i][0]  # energy reported

        # then, we affect the residue of energy if one, with the appropriate priority, to the usage_profile
        if duration:  # to know if the device needs more time
            self._usage_profile.append([0, 0])  # creation of the entry
            priority = data_device["usage_profile"][-1][2]
            self._usage_profile[-1][0] = consumption
            self._usage_profile[-1][1] = priority

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature.name not in self._usage_profile[0][0]:
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures[nature][0].devices.remove(self.name)
            self._natures.pop(nature)
            self._catalog.remove(f"{self.name}.{nature.name}.energy_accorded")
            self._catalog.remove(f"{self.name}.{nature.name}.energy_wanted")

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):

        if not self._moment:  # if a new period is starting
            self._is_done = []  # the list of achieved appliances is reinitialized

        consumption = {nature: [0, 0, 0] for nature in self._usage_profile[0][0]}  # consumption which will be asked eventually
        # priority = 0  # priority of the consumption

        if not self._remaining_time:  # if the device is not running then it's the user_profile which is taken into account

            for i in range(len(self._user_profile)):
                line = self._user_profile[i]
                if line[0] == self._moment and line[2] not in self._is_done:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in consumption:
                        consumption[nature][2] = self._usage_profile[0][0][nature]  # the energy needed by the device during the first hour of utilization
                        consumption[nature][1] = line[1] * self._usage_profile[0][0][nature]  # it modelizes the emergency

                    self._is_done.append(line[2])  # adding the usage to the list of already satisfied usages
                    # reinitialisation of the interruption data
                    self._interruption_data[0] = False
                    j = 0
                    while line[2] == self._user_profile[j][2] and j < (len(self._user_profile) - 1):  # as long as the usage ID is still the same, the last time_step is not reached (and of course as long as the end of the list is not reached)
                        self._interruption_data[1] = self._user_profile[j][0]
                        j += 1
                    self._interruption_data[2] = 0

                    break  # once the matching hour has been found, it is useless to pursue the loop

        else:  # if the device is running then it's the usage_profile who matters
            for nature in consumption:
                consumption[nature][2] = self._usage_profile[-self._remaining_time][0][nature]  # energy needed
                ratio = self._usage_profile[-self._remaining_time][1]  # emergency associated
                consumption[nature][1] = ratio * consumption[nature][2]

            if self._interruption_data[0]:  # if the device has been interrupted
                nature = list(self.natures)[0]  # take the first nature registered in the device to measure the emergency
                energy_wanted_before = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")
                min = energy_wanted_before[0][0]
                nom = energy_wanted_before[0][1]
                max = energy_wanted_before[0][2]
                emergency = (nom - min) / (max - min)

                ratio = (1 - emergency) / (self._interruption_data[1] + self._interruption_data[2] - (self._moment - 1)) + emergency  # calculation of priority in case of interruption
                nom = ratio * (max - min) + min
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", nom)

        for nature in self.natures:  # publication of the consumption in the catalog
            energy_wanted = [[consumption[nature.name][i] for i in range(3)], None]  # Emin, Enom, Emax (which are the same as it is urgent) and the price
            energy_wanted = self.natures[nature][1].quantity_modification(energy_wanted, self.agent.name)  # the contract may modify the energy wanted
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted)  # publication of the energy wanted in the catalog

    def _user_react(self):
        self._moment = (self._moment + 1) % self._period  # incrementing the moment in the period

        energy_wanted = sum([self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")[0][1] for nature in self.natures])  # total energy wanted by the device
        energy_accorded = sum([self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"] for nature in self.natures])  # total energy accorded to the device

        if self._remaining_time and energy_accorded < energy_wanted:  # if the device has started and not been served, then it has been interrupted
            self._interruption_data[0] = True  # it is flagged as "interrupted"

        # effort and interruption management
        if energy_wanted:  # if the device is active

            if energy_accorded:  # if it has been served
                if self._remaining_time:  # if it has started
                    self._remaining_time -= 1  # decrementing the remaining time of use
                else:  # if it has not started yet
                    self._remaining_time = len(self._usage_profile)

                self._interruption_data[2] += 1  # it has been working for one more time step

            energy_min = sum([self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")[0][0] for nature in self.natures])  # sum of the minimal energy, cumulated for all natures of energy, that the device should have given/received

            if energy_min > energy_accorded:  # if the device is inactive meanwhile its priority is 1
                for nature in self.natures:
                    effort = 1
                    effort = self.natures[nature][1].effort_modification(effort, self.agent.name)  # here, the contract may modify effort
                    self.agent.add_effort(effort, nature)  # effort increments

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def type(self):
        return "shiftable"


# ##############################################################################################
class AdjustableDevice(Device):  # a consumption which is adjustable

    def __init__(self, name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters):
        super().__init__(name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters)

        self._use_ID = None  # this ID references the ongoing use
        self._is_done = []  # list of usage already done during one period
        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run

        self._latent_demand = dict()  # the energy in excess or in default after being served

        self._max_power = dict()  # the max power accepted by the device, defined by the profile

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device

        # Creation of specific entries
        for nature in self._natures:
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted_minimum")
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted_maximum")

    def _get_consumption(self):
        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        start_time_variation = self._catalog.get("gaussian")(data_user["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data_user["profile"]:  # modification of the basic user_profile according to the results of random generation
            print(self.name)
            line[0] += start_time_variation

        duration_variation = self._catalog.get("gaussian")(data_user["duration_variation"])  # modification of the duration
        consumption_variation = self._catalog.get("gaussian")(data_device["consumption_variation"])  # modification of the consumption
        for line in data_device["usage_profile"]:
            line[0] *= duration_variation
            for nature in line[1]:
                for element in line[1][nature]:
                    element *= consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        for hour in data_user["profile"]:
            self._user_profile.append((hour // time_step) * time_step)  # changing the hour fo fit the time step

        # max power
        self._max_power = {element: time_step * data_device["max_power"][element] for element in data_device["max_power"]}  # the maximum power is registered for each nature

        # usage_profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        duration = 0
        consumption = {nature: [0, 0, 0] for nature in data_device["usage_profile"][0][1]}  # consumption is a dictionary containing the consumption for each nature

        for i in range(len(data_device["usage_profile"])):
            buffer = duration % time_step  # the time already taken by the line i-1 of data in the current time_step
            duration += data_device["usage_profile"][i][0]

            if duration < time_step:  # as long as the next time step is not reached, consumption and duration are summed
                for nature in consumption:
                    consumption[nature][0] += data_device["usage_profile"][i][1][nature][0]
                    consumption[nature][1] += data_device["usage_profile"][i][1][nature][1]
                    consumption[nature][2] += data_device["usage_profile"][i][1][nature][2]

            else:  # we add a part of the energy consumption on the current step and we report the other part and we store the values

                # fulling the usage_profile
                while duration // time_step:  # here we manage a constant consumption over several time steps

                    time_left = time_step - buffer  # the time available on the current time-step for the current consumption line i in data
                    ratio = min(time_left / data_device["usage_profile"][i][0], 1)  # the min() ensures that a duration which doesn't reach the next time step is not overestimated
                    self._usage_profile.append({})
                    for nature in consumption:
                        self._usage_profile[-1][nature] = [0, 0, 0]
                        self._usage_profile[-1][nature][0] = (consumption[nature][0] + data_device["usage_profile"][i][1][nature][0] * ratio)
                        self._usage_profile[-1][nature][1] = (consumption[nature][1] + data_device["usage_profile"][i][1][nature][1] * ratio)
                        self._usage_profile[-1][nature][2] = (consumption[nature][2] + data_device["usage_profile"][i][1][nature][2] * ratio)

                    duration -= time_step  # we decrease the duration of 1 time step
                    # buffer and consumption were the residue of line i-1, so they are not relevant anymore
                    buffer = 0
                    for nature in consumption:
                        for element in consumption[nature]:
                            element = 0

                for nature in consumption:
                    consumption[nature][0] = data_device["usage_profile"][i][1][nature][0] * duration / data_device["usage_profile"][i][0]  # energy reported
                    consumption[nature][1] = data_device["usage_profile"][i][1][nature][1] * duration / data_device["usage_profile"][i][0]  # energy reported
                    consumption[nature][2] = data_device["usage_profile"][i][1][nature][2] * duration / data_device["usage_profile"][i][0]  # energy reported

        # then, we affect the residue of energy if one, with the appropriate priority, to the usage_profile
        if duration:  # to know if the device need more time
            self._usage_profile.append(consumption)

        self._unused_nature_removal()  # remove unused natures

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        consumption = {nature: [0, 0, 0] for nature in self._usage_profile[0]}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # if the device is not running then it's the user_profile which is taken into account

            for hour in self._user_profile:
                if hour == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in consumption:
                        consumption[nature][0] = self._usage_profile[0][nature][0] + self._latent_demand[nature]
                        consumption[nature][1] = self._usage_profile[0][nature][1] + self._latent_demand[nature]
                        consumption[nature][2] = self._usage_profile[0][nature][2] + self._latent_demand[nature]
                    self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration

            for nature in self.natures:  # publication of the consumption in the catalog
                energy_wanted = [[consumption[nature.name][i] for i in range(3)], None]  # Emin, Enom, Emax (which are the same as it is urgent) and the price
                energy_wanted = self.natures[nature][1].quantity_modification(energy_wanted)  # the contract may modify the energy wanted
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted)  # publication of the energy wanted in the catalog

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor
        self._moment = (self._moment + 1) % self._period  # incrementing the moment in the period

        # effort management
        energy_wanted = dict()
        energy_accorded = dict()
        for nature in self._natures:
            energy_wanted[nature] = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")
            energy_accorded[nature] = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]

            if energy_wanted[nature] != energy_accorded[nature]:  # if it is not the nominal wanted energy, then it creates effort
                energy_wanted_min = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_minimum")  # minimum quantity of energy
                energy_wanted_max = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_maximum")  # maximum quantity of energy

                effort = min(abs(energy_wanted_min - energy_accorded), abs(energy_wanted_max - energy_accorded)) / energy_wanted  # effort increases
                effort = self.natures[nature][1].effort_modification(effort, self.agent.name)  # here, the contract may modify effort
                effort = self._catalog.get(f"{self.agent.name}.{nature}.effort") + effort
                self.agent.add_effort(effort, nature)  # effort increments

                self._latent_demand[nature] += energy_wanted[nature] - energy_accorded[nature]  # the energy in excess or in default

        activity = sum([self._catalog.get(f"{self.name}.{nature.name}.energy_wanted") for nature in self.natures])  # activity is used as a boolean
        if activity:  # if the device is active
            if self._remaining_time:  # decrementing the remaining time of use
                self._remaining_time -= 1

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def type(self):
        return "adjustable"


# ##############################################################################################
class ChargerDevice(Device):  # a consumption which is adjustable

    def __init__(self, name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters):
        super().__init__(name, contracts, agent_name, clusters, filename, user_type, consumption_device, parameters)

        self._use_ID = None  # this ID references the ongoing use
        self._is_done = []  # list of usage already done during one period
        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run

        self._demand = dict()  # the quantity of energy necessary to fulfill the need for each nature of energy

        self._min_power = dict()  # the max power accepted by the device, defined by the profile for each nature of energy
        self._max_power = dict()  # the max power accepted by the device, defined by the profile for each nature of energy

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        pass

    def _get_consumption(self):

        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        start_time_variation = self._catalog.get("gaussian")(data_user["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data_user["profile"]:
            line[0] += start_time_variation
            line[1] += start_time_variation

        consumption_variation = self._catalog.get("gaussian")(data_device["consumption_variation"])  # modification of the consumption
        for nature in data_device["usage_profile"].values():
            nature *= consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        for i in range(len(data_user["profile"])):
            self._user_profile.append([])
            for hour in data_user["profile"][i]:
                self._user_profile[-1].append((hour // time_step) * time_step)  # changing the hour fo fit the time step

        # min and max power allowed
        # these power are converted into energy quantities according to the time step
        self._min_power = {element: time_step * data_device["min_power"][element] for element in data_device["min_power"]}  # the minimum power is registered for each nature
        self._max_power = {element: time_step * data_device["max_power"][element] for element in data_device["max_power"]}  # the maximum power is registered for each nature

        # usage_profile
        self._usage_profile = data_device["usage_profile"]  # creation of an empty usage_profile with all cases ready
        self._demand = self._usage_profile  # if the simulation begins during an usage, the demand has to be initialized

        self._unused_nature_removal()  # remove unused natures

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision

        consumption = {nature: [0, 0, 0] for nature in self._usage_profile}  # consumption which will be asked eventually
        # priority = 0

        if self._remaining_time == 0:  # checking if the device has to start
            for usage in self._user_profile:
                if usage[0] == self._moment:  # if the current hour matches with the start of an usage
                    self._remaining_time = usage[1] - usage[0]  # incrementing usage duration
                    self._demand = self._usage_profile  # the demand for each nature of energy

        if self._remaining_time:  # if the device is active
                    # priority_list = []  # a list containing the priority calculated for each nature of energy
                    for nature in consumption:
                        consumption[nature][0] = self._min_power[nature]
                        consumption[nature][1] = max(self._min_power[nature], min(self._max_power[nature], self._demand[nature] / self._remaining_time))  # the nominal energy demand is the total demand divided by the number of turns left
                        # but it needs to be between the min and the max value
                        consumption[nature][2] = self._max_power[nature]

        for nature in self.natures:  # publication of the consumption in the catalog
            energy_wanted = [[consumption[nature.name][i] for i in range(3)], None]  # Emin, Enom, Emax (which are the same as it is urgent) and the price
            energy_wanted = self.natures[nature][1].quantity_modification(energy_wanted, self.agent.name)  # the contract may modify the energy wanted
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted)  # publication of the energy wanted in the catalog

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor

        self._moment = (self._moment + 1) % self._period  # incrementing the moment in the period

        # effort management
        energy_wanted = dict()
        energy_accorded = dict()
        for nature in self._natures:
            energy_wanted[nature] = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")[0][1]  # the nominal quantity of energy wanted
            energy_accorded[nature] = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]

            if energy_wanted != energy_accorded:  # if it is not the nominal wanted energy, then it creates effort
                for nature in self.natures:
                    energy_wanted_min = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")[0][0]  # minimum quantity of energy
                    energy_wanted_max = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")[0][2] # maximum quantity of energy

                    if energy_wanted == energy_wanted_max:  # only an urgent need can generate effort
                        effort = min(abs(energy_wanted_min - energy_accorded[nature]), abs(energy_wanted_max - energy_accorded[nature])) / energy_wanted[nature]  # effort increases
                        effort = self.natures[nature][1].effort_modification(effort)  # here, the contract may modify effort
                        effort = self._catalog.get(f"{self.agent.name}.{nature.name}.effort") + effort
                        self.agent.add_effort(effort, nature)  # effort increments

            for nature in self._natures:
                self._demand[nature.name] -= energy_accorded[nature]  # the energy which still has to be served
                # /!\ if there is a minimum power, remember to change the line above to take into account the start-up costs
                # otherwise, there is a risk that the total quantity of energy required is inferior to the minimum power necessary for the device to work

        activity = sum([self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")[0][1] for nature in self.natures])  # activity is used as a boolean: it is the sum of the nominal quantities of energy asked
        if activity:  # if the device is active
            if self._remaining_time:  # decrementing the remaining time of use
                self._remaining_time -= 1

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def type(self):
        return "charger"










