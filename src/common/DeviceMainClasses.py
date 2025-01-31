# ##############################################################################################
# Native packages
from datetime import datetime, timedelta
# Current packages
from src.common.Device import Device
from src.tools.Utilities import into_list
from src.common.Messages import MessagesManager
from src.tools.ReadingFunctions import reading_functions
from typing import Dict

from math import ceil


# ##############################################################################################
class NonControllableDevice(Device):
    messages_manager = MessagesManager()
    messages_manager.complete_information_message("flexibility", [0])  # -, indicates the level of flexibility on the latent consumption or production
    messages_manager.complete_information_message("interruptibility", 0)  # -, indicates if the device is interruptible
    messages_manager.complete_information_message("coming_volume", 0)  # kWh, gives an indication on the latent consumption or production
    messages_manager.set_type("standard")
    information_message = messages_manager.create_information_message
    decision_message = messages_manager.create_decision_message
    information_keys = messages_manager.information_keys
    decision_keys = messages_manager.decision_keys

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_user = self._read_consumer_data(profiles["user"])  # parsing the data
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        if data_device["format"] == "week":
            # we randomize a bit in order to represent reality better
            consumption_variation = self._catalog.get("gaussian")(1, data_device["consumption_variation"])  # modification of the consumption
            for nature in data_device["usage_profile"]:
                for i in range(len(data_device["usage_profile"][nature]["weekday"])):
                    data_device["usage_profile"][nature]["weekday"][i] *= consumption_variation
                for i in range(len(data_device["usage_profile"][nature]["weekend"])):
                    data_device["usage_profile"][nature]["weekend"][i] *= consumption_variation

            self._randomize_start_variation(data_user)

            # adaptation of the data to the time step
            # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
            time_step = self._catalog.get("time_step")

            for nature in data_device["usage_profile"]:
                consumption_profile = 5 * data_device["usage_profile"][nature]["weekday"] + \
                                      2 * data_device["usage_profile"][nature]["weekend"]

                # user profile
                for line in consumption_profile:
                    current_moment = int(line // time_step)  # the moment when the device will be turned on

                    # creation of the user profile, where there are hours associated with the use of the device
                    # first time step

                    ratio = (self._moment % time_step - line % time_step) / time_step  # the percentage of use at the beginning (e.g for a device starting at 7h45 with an hourly time step, it will be 0.25)
                    if ratio <= 0:  # in case beginning - start is negative
                        ratio += 1
                    self._user_profile.append([current_moment, ratio])  # adding the first time step when it will be turned on

                    # intermediate time steps
                    duration_residue = 1 - (ratio * time_step)  # the residue of the duration is the remnant time during which the device is operating
                    while duration_residue >= 1:  # as long as there is at least 1 full time step of functioning...
                        current_moment += 1
                        duration_residue -= 1
                        self._user_profile.append([current_moment, 1])  # ...a new entry is created with a ratio of 1 (full use)

                    # final time step
                    current_moment += 1
                    ratio = duration_residue/time_step  # the percentage of use at the end (e.g for a device ending at 11h45 with an hourly time step, it will be 0.75)
                    self._user_profile.append([current_moment, ratio])  # adding the final time step before it wil be turned off

            # usage profile
            self._technical_profile = []  # creation of an empty usage_profile with all cases ready

            self._technical_profile = dict()
            for nature in data_device["usage_profile"]:  # data_usage is then added for each nature used by the device
                self._technical_profile[nature] = 5 * data_device["usage_profile"][nature]["weekday"] + \
                                                  2 * data_device["usage_profile"][nature]["weekend"]

        else:
            self._technical_profile = {nature.name: [] for nature in self.natures}
            for nature in self._natures:
                for i in range(8760):
                    self._technical_profile[nature.name].append(self._manage_non_weekly_data(data_device, i, nature.name))

        self._unused_nature_removal()  # remove unused natures

    def _manage_non_weekly_data(self, data_device: Dict, hour: int, nature_name: str):
        self._get_data = reading_functions[data_device["format"]]  # the format acts a tag returning the relevant reading function
        time_step_value = self._catalog.get("time_step")
        time_step_length = self._catalog.get("time_step")

        # relevant datetime identification
        real_physical_time_start = datetime(year=2000, month=1, day=1, hour=0) + timedelta(hours=hour)

        # ##########################################################################################
        # start management
        rounded_physical_time_start = datetime(
            year=real_physical_time_start.year,
            month=real_physical_time_start.month,
            day=real_physical_time_start.day,
            hour=real_physical_time_start.hour
        )  # datetime rounded to the hour, for coherence with data format
        first_hour_fraction = 1 - (real_physical_time_start - rounded_physical_time_start).days / 24

        # ##########################################################################################
        # end management
        real_physical_time_end = real_physical_time_start + timedelta(hours=time_step_value * time_step_length)
        rounded_physical_time_end = datetime(
            year=real_physical_time_end.year,
            month=real_physical_time_end.month,
            day=real_physical_time_end.day,
            hour=real_physical_time_end.hour
        )  # datetime rounded to the hour, for coherence with data format
        last_hour_fraction = (real_physical_time_end - rounded_physical_time_end).days / 24

        # start date
        needed_hours = list()  # relevant hours to read, with a coefficient for the first and last hours
        needed_hours.append((0, first_hour_fraction))  # first hour management

        # central hours
        time = rounded_physical_time_start + timedelta(hours=1)
        offset = 1
        while (time - rounded_physical_time_end).days > 0:  # while the last hour is not reached
            needed_hours.append((-offset, 1))
            time += timedelta(hours=1)
            offset += 1

        # end date
        needed_hours.append((-self._period, last_hour_fraction))  # last hour management

        value = 0
        for i in range(len(needed_hours)):
            value += self._get_data(data_device[nature_name], real_physical_time_start, needed_hours[i][0]) * needed_hours[i][1]

        return value

    def _randomize_start_variation(self, data):
        start_time_variation = self._catalog.get("gaussian")(0, data["start_time_variation"])  # creation of a displacement in the user_profile
        self._moment = int((self._moment + start_time_variation) // self._catalog.get("time_step") % self._period)

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
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        for nature_name in energy_wanted:
            energy_wanted[nature_name]["energy_minimum"] = self._technical_profile[nature_name][self._moment]  # energy needed for all natures used by the device
            energy_wanted[nature_name]["energy_nominal"] = self._technical_profile[nature_name][self._moment]  # energy needed for all natures used by the device
            energy_wanted[nature_name]["energy_maximum"] = self._technical_profile[nature_name][self._moment]  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


# ##############################################################################################
class ShiftableDevice(Device):  # a consumption which is shiftable
    messages_manager = MessagesManager()
    messages_manager.complete_information_message("flexibility", [])  # -, indicates the level of flexibility on the latent consumption or production
    messages_manager.complete_information_message("interruptibility", 0)  # -, indicates if the device is interruptible
    messages_manager.complete_information_message("coming_volume", 0)  # kWh, gives an indication on the latent consumption or production
    messages_manager.set_type("standard")
    information_message = messages_manager.create_information_message
    decision_message = messages_manager.create_decision_message
    information_keys = messages_manager.information_keys
    decision_keys = messages_manager.decision_keys

    def __init__(self, name, contracts, agent, aggregators, filename, profiles, parameters=None):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)
        self._use_ID = None  # this ID references the ongoing use
        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._is_done = []  # list of usage already done during one period
        # a list containing the data necessary to manage priority if the device is interrupted
        self._interruption_data = [False,  # if the device has been interrupted
                                   0,  # last time step to launch the device initially
                                   0]  # duration during which the device has functioned
        self._coming_volume = {nature.name: 0 for nature in self._natures}  # kWh, the remnant energy consumption to finish a cycle

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_user = self._read_consumer_data(profiles["user"])  # parsing the data
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

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
        # the beginning and the end are chosen outside the period in order to avoid possible confusions
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
        self._technical_profile = []  # creation of an empty usage_profile with all cases ready
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

            else:  # we add a part of the energy consumption on the current step, we report the other part and we store the values into the self
                # fulling the usage_profile
                while duration // time_step:  # here we manage a constant consumption over several time steps
                    self._technical_profile.append([{}, 0])  # creation of the entry, with a dictionary for the different natures
                    time_left = time_step - buffer  # the time available on the current time-step for the current consumption line i in data
                    ratio = min(time_left / data_device["usage_profile"][i][0], 1)  # the min() ensures that a duration which doesn't reach the next time step is not overestimated
                    for nature in data_device["usage_profile"][i][1]:  # consumption is added for each nature present
                        self._technical_profile[-1][0][nature] = 0  # creation of the entry
                        self._technical_profile[-1][0][nature] = consumption[nature] + data_device["usage_profile"][i][1][nature] * ratio

                    self._technical_profile[-1][1] = max(priority, data_device["usage_profile"][i][2])  # the priority is the max betwwen the former priority and the new
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
            self._technical_profile.append([0, 0])  # creation of the entry
            priority = data_device["usage_profile"][-1][2]
            self._technical_profile[-1][0] = consumption
            self._technical_profile[-1][1] = priority

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature.name not in self._technical_profile[0][0]:
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures[nature]["aggregator"].devices.remove(self.name)
            self._natures.pop(nature)
            self._catalog.remove(f"{self.name}.{nature.name}.energy_accorded")
            self._catalog.remove(f"{self.name}.{nature.name}.energy_wanted")

    def _randomize_start_variation(self, data):
        start_time_variation = self._catalog.get("gaussian")(0, data["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data["profile"]:
            line[0] = (line[0] + start_time_variation) % self._period

    def _randomize_duration(self, data):
        duration_variation = self._catalog.get("gaussian")(1, data["duration_variation"])  # modification of the duration
        duration_variation = max(duration_variation/10, duration_variation)  # to avoid negative and null durations
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
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        if not self._remaining_time:  # if the device is not running then it's the user_profile who is taken into account
            for i in range(len(self._user_profile)):
                line = self._user_profile[i]
                if line[0] == self._moment and line[2] not in self._is_done:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in energy_wanted:
                        energy_wanted[nature]["energy_maximum"] = self._technical_profile[0][0][nature]  # the energy needed by the device during the first hour of utilization
                        energy_wanted[nature]["energy_nominal"] = line[1] * self._technical_profile[0][0][nature]  # it modelizes the emergency
                        start_moment = self._moment - line[2]
                        energy_wanted[nature]["flexibility"] = [1 for j in range(start_moment, len(self._user_profile))]
                        energy_wanted[nature]["interruptibility"] = 0  # such devices are not interruptible once their cycle hast started
                        self._coming_volume[nature] = sum([self._technical_profile[j][0][nature] for j in range(len(self._technical_profile))])
                        energy_wanted[nature]["coming_volume"] = self._coming_volume[nature]  # kWh, the energy consumed on the whole cycle

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
                ratio = self._technical_profile[-self._remaining_time][1]  # emergency associated
                energy_wanted[nature]["energy_minimum"] = 0
                energy_wanted[nature]["energy_maximum"] = self._technical_profile[-self._remaining_time][0][nature]  # energy needed
                energy_wanted[nature]["energy_nominal"] = ratio * energy_wanted[nature]["energy_maximum"]
                energy_wanted[nature]["flexibility"] = []
                energy_wanted[nature]["interruptibility"] = 0  # such devices are not interruptible once their cycle hast started
                energy_wanted[nature]["coming_volume"] = self._coming_volume[nature]

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):
        super().react()  # actions needed for all the devices

        energy_wanted = sum([self.get_energy_wanted_nom(nature) for nature in self.natures])  # total energy wanted by the device
        energy_accorded = sum([self.get_energy_accorded_quantity(nature) for nature in self.natures])  # total energy accorded to the device
        for nature in self._natures:
            self._coming_volume[nature.name] -= self.get_energy_accorded_quantity(nature)

        if self._remaining_time and energy_accorded < energy_wanted:  # if the device has started and not been served, then it has been interrupted
            self._interruption_data[0] = True  # it is flagged as "interrupted"
        elif energy_wanted:  # if the device is active
            if energy_accorded:  # if it has been served
                if self._remaining_time:  # if it has started
                    self._remaining_time -= 1  # decrementing the remaining time of use
                else:  # if it has not started yet
                    self._remaining_time = len(self._technical_profile) - 1
                self._interruption_data[2] += 1  # it has been working for one more time step
            else:  # if it has not started
                self._is_done.pop()

            energy_min = sum([self.get_energy_wanted_min(nature) for nature in self.natures])  # total minimum energy wanted by the device


# ##############################################################################################
class AdjustableDevice(Device):  # a consumption which is adjustable
    messages_manager = MessagesManager()
    messages_manager.complete_information_message("flexibility", [])  # -, indicates the level of flexibility on the latent concumption or production
    messages_manager.complete_information_message("interruptibility", 0)  # -, indicates if the device is interruptible
    messages_manager.complete_information_message("coming_volume", 0)  # kWh, gives an indication on the latent consumption or production
    messages_manager.set_type("standard")
    information_message = messages_manager.create_information_message
    decision_message = messages_manager.create_decision_message
    information_keys = messages_manager.information_keys
    decision_keys = messages_manager.decision_keys

    def __init__(self, name, contracts, agent, aggregators, filename, profiles, parameters=None):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run

        self._latent_demand = dict()  # the energy in excess or in default after being served

        for nature in self._natures:
            self._latent_demand[nature] = 0

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_user = self._read_consumer_data(profiles["user"])  # parsing the data
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

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
        self._tecnhical_profile = []  # creation of an empty usage_profile with all cases ready

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
                    self._tecnhical_profile.append({})
                    for nature in consumption:
                        self._tecnhical_profile[-1][nature] = [0, 0, 0]
                        self._tecnhical_profile[-1][nature][0] = (consumption[nature][0] + data_device["usage_profile"][i][1][nature][0] * ratio)
                        self._tecnhical_profile[-1][nature][1] = (consumption[nature][1] + data_device["usage_profile"][i][1][nature][1] * ratio)
                        self._tecnhical_profile[-1][nature][2] = (consumption[nature][2] + data_device["usage_profile"][i][1][nature][2] * ratio)

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
            self._tecnhical_profile.append(consumption)

        self._unused_nature_removal()  # remove unused natures

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        if self._remaining_time == 0:  # if the device is not running then it's the user_profile which is taken into account

            for hour in self._user_profile:
                if hour == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in energy_wanted:
                        energy_wanted[nature]["energy_minimum"] = self._tecnhical_profile[0][nature][0] + self._latent_demand[nature]
                        energy_wanted[nature]["energy_nominal"] = self._tecnhical_profile[0][nature][1] + self._latent_demand[nature]
                        energy_wanted[nature]["energy_maximum"] = self._tecnhical_profile[0][nature][2] + self._latent_demand[nature]
                    self._remaining_time = len(self._tecnhical_profile) - 1  # incrementing usage duration

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


# ##############################################################################################
class ChargerDevice(Device):  # a consumption which is adjustable
    messages_manager = MessagesManager()
    messages_manager.complete_information_message("flexibility", [])  # -, indicates the level of flexibility on the latent concumption or production
    messages_manager.complete_information_message("interruptibility", 0)  # -, indicates if the device is interruptible
    messages_manager.complete_information_message("coming_volume", 0)  # kWh, gives an indication on the latent consumption or production
    messages_manager.set_type("standard")
    information_message = messages_manager.create_information_message
    decision_message = messages_manager.create_decision_message
    information_keys = messages_manager.information_keys
    decision_keys = messages_manager.decision_keys

    def __init__(self, name, contracts, agent, aggregators, filename, profiles, parameters=None):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_user = self._read_consumer_data(profiles["user"])  # parsing the data
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

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
        self._technical_profile = data_device["usage_profile"]  # creation of an empty usage_profile with all cases ready
        self._demand = self._technical_profile  # if the simulation begins during an usage, the demand has to be initialized

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
        # message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        if self._remaining_time == 0:  # checking if the device has to start
            for usage in self._user_profile:
                if usage[0] == self._moment:  # if the current hour matches with the start of an usage
                    self._remaining_time = usage[1] - usage[0]  # incrementing usage duration
                    self._demand = self._technical_profile  # the demand for each nature of energy

        if self._remaining_time:  # if the device is active
            for nature in energy_wanted:
                energy_wanted[nature]["energy_minimum"] = self._min_power[nature]
                energy_wanted[nature]["energy_nominal"] = max(self._min_power[nature], min(self._max_power[nature], self._demand[nature] / self._remaining_time))  # the nominal energy demand is the total demand divided by the number of turns left
                # but it needs to be between the min and the max value
                energy_wanted[nature]["energy_maximum"] = self._max_power[nature]
                energy_wanted[nature]["flexibility"] = [1 - self._min_power[nature]/self._max_power[nature] for _ in range(ceil(self._demand[nature]/self._max_power[nature]))]
                energy_wanted[nature]["interruptibility"] = 1 - int(self._min_power[nature] is True)
                energy_wanted[nature]["coming_volume"] = self._demand[nature]  # kWh, the energy consumed on the whole cycle

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


# ##############################################################################################
class Converter(Device):
    messages_manager = MessagesManager()
    messages_manager.complete_information_message("efficiency", 1)  # kWh/kWh, a value of the efficiency of the conversion is added
    messages_manager.set_type("converter")
    information_message = messages_manager.create_information_message
    decision_message = messages_manager.create_decision_message
    information_keys = messages_manager.information_keys
    decision_keys = messages_manager.decision_keys

    def __init__(self, name, contracts, agent, filename, upstream_aggregators_list, downstream_aggregators_list, profiles, parameters=None):
        upstream_aggregators_list = into_list(upstream_aggregators_list)
        downstream_aggregators_list = into_list(downstream_aggregators_list)
        super().__init__(name, contracts, agent, upstream_aggregators_list + downstream_aggregators_list, filename, profiles, parameters)

        contracts = {contract.nature.name: contract for contract in contracts}
        self._upstream_aggregators_list = [{"name": aggregator.name, "nature": aggregator.nature.name, "contract": contracts[aggregator.nature.name]} for aggregator in upstream_aggregators_list]  # list of aggregators involved in the production of energy. The order is not important.
        self._downstream_aggregators_list = [{"name": aggregator.name, "nature": aggregator.nature.name, "contract": contracts[aggregator.nature.name]} for aggregator in downstream_aggregators_list]  # list of aggregators involved in the consumption of energy. The order is important: the first aggregator defines the final quantity of energy

        time_step = self._catalog.get("time_step")
        self._energy_physical_limits = {"minimum_energy": 0, "maximum_energy": parameters["max_power"] * time_step}

        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            self._catalog.add(f"{self.name}.{nature_name}.efficiency", None)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._efficiency = data_device["efficiency"]  # the efficiency of the converter for each nature of energy

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        # downstream side
        for aggregator in self ._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted[nature_name]["energy_minimum"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = - self._energy_physical_limits["maximum_energy"] * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

        # upstream side
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted[nature_name]["energy_minimum"] = self._energy_physical_limits["minimum_energy"] / self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = self._energy_physical_limits["minimum_energy"] / self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = self._energy_physical_limits["maximum_energy"] / self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def second_update(self):  # a method used to harmonize aggregator's decisions concerning multi-energy devices
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        # determination of the energy consumed/produced
        energy_wanted_downstream = []
        energy_available_upstream = []
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_wanted_downstream.append(-self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"] / self._efficiency[nature_name])  # the energy asked by the downstream aggregator
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            energy_available_upstream.append(self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"] / self._efficiency[nature_name])  # the energy accorded by the upstream aggregator

        limit_energy_upstream = min(energy_available_upstream)
        limit_energy_downstream = min(energy_wanted_downstream)
        raw_energy_transformed = min(limit_energy_upstream, limit_energy_downstream)

        # downstream side
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]

            # resetting the demand
            energy_wanted[nature_name]["energy_minimum"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["price"] = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["price"]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"] = - raw_energy_transformed * self._efficiency[nature_name]
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

        # upstream side
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]

            # resetting the demand
            energy_wanted[nature_name]["energy_minimum"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_nominal"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name]["energy_maximum"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name]["price"] = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["price"]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name]["efficiency"] = self._efficiency[nature_name]

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"] = raw_energy_transformed * self._efficiency[nature_name]
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

    def react(self):
        super().react()  # actions needed for all the devices

        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            self._catalog.set(f"{self.name}.{nature_name}.efficiency", self._efficiency[nature_name])


# ##############################################################################################
class Storage(Device):
    messages_manager = MessagesManager()
    messages_manager.complete_information_message("state_of_charge", 0)  # kWh/kWh, the ration of charge stored energy / (max energy - min energy)
    messages_manager.complete_information_message("capacity", 0)  # kWh, the maximum energy recoverable from the storage device (max energy - min energy)
    messages_manager.complete_information_message("self_discharge_rate", 0)  # kWh/kWh, the rate at which the storage device is dicharging
    messages_manager.complete_information_message("efficiency", 1)  # kWh/kWh, the efficiency of the cycle
    messages_manager.set_type("storage")
    information_message = messages_manager.create_information_message
    decision_message = messages_manager.create_decision_message
    information_keys = messages_manager.information_keys
    decision_keys = messages_manager.decision_keys

    def __init__(self, name, contracts, agent, filename, aggregators, profiles, parameters):

        self._capacity = parameters["capacity"]
        self._state_of_charge = parameters["initial_SOC"]

        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profile):
        time_step = self._catalog.get("time_step")
        data_device = self._read_technical_data(profile["device"])  # parsing the data

        # randomization
        self._randomize_multiplication(data_device["charge"]["efficiency"], data_device["efficiency_variation"])
        self._randomize_multiplication(data_device["discharge"]["efficiency"], data_device["efficiency_variation"])
        self._randomize_multiplication(data_device["charge"]["power"], data_device["power_variation"])
        self._randomize_multiplication(data_device["discharge"]["power"], data_device["power_variation"])

        minimum_energy_variation = self._catalog.get("gaussian")(1, data_device["capacity_variation"])  # modification of the minimum_energy
        minimum_energy_variation = min(max(0, minimum_energy_variation), self._capacity)  # to avoid negative values and values beyond the maximum minimum_energy
        data_device["minimum_energy"] *= minimum_energy_variation

        # setting
        self._efficiency = {"charge": data_device["charge"]["efficiency"], "discharge": data_device["discharge"]["efficiency"]}  # efficiency
        # self._max_transferable_energy = {"charge": data_device["charge"]["power"] * time_step, "discharge": data_device["discharge"]["power"] * time_step}

        self._catalog.add(f"{self.name}.energy_stored", self._capacity * self._state_of_charge)  # the energy stored at the starting point
        self._min_energy = data_device["minimum_energy"]  # the minimum of energy needed in the device below which it cannot unload energy

        self._charge_nature = data_device["charge"]["nature"]
        self._discharge_nature = data_device["discharge"]["nature"]

        self._max_transferable_energy = {"charge": lambda: data_device["charge"]["power"] * time_step,
                                         "discharge": lambda: data_device["discharge"]["power"] * time_step}

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        old_energy_stored = self._catalog.get(f"{self.name}.energy_stored")
        energy_stored = self._degradation_of_energy_stored()  # reduction of the energy stored over time
        self._catalog.set(f"{self.name}.energy_stored", energy_stored)

        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually
        energy_stored = self._catalog.get(f"{self.name}.energy_stored")

        energy_wanted[self._discharge_nature]["energy_minimum"] = - min(self._max_transferable_energy["discharge"](), max((energy_stored - self._min_energy) * self._efficiency["discharge"], 0))  # the discharge mode, where energy is "produced"
        energy_wanted[self._charge_nature]["energy_maximum"] = min(self._max_transferable_energy["charge"](), (self._capacity - energy_stored) / self._efficiency["charge"])  # the charge mode, where energy is "consumed"

        energy_wanted[self._charge_nature]["efficiency"] = self._efficiency
        energy_wanted[self._charge_nature]["self_discharge_rate"] = 1 - old_energy_stored/energy_stored
        energy_wanted[self._charge_nature]["capacity"] = self._capacity
        energy_wanted[self._charge_nature]["state_of_charge"] = self._state_of_charge

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):
        super().react()  # actions needed for all the devices
        energy_stored = self._catalog.get(f"{self.name}.energy_stored")

        for nature in self.natures:
            energy_accorded = self.get_energy_accorded(nature)

            if energy_accorded["quantity"] < 0:  # if the device unloads energy
                energy_stored += energy_accorded["quantity"] / self._efficiency["discharge"]
            else:  # if the device loads energy
                energy_stored += energy_accorded["quantity"] * self._efficiency["charge"]

        self._catalog.set(f"{self.name}.energy_stored", energy_stored)
        self._state_of_charge = (energy_stored - self._min_energy) / self._capacity

    def _degradation_of_energy_stored(self):  # a class-specific function reducing the energy stored over time
        pass

    def make_balances(self):
        super().make_balances()  # non-specific actions

        for nature in self.natures:
            aggregator = self.natures[nature]["aggregator"]
            energy_stored_aggregator = self._catalog.get(f"{aggregator.name}.energy_stored")
            energy_storable_aggregator = self._catalog.get(f"{aggregator.name}.energy_storable")

            energy_stored_device = self._catalog.get(f"{self.name}.energy_stored") * self._efficiency["discharge"]
            energy_storable_device = (self._capacity - self._catalog.get(f"{self.name}.energy_stored")) / self._efficiency["charge"]

            self._catalog.set(f"{aggregator.name}.energy_stored", energy_stored_aggregator + energy_stored_device)
            self._catalog.set(f"{aggregator.name}.energy_storable", energy_storable_aggregator + energy_storable_device)








