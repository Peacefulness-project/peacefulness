# ##############################################################################################
#
# Native packages
from json import load
from datetime import datetime
from math import ceil
# Current packages
from common.DeviceMainClasses import AdjustableDevice
from common.Core import DeviceException


class Heating(AdjustableDevice):

    def __init__(self, name,  agent_name, clusters, user_type, consumption_device, filename="usr/DevicesProfiles/Heating.json"):
        super().__init__(name, agent_name, clusters, filename, user_type, consumption_device)

        self._inertia = None

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _get_consumption(self):

        # parsing the data
        file = open(self._filename, "r")
        data = load(file)

        # getting the user profile
        try:
            data_user = data["user_profile"][self._user_profile_name]
        except:
            raise DeviceException(f"{self._user_profile_name} does not belong to the list of predefined profiles: {data['user_profile'].keys()}")

        # getting the usage profile
        try:
            data_device = data["device_consumption"][self._usage_profile_name]
        except:
            raise DeviceException(f"{self._usage_profile_name} does not belong to the list of predefined profiles: {data['usage_profile'].keys()}")
        file.close()

        # creation of the consumption data
        time_step = self._catalog.get("time_step")
        self._period = int(data_user["period"]//time_step)  # the number of iteration corresponding to a period
        self._offset = data_user["offset"]
        # the period MUST be a multiple of the time step
        year = self._catalog.get("physical_time").year
        beginning = self._catalog.get("physical_time") - datetime(year=year, month=1, day=1)  # number of hours elapsed since the beginning of the year
        beginning = beginning.total_seconds()/3600
        beginning = (beginning - self._offset)/time_step % self._period
        self._moment = ceil(beginning)  # the position in the period where the device starts

        # we randomize a bit in order to represent reality better
        start_time_variation = (self._catalog.get("float")() - 0.5) * data_user["start_time_variation"]  # creation of a displacement in the user_profile
        for start_time in data_user["profile"]:
            start_time += start_time_variation

        duration_variation = (self._catalog.get("float")() - 0.5) * data_user["duration_variation"]  # modification of the duration
        consumption_variation = (self._catalog.get("float")() - 0.5) * data_device["consumption_variation"]  # modification of the consumption
        for line in data_device["usage_profile"]:
            line[0] += duration_variation
            for nature in line[1]:
                for element in line[1][nature]:
                    element += consumption_variation

        self._inertia = data_device["coeff"]

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        for hour in data_user["profile"]:
            self._user_profile.append((hour // time_step) * time_step)  # changing the hour fo fit the time step

        # usage_profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        duration = 0
        temperature_range = {nature: [0, 0, 0] for nature in data_device["usage_profile"][0][1]}  # temperature is a dictionary containing the consumption for each nature

        for i in range(len(data_device["usage_profile"])):
            buffer = duration % time_step  # the time already taken by the line i-1 of data in the current time_step
            duration += data_device["usage_profile"][i][0]

            if duration < time_step:  # as long as the next time step is not reached, consumption and duration are summed
                for nature in temperature_range:
                    temperature_range[nature][0] += data_device["usage_profile"][i][1][nature][0]
                    temperature_range[nature][1] += data_device["usage_profile"][i][1][nature][1]
                    temperature_range[nature][2] += data_device["usage_profile"][i][1][nature][2]

            else:  # we add a part of the energy consumption on the current step and we report the other part and we store the values into the self

                # fulling the usage_profile
                while duration // time_step:  # here we manage a constant consumption over several time steps

                    time_left = time_step - buffer  # the time available on the current time-step for the current consumption line i in data
                    # ratio = min(time_left / data_device["usage_profile"][i][0], 1)  # the min() ensures that a duration which doesn't reach the next time step is not overestimated
                    self._usage_profile.append({})
                    for nature in temperature_range:
                        self._usage_profile[-1][nature] = [0, 0, 0]
                        self._usage_profile[-1][nature][0] = (temperature_range[nature][0] + data_device["usage_profile"][i][1][nature][0]) / 2
                        self._usage_profile[-1][nature][1] = (temperature_range[nature][1] + data_device["usage_profile"][i][1][nature][1]) / 2
                        self._usage_profile[-1][nature][2] = (temperature_range[nature][2] + data_device["usage_profile"][i][1][nature][2]) / 2

                    duration -= time_step  # we decrease the duration of 1 time step
                    # buffer and consumption were the residue of line i-1, so they are not relevant anymore
                    buffer = 0
                    for nature in temperature_range:
                        for element in temperature_range[nature]:
                            element = 0

                for nature in temperature_range:
                    temperature_range[nature][0] = data_device["usage_profile"][i][1][nature][0] * duration / data_device["usage_profile"][i][0]  # energy reported
                    temperature_range[nature][1] = data_device["usage_profile"][i][1][nature][1] * duration / data_device["usage_profile"][i][0]  # energy reported
                    temperature_range[nature][2] = data_device["usage_profile"][i][1][nature][2] * duration / data_device["usage_profile"][i][0]  # energy reported

        # then, we affect the residue of energy if one, with the appropriate priority, to the usage_profile
        if duration:  # to know if the device need more time
            self._usage_profile.append(temperature_range)

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature.name not in self._usage_profile[0].keys():
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures.pop(nature)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # method updating needs of the devices before the supervision

        consumption = {nature: [0, 0, 0] for nature in self._usage_profile[0]}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # if the device is not running then it's the user_profile which is taken into account

            for hour in self._user_profile:
                if hour == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet

                    outdoor_temperature = self._catalog.get("outdoor_temperature")

                    for nature in consumption:
                        consumption[nature][0] = (self._usage_profile[0][nature][0] - outdoor_temperature) * self._inertia
                        consumption[nature][1] = (self._usage_profile[0][nature][1] - outdoor_temperature) * self._inertia
                        consumption[nature][2] = (self._usage_profile[0][nature][2] - outdoor_temperature) * self._inertia
                    self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration

            for nature in self.natures:
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted_minimum", consumption[nature.name][0])
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", consumption[nature.name][1])
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted_maximum", consumption[nature.name][2])

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor

        self._moment = (self._moment + 1) % self._period  # incrementing the moment in the period

        for nature in self._natures:
            energy_wanted_min = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_minimum")  # minimum quantity of energy
            energy_wanted = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")  # nominal quantity of energy
            energy_wanted_max = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_maximum")  # maximum quantity of energy
            energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")
            if energy_wanted_min:  # if the device is active
                if self._remaining_time:  # decrementing the remaining time of use
                    self._remaining_time -= 1

                if not (energy_wanted_min < energy_accorded < energy_wanted_max):  # if the energy given is not in the borders defined by the user
                    # be careful when the adjustable device is a producer, as the notion of maximum and minimum can create confusion (negative values)
                    self._agent._contracts[nature].adjustable_dissatisfaction(self.agent.name, self.name, self.natures)

                    self._latent_demand += energy_wanted - energy_accorded  # the energy in excess or in default

