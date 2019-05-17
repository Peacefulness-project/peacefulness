# This device represents a washing machine

from common.Core import Device, DeviceException

import random as rnd


class WashingMachine(Device):

    def __init__(self, name, agent_name, clusters, configuration):
        super().__init__(name, agent_name, clusters)

        # if len(self._natures) != 1:
        #     raise DeviceException(f"A dishwasher must be attached to only one cluster")

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._use_ID = None  # this ID references the ongoing use
        self._is_done = []  # list of usage already done during one period
        self._hour = None  # the hour of the day

        self._period = 168  # this period represents a typical usage of a washing machine

        self._user_profile = dict()  # user profile of utilisation, describing user's priority
        # hour since the beginning of the period : [ priority, usage ID ]
        # the user profile lasts 1 week and starts monday at 00:00 AM

        self._usage_profile = {"LVE": [], "DHW": []}  # energy and interruptibility for one usage
        # [ energy consumption, priority ]

        # here washing machine is modeled as a device working 2 hours and consuming around 1 elec kWh and 1 heat kWh
        self._usage_profile["LVE"].append([0.35, 1])
        self._usage_profile["LVE"].append([0.2, 1])

        self._usage_profile["DHW"].append([1, 1])

        if configuration is "people_alone":  # this configuration corresponds to one usage a week
            self._people_alone()
        elif configuration is "couple":
            self._couple()
        elif configuration is "family":
            self._family()
        else:
            raise DeviceException(f"configuration must be people_alone, couple or family")

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        self._hour = self._catalog.get("physical_time").hour + self._catalog.get("physical_time").weekday()  # getting the hour of the day

    def _people_alone(self):

        n = 1
        for i in range(n):  # 1 time a week
            time_frame = rnd.randint(1, 5)  # the number of hours during which the device can be started
            start = rnd.randint((168//n)*i, (168//n)*(i+1)-time_frame-len(self._usage_profile))  # the start hour

            for j in range(time_frame):
                self._user_profile[start + j] = [j/time_frame, i]

    def _couple(self):

        n = 3
        for i in range(n):  # 3 times a week
            time_frame = rnd.randint(1, 5)  # the number of hours during which the device can be started
            start = rnd.randint((168//n)*i, (168//n)*(i+1)-time_frame-len(self._usage_profile))  # the start hour

            for j in range(time_frame):
                self._user_profile[start + j] = [j / time_frame, i]
        rnd.randint(0, 167)

    def _family(self):

        n = 7
        for i in range(n):  # 7 times a week
            time_frame = rnd.randint(1, 5)  # the number of hours during which the device can be started
            start = rnd.randint((168//n)*i, (168//n)*(i+1)-time_frame-len(self._usage_profile))  # the start hour

            for j in range(time_frame):
                self._user_profile[start + j] = [j/time_frame, i]

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):

        if self._hour == 0:  # if a new period is starting
            self._is_done = []  # the list of achieved appliances is reinitialized

        consumption = {"LVE": 0, "DHW": 0}  # consumption which will asked eventually
        priority = 0  # priority of the consumption

        if self._remaining_time == 0:  # if the device is not running
            # then it's the user profile which is taken into account

            for hour in self._user_profile:
                if hour == self._hour and self._user_profile[hour][1] not in self._is_done:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    for nature in self._usage_profile:
                        consumption[nature] = self._usage_profile[nature][0][0]  # the energy needed by the device during the first hour of utilization
                    priority = self._user_profile[hour][0]  # the current priority
                    self._is_done.append(self._user_profile[hour][1])  # adding the usage to the list of already satisfied usages

        else:  # if the device is running
            # then it's the usage profile who matters
            for nature in self._usage_profile:
                consumption[nature] = self._usage_profile[nature][-self._remaining_time][0]  # energy needed
            priority = self._usage_profile[nature][-self._remaining_time][1]  # priority associated

        for nature in self.natures:
            self._catalog.set(f"{self.name}.{nature.name}.asked_energy", consumption[nature.name])
        self._catalog.set(f"{self.name}.priority", priority)

    def react(self):

        self._hour = self._hour + 1 - (self._hour // self._period)*self._period  # incrementing the hour in the period

        if self._remaining_time != 0:  # decrementing the remaining time of use
            self._remaining_time -= 1
        else:
            if self._hour in self._user_profile:  # if it can correspond to the beginning of an usage
                for nature in self._natures:
                    if self._catalog.get(f"{self.name}.{nature.name}.asked_energy") != 0:  # if it has started
                        self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration
                        self._is_done.append(self._user_profile[self._hour][1])  # the usage is considered as done



