# ##############################################################################################
# Native packages
# Current packages
from src.common.Device import Device, DeviceException
from json import load


# ##############################################################################################
class NonControllableDevice(Device):

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self):
        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        beginning = self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        self._randomize_start_variation(data_user)
        self._randomize_consumption(data_device)
        self._randomize_duration(data_user)

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

    def _randomize_start_variation(self, data):
        start_time_variation = self._catalog.get("gaussian")(0, data["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data["profile"]:  # modification of the basic user_profile according to the results of random generation
            line[0] += start_time_variation

    def _randomize_duration(self, data):
        duration_variation = self._catalog.get("gaussian")(1, data["duration_variation"])  # modification of the duration
        duration_variation = max(0, duration_variation)  # to avoid negative durations
        for line in data["profile"]:  # modification of the basic user_profile according to the results of random generation
            line[1] *= duration_variation

    def _randomize_consumption(self, data):
        consumption_variation = self._catalog.get("gaussian")(1, data["consumption_variation"])  # modification of the consumption
        consumption_variation = max(0, consumption_variation)  # to avoid to shift from consumption to production and vice-versa
        for nature in data["usage_profile"]:
            data["usage_profile"][nature] *= consumption_variation

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self._usage_profile}  # consumption that will be asked eventually

        for line in self._user_profile:
            if line[0] == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet
                for nature in energy_wanted:
                    energy_wanted[nature]["energy_minimum"] = self._usage_profile[nature] * line[1]  # energy needed for all natures used by the device
                    energy_wanted[nature]["energy_nominal"] = self._usage_profile[nature] * line[1]  # energy needed for all natures used by the device
                    energy_wanted[nature]["energy_maximum"] = self._usage_profile[nature] * line[1]  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def type(self):
        return "non_controllable"


# ##############################################################################################
class ShiftableDevice(Device):  # a consumption which is shiftable

    def __init__(self, name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name, parameters)
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

    def _read_data_profiles(self):
        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        self._randomize_start_variation(data_user)
        self._randomize_consumption(data_device)
        self._randomize_duration(data_device)

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
        next_point = data_user["profile"][j+1]  # the next point of data that will be encountered
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
            self._natures[nature]["aggregator"].devices.remove(self.name)
            self._natures.pop(nature)
            self._catalog.remove(f"{self.name}.{nature.name}.energy_accorded")
            self._catalog.remove(f"{self.name}.{nature.name}.energy_wanted")

    def _randomize_start_variation(self, data):
        start_time_variation = self._catalog.get("gaussian")(0, data["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data["profile"]:
            line[0] += start_time_variation

    def _randomize_duration(self, data):
        duration_variation = self._catalog.get("gaussian")(1, data["duration_variation"])  # modification of the duration
        duration_variation = max(0, duration_variation)  # to avoid negative durations
        for line in data["usage_profile"]:  # modification of the basic user_profile according to the results of random generation
            line[0] *= duration_variation

    def _randomize_consumption(self, data):
        consumption_variation = self._catalog.get("gaussian")(1, data["consumption_variation"])  # modification of the consumption
        consumption_variation = max(0, consumption_variation)  # to avoid to shift from consumption to production and vice-versa
        for line in data["usage_profile"]:  # modification of the basic user_profile according to the results of random generation
            for nature in line[1]:
                line[1][nature] *= consumption_variation

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):

        if not self._moment:  # if a new period is starting
            self._is_done = []  # the list of achieved appliances is reinitialized

        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                       for nature in self._usage_profile[0][0]}  # consumption which will be asked eventually

        if not self._remaining_time:  # if the device is not running then it's the user_profile who is taken into account

            for i in range(len(self._user_profile)):
                line = self._user_profile[i]
                # print(line, self._moment, self._is_done, self._remaining_time)
                if line[0] == self._moment and line[2] not in self._is_done:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in energy_wanted:
                        energy_wanted[nature]["energy_maximum"] = self._usage_profile[0][0][nature]  # the energy needed by the device during the first hour of utilization
                        energy_wanted[nature]["energy_nominal"] = line[1] * self._usage_profile[0][0][nature]  # it modelizes the emergency

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
            for nature in energy_wanted:
                ratio = self._usage_profile[-self._remaining_time][1]  # emergency associated
                energy_wanted[nature]["energy_minimum"] = 0
                energy_wanted[nature]["energy_maximum"] = self._usage_profile[-self._remaining_time][0][nature]  # energy needed
                energy_wanted[nature]["energy_nominal"] = ratio * energy_wanted[nature]["energy_maximum"]

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):
        super().react()  # actions needed for all the devices

        energy_wanted = sum([self.get_energy_wanted_nom(nature) for nature in self.natures])  # total energy wanted by the device
        energy_accorded = sum([self.get_energy_accorded_quantity(nature) for nature in self.natures])  # total energy accorded to the device

        if self._remaining_time and energy_accorded < energy_wanted:  # if the device has started and not been served, then it has been interrupted
            self._interruption_data[0] = True  # it is flagged as "interrupted"

        elif energy_wanted:  # if the device is active

            if energy_accorded:  # if it has been served
                if self._remaining_time:  # if it has started
                    self._remaining_time -= 1  # decrementing the remaining time of use
                else:  # if it has not started yet
                    self._remaining_time = len(self._usage_profile) - 1

                self._interruption_data[2] += 1  # it has been working for one more time step
            else:  # if it has not started
                self._is_done.pop()

            energy_min = sum([self.get_energy_wanted_min(nature) for nature in self.natures])  # total minimum energy wanted by the device

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def type(self):
        return "shiftable"


