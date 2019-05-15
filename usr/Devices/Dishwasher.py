from common.Core import Device, DeviceException


class Dishwasher(Device):

    def __init__(self, name, agent_name, clusters, configuration):
        super().__init__(name, agent_name, clusters)

        if len(self._natures) != 1:
            raise DeviceException(f"A dishwasher must be attached to only one cluster")

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._use_ID = None  # this ID references the ongoing use
        self._is_done = []  # list of usage already done during one period
        self._hour = None  # the hour of the day

        self._period = 24  # this period represents a typical usage of a dishwasher (e.g 2 days)

        self._user_profile = dict()  # user profile of utilisation, describing user's priority
        # hour since the beginning of the period : [ priority, usage ID ]

        self._usage_profile = []  # energy and interruptibility for one usage
        # [ energy consumption, priority ]

        # here the dishwasher is modeled as a device working 2 hours and consuming 1 kWh
        self._usage_profile.append([0.5, 1])
        self._usage_profile.append([0.5, 1])

        if configuration is "morning":
            self._morning_usage()
        elif configuration is "afternoon":
            self._afternoon_usage()
        elif configuration is "evening":
            self._evening_usage()
        elif configuration is "several_usages":
            self._several_usages()
        else:
            raise DeviceException(f"configuration must be morning, afternoon, evening or several_usages")

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        self._hour = self._catalog.get("physical_time").hour  # getting the hour of the day

    def _morning_usage(self):
        self._user_profile[ 8] = [0/3, 0]
        self._user_profile[ 9] = [0/3, 0]
        self._user_profile[10] = [0/3, 0]
        self._user_profile[11] = [0/3, 0]

    def _afternoon_usage(self):
        self._user_profile[13] = [0/3, 0]
        self._user_profile[14] = [0/3, 0]
        self._user_profile[15] = [0/3, 0]
        self._user_profile[16] = [0/3, 0]

    def _evening_usage(self):
        self._user_profile[20] = [0/3, 0]
        self._user_profile[21] = [0/3, 0]
        self._user_profile[22] = [0/3, 0]
        self._user_profile[23] = [0/3, 0]

    def _several_usages(self):
        # morning usage
        self._user_profile[ 8] = [0/3, 0]
        self._user_profile[ 9] = [0/3, 0]
        self._user_profile[10] = [0/3, 0]
        self._user_profile[11] = [0/3, 0]

        # evening usage
        self._user_profile[20] = [0/3, 1]
        self._user_profile[21] = [0/3, 1]
        self._user_profile[22] = [0/3, 1]
        self._user_profile[23] = [0/3, 1]

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
                print(f"{hour}, {self._hour }")
                print(f"{self._user_profile[hour][1]}, {self._is_done}")
                if hour == self._hour and self._user_profile[hour][1] not in self._is_done:  # if a consumption has been scheduled and if it has not been fulfilled yet
                    consumption = self._usage_profile[0][0]  # the energy needed by the device during the first hour of utilization
                    priority = self._user_profile[hour][0]  # the current priority
                    self._is_done.append(self._user_profile[hour][1])  # adding the usage to the list of already satisfied usages

        else:  # if the device is running
            # then it's the usage profile who matters
            consumption = self._usage_profile[-self._remaining_time][0]  # energy needed
            priority = self._usage_profile[-self._remaining_time][1]  # priority associated

        for nature in self.natures:
            print(consumption)
            self._catalog.set(f"{self.name}.{nature.name}.asked_energy", consumption)
            self._catalog.set(f"{self.name}.priority", priority)

        print("\n")

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



