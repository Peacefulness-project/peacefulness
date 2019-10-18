# ##############################################################################################
#
# Native packages
from math import exp
# Current packages
from common.DeviceMainClasses import AdjustableDevice
from common.Core import DeviceException
from tools.UserClassesDictionary import user_classes_dictionary


class Heating(AdjustableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/Heating.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)

        self._G = None  # this value represents the quantity of energy to necessary to heat
        self._thermal_inertia = None  # this value represents the velocity with which the house
        self._temperature_range = None
        self._repartition = None  # this dictionary contains the repartition of energy between the different energies used by the device
        # normally, the sum of these coefficients must be 1

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

        beginning = self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        start_time_variation = self._catalog.get("gaussian")(data_user["start_time_variation"])  # creation of a displacement in the user_profile
        duration_variation = self._catalog.get("gaussian")(data_user["duration_variation"])  # modification of the duration
        temperature_variation = self._catalog.get("gaussian")(data_user["temperature_variation"])  # modification of the temperature
        for line in data_user["profile"]:
            line[0][0] += start_time_variation  # modification of the starting hour of activity for an usage of the device
            line[0][1] *= duration_variation  #  modification of the ending hour of activity for an usage of the device

            line[1] = [line[1][i] + temperature_variation for i in range(3)]

        consumption_variation = self._catalog.get("gaussian")(data_device["consumption_variation"])  # modification of the G coefficient
        data_device["usage_profile"][1] *= consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        # parameters
        # max power
        self._max_power = {element: time_step * data_device["max_power"][element] for element in data_device["max_power"]}  # the maximum power is registered for each nature

        # repartition of consumption between the different natures of energy
        self._repartition = data_device["usage_profile"][0]  # this dictionary contains the repartition of energy between the different energies used by the device
        if sum(self._repartition.values()) != 1:  # normally, the sum of these coefficients must be 1
            raise DeviceException(f"device {self.name} of type {type(self)} repartition between different natures of energy is not equal to 100%")

        # thermal inertia
        self._G = data_device["usage_profile"][1]  # this value represents the quantity of energy to necessary to heat

        # G coefficient
        self._thermal_inertia = data_device["usage_profile"][2]  # this value represents the velocity with which the house


        # user profile
        temperature_range = [0, 0, 0]  # temperature contains the min temperature, the nominal temperature and the max temperature
        repartition = dict()

        for line in data_user["profile"]:
            current_moment = int(line[0][0] // time_step)  # the moment when the device will be turned on

            # creation of the user profile, where there are hours associated with the use of the device
            # first time step

            temperature_range[0] += line[1][0]  # the minimum of temperature accepted by the agent
            temperature_range[1] += line[1][1]  # the nominal of temperature accepted by the agent
            temperature_range[2] += line[1][2]  # the maximum of temperature accepted by the agent

            ratio = (beginning % time_step - line[0][0] % time_step) / time_step  # the percentage of use at the beginning (e.g for a device starting at 7h45 with an hourly time step, it will be 0.25)
            if ratio <= 0:  # in case beginning - start is negative
                ratio += 1
            for nature in self.natures:  # affecting a coeff of energy to each nature used inb the process
                repartition[nature.name] = ratio * self._repartition[nature.name]

            self._user_profile.append([current_moment, repartition, temperature_range])  # adding the first time step when it will be turned on

            # intermediate time steps
            duration_residue = line[0][1] - (ratio * time_step)  # the residue of the duration is the remnant time during which the device is operating
            self._user_profile[-1].append([])
            while duration_residue >= 1:  # as long as there is at least 1 full time step of functioning...
                current_moment += 1
                duration_residue -= 1
                self._user_profile[-1][-1] = [current_moment, 1]  # ...a new entry is created with a ratio of 1 (full use)

            # final time step
            current_moment += 1
            ratio = duration_residue/time_step  # the percentage of use at the end (e.g for a device ending at 7h45 with an hourly time step, it will be 0.75)
            for nature in self.natures:  # affecting a coeff of energy to each nature used in the process
                repartition[nature.name] = ratio * self._repartition[nature.name]

            self._user_profile.append([current_moment, repartition, temperature_range])  # adding the final time step before it will be turned off

        # usage profile
        self._usage_profile = []  # creation of an empty usage_profile with all cases ready

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature.name not in self._repartition.keys():
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures.pop(nature)
            self._catalog.remove(f"{self.name}.{nature.name}.energy_accorded")
            self._catalog.remove(f"{self.name}.{nature.name}.energy_wanted")

        # managing the temperature at the level of the agent
        try:  # there can be only one temperature in the catalog for each agent
            # then, using "try" allows only one device to create these entries and avoids to give these tasks to the agent
            self._catalog.add(f"{self.agent.name}.current_indoor_temperature")
            self._catalog.add(f"{self.agent.name}.previous_indoor_temperature")

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

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # method updating needs of the devices before the supervision

        consumption = {nature: [0, 0, 0] for nature in self._repartition}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # if the device is not running then it's the user_profile which is taken into account

            for line in self._user_profile:

                if line[0] == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet

                    current_indoor_temperature = self._catalog.get(f"{self.agent.name}.current_indoor_temperature")
                    previous_indoor_temperature = self._catalog.get(f"{self.agent.name}.previous_indoor_temperature")

                    current_outdoor_temperature = self._catalog.get("current_outdoor_temperature")
                    previous_outdoor_temperature = self._catalog.get("previous_outdoor_temperature")

                    time_step = self._catalog.get("time_step") * 3600

                    deltaT0 = previous_indoor_temperature - previous_outdoor_temperature
                    self._temperature_range = line[2]
                    deltaTmin = line[2][0] - current_outdoor_temperature
                    deltaTnom = line[2][1] - current_outdoor_temperature
                    deltaTmax = line[2][2] - current_outdoor_temperature

                    for nature in consumption:
                        # min power calculation:
                        consumption[nature][0] = time_step / self._thermal_inertia / self._G * (deltaTmin - deltaT0 * exp(-time_step/self._thermal_inertia)) / (1 - exp(-time_step/self._thermal_inertia))
                        consumption[nature][0] = min(consumption[nature][2] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be suprior to the maximum power
                        # nominal power calculation:
                        consumption[nature][1] = time_step / self._thermal_inertia / self._G * (deltaTnom - deltaT0 * exp(-time_step/self._thermal_inertia)) / (1 - exp(-time_step/self._thermal_inertia))
                        consumption[nature][1] = min(consumption[nature][2] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be suprior to the maximum power
                        # max power calculation:
                        consumption[nature][2] = time_step / self._thermal_inertia / self._G * (deltaTmax - deltaT0 * exp(-time_step/self._thermal_inertia)) / (1 - exp(-time_step/self._thermal_inertia))
                        consumption[nature][2] = min(consumption[nature][2] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be suprior to the maximum power

                    self._remaining_time = len(self._user_profile) - 1  # incrementing usage duration

            for nature in self.natures:
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted_minimum", consumption[nature.name][0])
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", consumption[nature.name][1])
                self._catalog.set(f"{self.name}.{nature.name}.energy_wanted_maximum", consumption[nature.name][2])

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor

        for nature in self._natures:
            energy_wanted_min = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_minimum")  # minimum quantity of energy
            energy_wanted_max = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted_maximum")  # maximum quantity of energy
            energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")
            if energy_wanted_min:  # if the device is active
                if self._remaining_time:  # decrementing the remaining time of use
                    self._remaining_time -= 1

                if not (energy_wanted_min < energy_accorded < energy_wanted_max):  # if the energy given is not in the borders defined by the user
                    # be careful when the adjustable device is a producer, as the notion of maximum and minimum can create confusion (negative values)

                    Tnom = self._temperature_range[1]  # ideal temperature
                    Tint = self._catalog.get(f"{self.agent.name}.current_indoor_temperature")  # temperature inside

                    Tmin = self._temperature_range[0]  # inferior accepted temperature
                    TminDis = Tnom - 2*(Tnom - Tmin)  # inferior temperature at which maximal effort is reached
                    Tmax = self._temperature_range[2]  # superior accepted temperature
                    TmaxDis = Tnom + 2*(Tmax - Tnom)  # superior temperature at which maximal effort is reached


                    for nature in self.natures:
                        # effort generated by a too cold temperature
                        effort = min(1, (Tint - TminDis)/(Tmin - TminDis))*(Tint < Tmin) \
                                         + min(1, (TmaxDis - Tint)/(TmaxDis - Tmax))*(Tint > Tmax)  # effort generated by a too hot temperature
                        effort = self._catalog.get(f"{self.agent.name}.{nature.name}.effort") + effort
                        effort = self.natures[nature][1].effort_modification(effort)  # here, the contract may modify effort                        self._catalog.set(f"{self.agent.name}.effort", effort)
                        self._catalog.set(f"{self.agent.name}.{nature.name}.effort", effort)

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

        self._moment = (self._moment + 1) % self._period  # incrementing the moment in the period


user_classes_dictionary[f"{Heating.__name__}"] = Heating












