# This device represents a dishwasher

from common.Core import Device, DeviceException


class Dishwasher(Device):

    def __init__(self, name, agent_name, clusters):
        super().__init__(name, agent_name, clusters)

        if len(self._natures) != 1:
            raise DeviceException(f"A dishwasher must be attached to only one cluster")

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._use_ID = None  # this ID references the ongoing use
        self._is_done = []  # list of usage already done during one period
        self._hour = 0  # the hour of the day

        self._period = 0  # this period represents a typical usage of a dishwasher (e.g 2 days)

        self._user_profile = []  # user profile of utilisation, describing user's priority
        # hour since the beginning of the period : [ priority, usage ID ]
        # the user profile lasts 1 day and starts at 00:00 AM

        self._usage_profile = []  # energy and interruptibility for one usage
        # [ energy consumption, priority ]

        # here the dishwasher is modeled as a device working 2 hours and consuming 1 kWh
        self._usage_profile.append([0.5, 1])
        self._usage_profile.append([0.5, 1])

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        self._hour = self._catalog.get("physical_time").hour  # getting the hour of the day

        # adapting the user profile to the chosen time step
        time_step = self._catalog.get("time_step")  # getting back the value of the time step

        # if time_step - 1:  # if the time step is not of 1h
        #     new_profile = dict()
        #
        #     for key in self._user_profile:  # the keys represent the hour
        #         if key//time_step not in new_profile:  # if the entry is not created yet
        #             new_profile[key//time_step] = [0, 0]  # creating a new entry
        #         new_profile[key//time_step][0] = max(new_profile[key//time_step][0], self._user_profile[key][0])  # the priority is the max of the former priorities
        #
        #     self.user_profile = new_profile

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):

        if self._hour == 0:  # if a new period is starting
            self._is_done = []  # the list of achieved appliances is reinitialized

        consumption = 0  # consumption which will asked eventually
        priority = 0  # priority of the consumption

        if self._remaining_time == 0:  # if the device is not running
            # then it's the user profile which is taken into account

            for hour in self._user_profile:
                if hour == self._hour and self._user_profile[hour][1] not in self._is_done:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    consumption = self._usage_profile[0][0]  # the energy needed by the device during the first hour of utilization
                    priority = self._user_profile[hour][0]  # the current priority
                    self._is_done.append(self._user_profile[hour][1])  # adding the usage to the list of already satisfied usages

        else:  # if the device is running
            # then it's the usage profile who matters
            consumption = self._usage_profile[-self._remaining_time][0]  # energy needed
            priority = self._usage_profile[-self._remaining_time][1]  # priority associated

        for nature in self.natures:
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", consumption)
            self._catalog.set(f"{self.name}.priority", priority)

    def _user_react(self):

        self._hour = self._hour + 1 - (self._hour // self._period)*self._period  # incrementing the hour in the period

        if self._remaining_time != 0:  # decrementing the remaining time of use
            self._remaining_time -= 1
        else:
            if self._hour in self._user_profile:  # if it can correspond to the beginning of an usage
                for nature in self._natures:
                    if self._catalog.get(f"{self.name}.{nature.name}.energy_wanted") != 0:  # if it has started
                        self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration
                        self._is_done.append(self._user_profile[self._hour][1])  # the usage is considered as done


