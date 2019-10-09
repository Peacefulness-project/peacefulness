# ##############################################################################################
#
# Native packages
from json import load
from datetime import datetime
from math import ceil, exp
# Current packages
from common.DeviceMainClasses import AdjustableDevice
from common.Core import DeviceException


class Heating(AdjustableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters, filename="usr/DevicesProfiles/Heating.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)

        self._G = parameters["G"]
        self._thermal_inertia = parameters["thermal_inertia"]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device

        # Creation of specific entries
        for nature in self._natures:
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted_minimum")
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted_maximum")

        # managing the temperature at the level of the agent
        try:  # there can be only one temperature in the catalog for each agent
            # then, using "try" allows only one device to create these entries and avoids to give these tasks to the agent
            self._catalog.add(f"{self.agent.name}.current_indoor_temperature", self._parameters["initial_temperature"])
            self._catalog.add(f"{self.agent.name}.previous_indoor_temperature", self._parameters["initial_temperature"])

            try:  # if it is the first temperature-based device, it creates an entry repertoring all agents with a temperature in the catalog
                # later, a daemon in charge of updating temperatures saves the list and removes this entry
                self._catalog.add("agents_with_temperature_devices", {})
            except:
                pass

            agent_list = self._catalog.get("agents_with_temperature_devices")
            agent_list[self.agent.name] = [self._thermal_inertia, self._G]
            self._catalog.set("agents_with_temperature_devices", agent_list)

        except:
            pass

    def _get_consumption(self):

        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        start_time_variation = self._catalog.get("gaussian")(data_user["start_time_variation"])  # creation of a displacement in the user_profile
        for start_time in data_user["profile"]:
            start_time *= start_time_variation

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

                    current_indoor_temperature = self._catalog.get(f"{self.agent.name}.current_indoor_temperature")
                    previous_indoor_temperature = self._catalog.get(f"{self.agent.name}.previous_indoor_temperature")

                    current_outdoor_temperature = self._catalog.get("current_outdoor_temperature")
                    previous_outdoor_temperature = self._catalog.get("previous_outdoor_temperature")

                    time_step = self._catalog.get("time_step") * 3600

                    deltaT0 = previous_indoor_temperature - previous_outdoor_temperature

                    for nature in consumption:
                        # min power calculation:
                        deltaTnew = self._usage_profile[0][nature][0] - current_outdoor_temperature
                        consumption[nature][0] = time_step / self._thermal_inertia / self._G * (deltaTnew - deltaT0 * exp(-time_step/self._thermal_inertia)) / (1 - exp(-time_step/self._thermal_inertia))
                        consumption[nature][0] = min(consumption[nature][2], self._max_power[nature])  # the real energy asked can't be suprior to the maximum power
                        # nominal power calculation:
                        deltaTnew = self._usage_profile[0][nature][1] - current_outdoor_temperature
                        consumption[nature][1] = time_step / self._thermal_inertia / self._G * (deltaTnew - deltaT0 * exp(-time_step/self._thermal_inertia)) / (1 - exp(-time_step/self._thermal_inertia))
                        consumption[nature][1] = min(consumption[nature][2], self._max_power[nature])  # the real energy asked can't be suprior to the maximum power
                        # max power calculation:
                        deltaTnew = self._usage_profile[0][nature][2] - current_outdoor_temperature
                        consumption[nature][2] = time_step / self._thermal_inertia / self._G * (deltaTnew - deltaT0 * exp(-time_step/self._thermal_inertia)) / (1 - exp(-time_step/self._thermal_inertia))
                        consumption[nature][2] = min(consumption[nature][2], self._max_power[nature])  # the real energy asked can't be suprior to the maximum power

                    self._remaining_time = len(self._usage_profile) - 1  # incrementing usage duration

            for nature in self.natures:
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted_minimum", consumption[nature.name][0])
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", consumption[nature.name][1])
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted_maximum", consumption[nature.name][2])

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor

        self._moment = (self._moment + 1) % self._period  # incrementing the moment in the period

        for nature in self._natures:
            energy_wanted_min = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_minimum")  # minimum quantity of energy
            energy_wanted_max = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_maximum")  # maximum quantity of energy
            energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")
            if energy_wanted_min:  # if the device is active
                if self._remaining_time:  # decrementing the remaining time of use
                    self._remaining_time -= 1

                if not (energy_wanted_min < energy_accorded < energy_wanted_max):  # if the energy given is not in the borders defined by the user
                    # be careful when the adjustable device is a producer, as the notion of maximum and minimum can create confusion (negative values)
                    dissatisfaction = self._catalog.get(f"{self.agent.name}.dissatisfaction")
                    for nature in self.natures:

                        Tnom = self._usage_profile[0][nature][1]  # ideal temperature
                        Tint = self._catalog.get(f"{self.agent.name}.current_indoor_temperature")  # temperature inside

                        Tmin = self._usage_profile[0][nature][0]  # inferior accepted temperature
                        TminDis = Tnom - 2*(Tnom - Tmin)  # inferior temperature at which maximal dissatisfaction is reached
                        Tmax = self._usage_profile[0][nature][2]  # superior accepted temperature
                        TmaxDis = Tnom + 2*(Tmax - Tnom)  # superior temperature at which maximal dissatisfaction is reached

                        # dissatisfaction generated by a too cold temperature
                        dissatisfaction += min(1, (Tint - TminDis)/(Tmin - TminDis))*(Tint < Tmin) \
                                         + min(1, (TmaxDis - Tint)/(TmaxDis - Tmax))*(Tint > Tmax)  # dissatisfaction generated by a too hot temperature

                        dissatisfaction = self.natures[nature][1].dissatisfaction_modification(dissatisfaction)  # here, the contract may modify dissatisfaction
                        self._catalog.set(f"{self.agent.name}.dissatisfaction", dissatisfaction)
                        self._natures[nature][1].adjustable_dissatisfaction(self.agent.name, self.name, self.natures)

        # recalculating the temperature
        current_indoor_temperature = self._catalog.get(f"{self.agent.name}.current_indoor_temperature")
        previous_indoor_temperature = self._catalog.get(f"{self.agent.name}.previous_indoor_temperature")
        self._catalog.set(f"{self.agent.name}.previous_indoor_temperature", current_indoor_temperature)  # updating the previous indoor temperature

        current_outdoor_temperature = self._catalog.get("current_outdoor_temperature")
        previous_outdoor_temperature = self._catalog.get("previous_outdoor_temperature")

        time_step = self._catalog.get("time_step") * 3600

        deltaT0 = previous_indoor_temperature - previous_outdoor_temperature

        power = 0
        for nature in self._natures:
            power += self._catalog.get(f"{self.name}.{nature.name}.energy_accorded") / time_step

        current_indoor_temperature = power * self._G * self._thermal_inertia * (1 - exp(-time_step/self._thermal_inertia)) \
                                     + 0 * deltaT0 * exp(-time_step/self._thermal_inertia) + current_outdoor_temperature

        self._catalog.set(f"{self.agent.name}.current_indoor_temperature", current_indoor_temperature)














