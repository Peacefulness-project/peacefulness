# Native packages
from math import exp, log
# Current packages
from src.common.DeviceMainClasses import AdjustableDevice
from src.common.Device import DeviceException, Device


class DomesticHeatPump(AdjustableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib\Subclasses\Device\DomesticHeatPump\DomesticHeatPump.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        outdoor_temperature_daemon = self._catalog.daemons[parameters["outdoor_temperature_daemon"]]
        self._location = outdoor_temperature_daemon.location  # the location of the device, in relation with the meteorological data

        # management of the location
        try:
            self._catalog.add("locations", [])
        except:
            pass

        location = self._catalog.get("locations")
        if self._location not in location:  # if the location of the device is not already in the list of locations
            location.append(self._location)  # add the location of the device to the list of locations

        # managing the temperature at the level of the agent
        try:  # there can be only one temperature in the catalog for each agent
            # then, using "try" allows only one device to create these entries and avoids to give these tasks to the agent
            outdoor_temperature = self._catalog.get(f"{self._location}.current_outdoor_temperature")
            self._catalog.add(f"{self.agent.name}.current_indoor_temperature", outdoor_temperature)
            self._catalog.add(f"{self.agent.name}.previous_indoor_temperature", outdoor_temperature)

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
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_user = self._read_consumer_data(profiles["user"])  # parsing the data
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        # we randomize a bit in order to represent reality better
        self._randomize_start_variation(data_user)
        self._randomize_consumption(data_device)
        self._randomize_duration(data_user)

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
        for line in data_user["profile"]:
            temperature_range = [0, 0, 0]  # temperature contains the min temperature, the nominal temperature and the max temperature
            repartition = dict()  # the repartition between the different energies
            current_moment = int(line[0][0] // time_step)  # the moment when the device will be turned on

            # creation of the user profile, where there are hours associated with the use of the device
            # first time step

            temperature_range[0] = line[1][0]  # the minimum of temperature accepted by the agent
            temperature_range[1] = line[1][1]  # the nominal of temperature accepted by the agent
            temperature_range[2] = line[1][2]  # the maximum of temperature accepted by the agent

            ratio = (self._moment % time_step - line[0][0] % time_step) / time_step  # the percentage of use at the beginning (e.g for a device starting at 7h45 with an hourly time step, it will be 0.25)
            if ratio <= 0:  # in case beginning - start is negative
                ratio += 1
            for nature_name in self._repartition:  # affecting a coefficient of energy to each nature used inb the process
                    repartition[nature_name] = ratio * self._repartition[nature_name]

            self._user_profile.append([current_moment, {nature: repartition[nature] for nature in repartition}, temperature_range])  # adding the first time step when it will be turned on

            if len(self._user_profile) >= 2:  # if there is an usage before this one
                if current_moment == self._user_profile[-2][0]:  # if the beginning of the new usage takes place at the same time as the end of the latter
                    old_repartition = self._user_profile[-2][1]
                    new_repartition = {nature_name: old_repartition[nature_name] + repartition[nature_name] for nature_name in repartition}  # the ratio of utilisation is the sum of the two former ratios
                    # the sum still cannot go above 1
                    old_temperature_range = self._user_profile[-2][2]
                    new_temperature = [0, 0, 0]

                    for i in range(len(temperature_range)):  # for each temperature we keep the worst case, i.e the higher
                        new_temperature[i] = max(temperature_range[i], old_temperature_range[i])
                        self._user_profile[-1] = [current_moment, {nature: new_repartition[nature] for nature in new_repartition}, new_temperature]  # adding the first time step when it will be turned on

            # intermediate time steps
            duration_residue = line[0][1] - (ratio * time_step)  # the residue of the duration is the remnant time during which the device is operating
            while duration_residue >= 1:  # as long as there is at least 1 full time step of functioning...
                current_moment += 1
                duration_residue -= 1
                self._user_profile.append([current_moment, self._repartition, temperature_range])  # ...a new entry is created with a ratio of 1 (full use)

            # final time step
            current_moment += 1
            ratio = duration_residue/time_step  # the percentage of use at the end (e.g for a device ending at 7h45 with an hourly time step, it will be 0.75)
            for nature_name in self._repartition:  # affecting a coefficient of energy to each nature used in the process
                    repartition[nature_name] = ratio * self._repartition[nature_name]

            self._user_profile.append([current_moment, {nature: repartition[nature] for nature in repartition}, temperature_range])  # adding the final time step before it will be turned off

        # removal of unused natures in the self._natures
        nature_to_remove = []
        for nature in self._natures:
            if nature.name not in self._repartition.keys():
                nature_to_remove.append(nature)
        for nature in nature_to_remove:
            self._natures[nature]["aggregator"].devices.remove(self.name)
            self._natures.pop(nature)
            self._catalog.remove(f"{self.name}.{nature.name}.energy_accorded")
            self._catalog.remove(f"{self.name}.{nature.name}.energy_wanted")

    def _randomize_start_variation(self, data):
        start_time_variation = self._catalog.get("gaussian")(0, data["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data["profile"]:
            line[0][0] += start_time_variation  # modification of the starting hour of activity for an usage of the device

    def _randomize_temperature(self, data):
        temperature_variation = self._catalog.get("gaussian")(0, data["temperature_variation"])  # modification of the temperature
        for line in data["profile"]:
            line[1] = [line[1][i] + temperature_variation for i in range(3)]

    def _randomize_duration(self, data):
        duration_variation = self._catalog.get("gaussian")(1, data["duration_variation"])  # modification of the duration
        duration_variation = max(0, duration_variation)  # to avoid negative durations
        for line in data["profile"]:
            line[0][1] *= duration_variation  # modification of the ending hour of activity for an usage of the device

    def _randomize_consumption(self, data):
        consumption_variation = self._catalog.get("gaussian")(1, data["consumption_variation"])  # modification of the consumption
        consumption_variation = max(0, consumption_variation)  # to avoid to shift from consumption to production and vice-versa
        data["usage_profile"][1] *= consumption_variation

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        for line in self._user_profile:

            if line[0] == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet

                current_indoor_temperature = self._catalog.get(f"{self.agent.name}.current_indoor_temperature")
                previous_indoor_temperature = self._catalog.get(f"{self.agent.name}.previous_indoor_temperature")

                current_outdoor_temperature = self._catalog.get(f"{self._location}.current_outdoor_temperature")
                previous_outdoor_temperature = self._catalog.get(f"{self._location}.previous_outdoor_temperature")

                time_step = self._catalog.get("time_step") * 3600

                deltaT0 = current_indoor_temperature - current_outdoor_temperature
                self._temperature_range = line[2]
                deltaTmin = line[2][0] - current_outdoor_temperature
                deltaTnom = line[2][1] - current_outdoor_temperature
                deltaTmax = line[2][2] - current_outdoor_temperature

                # TODO température Tfs

                Tcs = current_indoor_temperature + 273.15
                Tce = line[2][1] + 273.15
                Tfs = current_outdoor_temperature + 273.15
                Tfe = Tfs + (Tcs - Tce)

                Tmc = (Tcs - Tce) / (log(Tcs / Tce))
                Tmf = (Tfs - Tfe) / (log(Tfs / Tfe))

                COP = (Tmc - 273.15) / (Tmc - Tmf)

                for nature in energy_wanted:
                    # min power calculation:
                    energy_wanted[nature]["energy_minimum"] = time_step / self._thermal_inertia * self._G * (deltaTmin - deltaT0 * exp(-time_step/self._thermal_inertia)) / COP  # / (1 - exp(-time_step/self._thermal_inertia))
                    energy_wanted[nature]["energy_minimum"] = min(energy_wanted[nature]["energy_minimum"] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be superior to the maximum power
                    energy_wanted[nature]["energy_minimum"] = max(0, energy_wanted[nature]["energy_minimum"])
                    # nominal power calculation:
                    energy_wanted[nature]["energy_nominal"] = time_step / self._thermal_inertia * self._G * (deltaTnom - deltaT0 * exp(-time_step/self._thermal_inertia)) / COP  # / (1 - exp(-time_step/self._thermal_inertia))
                    energy_wanted[nature]["energy_nominal"] = min(energy_wanted[nature]["energy_nominal"] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be superior to the maximum power
                    energy_wanted[nature]["energy_nominal"] = max(0, energy_wanted[nature]["energy_nominal"])
                    # max power calculation:
                    energy_wanted[nature]["energy_maximum"] = time_step / self._thermal_inertia * self._G * (deltaTmax - deltaT0 * exp(-time_step/self._thermal_inertia)) / COP  # / (1 - exp(-time_step/self._thermal_inertia))
                    energy_wanted[nature]["energy_maximum"] = min(energy_wanted[nature]["energy_maximum"] * self._repartition[nature], self._max_power[nature])  # the real energy asked can't be superior to the maximum power
                    energy_wanted[nature]["energy_maximum"] = max(0, energy_wanted[nature]["energy_maximum"])

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):  # method updating the device according to the decisions taken by the supervisor
        Device.react(self)  # actions needed for all the devices

        for nature in self._natures:
            energy_wanted_min = self.get_energy_wanted_min(nature)  # minimum quantity of energy
            energy_wanted_max = self.get_energy_wanted_max(nature)  # maximum quantity of energy
            energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]

            if energy_wanted_min:  # if the device is active
                if self._remaining_time:  # decrementing the remaining time of use
                    self._remaining_time -= 1

                if not (energy_wanted_min <= energy_accorded <= energy_wanted_max):  # if the energy given is not in the borders defined by the user
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

                        self.agent.add_effort(effort, nature)  # effort increments

        # recalculating the temperature
        current_indoor_temperature = self._catalog.get(f"{self.agent.name}.current_indoor_temperature")

        time_step = self._catalog.get("time_step") * 3600

        power = 0
        for nature in self._natures:
            power += self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"] / time_step

        current_indoor_temperature += power / self._G * self._thermal_inertia
        self._catalog.set(f"{self.agent.name}.current_indoor_temperature", current_indoor_temperature)










