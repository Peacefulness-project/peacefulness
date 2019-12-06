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
        pass

    def _get_consumption(self):

        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        beginning = self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        start_time_variation = self._catalog.get("gaussian")(0, data_user["start_time_variation"])  # creation of a displacement in the user_profile
        duration_variation = self._catalog.get("gaussian")(1, data_user["duration_variation"])  # modification of the duration
        temperature_variation = self._catalog.get("gaussian")(0, data_user["temperature_variation"])  # modification of the temperature
        for line in data_user["profile"]:
            line[0][0] += start_time_variation  # modification of the starting hour of activity for an usage of the device
            line[0][1] *= duration_variation  #  modification of the ending hour of activity for an usage of the device

            line[1] = [line[1][i] + temperature_variation for i in range(3)]

        consumption_variation = self._catalog.get("gaussian")(1, data_device["consumption_variation"])  # modification of the G coefficient
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

            temperature_range[0] = line[1][0]  # the minimum of temperature accepted by the agent
            temperature_range[1] = line[1][1]  # the nominal of temperature accepted by the agent
            temperature_range[2] = line[1][2]  # the maximum of temperature accepted by the agent

            ratio = (beginning % time_step - line[0][0] % time_step) / time_step  # the percentage of use at the beginning (e.g for a device starting at 7h45 with an hourly time step, it will be 0.25)
            if ratio <= 0:  # in case beginning - start is negative
                ratio += 1
            for nature in self.natures:  # affecting a coefficient of energy to each nature used inb the process
                try:
                    repartition[nature.name] = ratio * self._repartition[nature.name]
                except:
                    pass

            self._user_profile.append([current_moment, repartition, temperature_range])  # adding the first time step when it will be turned on

            # intermediate time steps
            duration_residue = line[0][1] - (ratio * time_step)  # the residue of the duration is the remnant time during which the device is operating
            while duration_residue >= 1:  # as long as there is at least 1 full time step of functioning...
                self._user_profile.append([])
                current_moment += 1
                duration_residue -= 1
                self._user_profile[-1] = [current_moment, 1, temperature_range]  # ...a new entry is created with a ratio of 1 (full use)

            # final time step
            current_moment += 1
            ratio = duration_residue/time_step  # the percentage of use at the end (e.g for a device ending at 7h45 with an hourly time step, it will be 0.75)
            for nature in self.natures:  # affecting a coefficient of energy to each nature used in the process
                try:
                    repartition[nature.name] = ratio * self._repartition[nature.name]
                except:
                    pass

            self._user_profile.append([current_moment, repartition, temperature_range])  # adding the final time step before it will be turned off

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature.name not in self._repartition.keys():
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures[nature]["cluster"].devices.remove(self.name)
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

    def update(self):  # method updating needs of the devices before the supervision

        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                         for nature in self._repartition}  # Emin, Enom, Emax and the price

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

                for nature in energy_wanted:
                    # min power calculation:
                    energy_wanted[nature]["energy_minimum"] = time_step / self._thermal_inertia * self._G * (deltaTmin - deltaT0 * exp(-time_step/self._thermal_inertia))# / (1 - exp(-time_step/self._thermal_inertia))
                    energy_wanted[nature]["energy_minimum"] = min(energy_wanted[nature]["energy_minimum"] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be superior to the maximum power
                    energy_wanted[nature]["energy_minimum"] = max(0, energy_wanted[nature]["energy_minimum"])
                    # nominal power calculation:
                    energy_wanted[nature]["energy_nominal"] = time_step / self._thermal_inertia * self._G * (deltaTnom - deltaT0 * exp(-time_step/self._thermal_inertia))# / (1 - exp(-time_step/self._thermal_inertia))
                    energy_wanted[nature]["energy_nominal"] = min(energy_wanted[nature]["energy_nominal"] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be superior to the maximum power
                    energy_wanted[nature]["energy_nominal"] = max(0, energy_wanted[nature]["energy_nominal"])
                    # max power calculation:
                    energy_wanted[nature]["energy_maximum"] = time_step / self._thermal_inertia * self._G * (deltaTmax - deltaT0 * exp(-time_step/self._thermal_inertia))# / (1 - exp(-time_step/self._thermal_inertia))
                    energy_wanted[nature]["energy_maximum"] = min(energy_wanted[nature]["energy_maximum"] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be superior to the maximum power
                    energy_wanted[nature]["energy_maximum"] = max(0, energy_wanted[nature]["energy_maximum"])

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def _user_react(self):  # method updating the device according to the decisions taken by the supervisor

        for nature in self._natures:
            energy_wanted_min = self.get_energy_wanted_min(nature)  # minimum quantity of energy
            energy_wanted_max = self.get_energy_wanted_max(nature)  # maximum quantity of energy
            energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]
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
                        effort = min(1, (TminDis - Tint)/(Tmin - TminDis))*(Tint < Tmin) \
                                         + min(1, (TmaxDis - Tint)/(TmaxDis - Tmax))*(Tint > Tmax)  # effort generated by a too hot temperature

                        effort = self.natures[nature]["contract"].effort_modification(effort, self.agent.name)  # here, the contract may modify effort
                        self.agent.add_effort(effort, nature)  # effort increments

        # recalculating the temperature
        current_indoor_temperature = self._catalog.get(f"{self.agent.name}.current_indoor_temperature")
        previous_indoor_temperature = self._catalog.get(f"{self.agent.name}.previous_indoor_temperature")
        self._catalog.set(f"{self.agent.name}.previous_indoor_temperature", current_indoor_temperature)  # updating the previous indoor temperature

        current_outdoor_temperature = self._catalog.get("current_outdoor_temperature")
        previous_outdoor_temperature = self._catalog.get("previous_outdoor_temperature")

        time_step = self._catalog.get("time_step") * 3600

        deltaT0 = current_indoor_temperature - current_outdoor_temperature

        power = 0
        for nature in self._natures:
            power += self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"] / time_step

        current_indoor_temperature = power / self._G * self._thermal_inertia\
                                     + deltaT0 * exp(-time_step/self._thermal_inertia) + current_outdoor_temperature
        self._catalog.set(f"{self.agent.name}.current_indoor_temperature", current_indoor_temperature)

        self._moment = (self._moment + 1) % self._period  # incrementing the moment in the period


user_classes_dictionary[f"{Heating.__name__}"] = Heating

# * (1 - exp(-time_step / self._thermal_inertia))