# ##############################################################################################
class AdjustableDevice(Device):  # a consumption which is adjustable

    def __init__(self, name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name, parameters)

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run

        self._latent_demand = dict()  # the energy in excess or in default after being served

        for nature in self._natures:
            self._latent_demand[nature] = 0

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self):
        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        start_time_variation = self._catalog.get("gaussian")(0, data_user["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data_user["profile"]:  # modification of the basic user_profile according to the results of random generation
            line[0] += start_time_variation

        duration_variation = self._catalog.get("gaussian")(1, data_user["duration_variation"])  # modification of the duration
        consumption_variation = self._catalog.get("gaussian")(1, data_device["consumption_variation"])  # modification of the consumption
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
        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                       for nature in self._usage_profile[0]}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # if the device is not running then it's the user_profile which is taken into account

            for hour in self._user_profile:
                if hour == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in energy_wanted:
                        energy_wanted[nature]["energy_minimum"] = self._usage_profile[0][nature][0] + self._latent_demand[nature]
                        energy_wanted[nature]["energy_nominal"] = self._usage_profile[0][nature][1] + self._latent_demand[nature]
                        energy_wanted[nature]["energy_maximum"] = self._usage_profile[0][nature][2] + self._latent_demand[nature]
                    self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration

            self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):  # method updating the device according to the decisions taken by the strategy
        super().react()  # actions needed for all the devices

        # effort management
        energy_wanted = dict()
        energy_accorded = dict()
        for nature in self._natures:
            energy_wanted[nature] = self.get_energy_wanted_nom(nature)
            energy_accorded[nature] = self.get_energy_accorded_quantity(nature)

            self._latent_demand[nature] += energy_wanted[nature] - energy_accorded[nature]  # the energy in excess or in default

        activity = sum([self.get_energy_wanted_nom(nature) for nature in self.natures])  # activity is used as a boolean
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

    def __init__(self, name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name, parameters)

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self):

        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        self._randomize_start_variation(data_user)
        self._randomize_consumption(data_device)

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

    def _randomize_start_variation(self, data):
        start_time_variation = self._catalog.get("gaussian")(0, data["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data["profile"]:
            line[0] += start_time_variation
            line[1] += start_time_variation

    def _randomize_consumption(self, data):
        consumption_variation = self._catalog.get("gaussian")(1, data["consumption_variation"])  # modification of the consumption
        consumption_variation = max(0, consumption_variation)  # to avoid to shift from consumption to production and vice-versa
        for nature in data["usage_profile"]:
            data["usage_profile"][nature] *= consumption_variation

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision

        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                       for nature in self._usage_profile}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # checking if the device has to start
            for usage in self._user_profile:
                if usage[0] == self._moment:  # if the current hour matches with the start of an usage
                    self._remaining_time = usage[1] - usage[0]  # incrementing usage duration
                    self._demand = self._usage_profile  # the demand for each nature of energy

        if self._remaining_time:  # if the device is active
            for nature in energy_wanted:
                energy_wanted[nature]["energy_minimum"] = self._min_power[nature]
                energy_wanted[nature]["energy_nominal"] = max(self._min_power[nature], min(self._max_power[nature], self._demand[nature] / self._remaining_time))  # the nominal energy demand is the total demand divided by the number of turns left
                # but it needs to be between the min and the max value
                energy_wanted[nature]["energy_maximum"] = self._max_power[nature]

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):  # method updating the device according to the decisions taken by the strategy
        super().react()  # actions needed for all the devices

        # effort management
        energy_wanted_nominal = dict()
        energy_accorded = dict()
        for nature in self._natures:
            energy_wanted_nominal[nature] = self.get_energy_wanted_nom(nature)  # the nominal quantity of energy wanted
            energy_accorded[nature] = self.get_energy_accorded_quantity(nature)

            for nature in self._natures:
                self._demand[nature.name] -= energy_accorded[nature]  # the energy which still has to be served
                # /!\ if there is a minimum power, remember to change the line above to take into account the start-up costs
                # otherwise, there is a risk that the total quantity of energy required is inferior to the minimum power necessary for the device to work

        activity = sum([self.get_energy_wanted_nom(nature) for nature in self.natures])  # activity is used as a boolean: it is the sum of the nominal quantities of energy asked
        if activity:  # if the device is active
            if self._remaining_time:  # decrementing the remaining time of use
                self._remaining_time -= 1

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def type(self):
        return "charger"


class Converter(Device):

    def __init__(self, name, contracts, agent, filename, upstream_aggregator, downstream_aggregator, profile_name, parameters=None):
        super().__init__(name, contracts, agent, [upstream_aggregator, downstream_aggregator], filename, None, profile_name, parameters)

        self._upstream_aggregator = {"name": upstream_aggregator.name, "nature": upstream_aggregator.nature.name, "contract": contracts}  # the aggregator who has to adapt
        self._downstream_aggregator = {"name": downstream_aggregator.name, "nature": downstream_aggregator.nature.name, "contract": contracts}   # the aggregator who has the last word

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self):
        # parsing the data
        file = open(self._filename, "r")
        data = load(file)

        # getting the user profile
        try:
            technical_data = data[self._usage_profile_name]
        except:
            raise DeviceException(f"{self._usage_profile_name} does not belong to the list of predefined profiles for the class {type(self).__name__}: {data.keys()}")

        file.close()

        self._energy_physical_limits = {"minimum_energy": 0, "maximum_energy": technical_data["capacity"]}
        self._efficiency = technical_data["efficiency"]  # the efficiency of the converter

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        # downstream side
        energy_wanted = {nature.name: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self.natures}  # consumption that will be asked eventually

        nature_name = self._downstream_aggregator["nature"]
        energy_wanted[nature_name]["energy_minimum"] = - self._energy_physical_limits["minimum_energy"]  # the physical minimum of energy this converter has to consume
        energy_wanted[nature_name]["energy_nominal"] = - self._energy_physical_limits["minimum_energy"]  # the physical minimum of energy this converter has to consume
        energy_wanted[nature_name]["energy_maximum"] = - self._energy_physical_limits["maximum_energy"]  # the physical maximum of energy this converter can consume

        # upstream side
        nature_name = self._upstream_aggregator["nature"]
        energy_wanted[nature_name]["energy_minimum"] = self._energy_physical_limits["minimum_energy"] / self._efficiency  # the physical minimum of energy this converter has to consume
        energy_wanted[nature_name]["energy_nominal"] = self._energy_physical_limits["minimum_energy"] / self._efficiency  # the physical minimum of energy this converter has to consume
        energy_wanted[nature_name]["energy_maximum"] = self._energy_physical_limits["maximum_energy"] / self._efficiency  # the physical maximum of energy this converter can consume

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):
        # determination of the energy consumed/produced
        energy_wanted_downstream = self._catalog.get(f"{self.name}.{self._downstream_aggregator['nature']}.energy_accorded")["quantity"]  # the energy asked by the downstream aggregator
        energy_available_upstream = self._catalog.get(f"{self.name}.{self._downstream_aggregator['nature']}.energy_accorded")["quantity"] / self._efficiency  # the energy accorded by the upstream aggregator
        energy_furnished_downstream = min(-energy_available_upstream, energy_wanted_downstream)
        energy_consumed_upstream = - energy_furnished_downstream / self._efficiency

        # downstream side
        price = self._catalog.get(f"{self.name}.{self._downstream_aggregator['nature']}.energy_accorded")["price"]
        self._catalog.set(f"{self.name}.{self._downstream_aggregator['nature']}.energy_accorded", {"quantity": energy_furnished_downstream, "price": price})  # the quantity of energy furnished to the downstream aggregator

        # upstream side
        price = self._catalog.get(f"{self.name}.{self._upstream_aggregator['nature']}.energy_accorded")["price"]
        self._catalog.set(f"{self.name}.{self._upstream_aggregator['nature']}.energy_accorded", {"quantity": energy_consumed_upstream, "price": price})  # the quantity of energy furnished to the downstream aggregator

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def type(self):
        return "converter"




