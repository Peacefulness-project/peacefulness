from src.common.DeviceMainClasses import ChargerDevice
from src.common.Device import Device


class HotWaterTank(ChargerDevice, Device):

    def __init__(self, name, contracts, agent, aggregators, user_profile_name, usage_profile_name, filename="lib/Subclasses/Device/HotWaterTank/HotWaterTank.json"):
        super().__init__(name, contracts, agent, aggregators, filename, user_profile_name, usage_profile_name)

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

        # user_profile
        self._user_profile = [[i * time_step, 0] for i in range(self._period)]  # creation of an empty user_profile with all cases ready

        # month dependency
        self._month_dependency = data_user["month_dependency"]

        # location
        self._location = data_user["location"]

        # adding a null priority at the beginning and the end of the period
        # the beginning and the end are chosen outside of the period in order to avoid possible confusions
        data_user["profile"].reverse()
        data_user["profile"].append([-1, 0])
        data_user["profile"].reverse()
        data_user["profile"].append([self._period*time_step+1, 0])

        j = 0  # the place where you are in the data
        next_point = data_user["profile"][j+1]  # the next point of data that will be encountered

        for line in self._user_profile:  # filling the user profile with priority

            while True:  # the loop is shut down when all the data on the line has been recorded

                next_point_reached = False  # a flag indicating when the next time step is beyond the scope of the "line"
                if next_point[0] < line[0] + time_step:  # when "next_point" is reached, it becomes "previous_point"
                    next_point_reached = True
                    j += 1
                    next_point = data_user["profile"][j + 1]
                    line[1] = data_user["profile"][j][1]

                if next_point[0] > line[0] + time_step or not next_point_reached:
                    break

        # cleaning of the useless entries in the user_profile
        elements_to_keep = []
        for i in range(len(self._user_profile)):
            if self._user_profile[i][1]:  # if the priority is not null
                elements_to_keep.append(self._user_profile[i])
        self._user_profile = elements_to_keep

        # min and max power allowed
        # these power are converted into energy quantities according to the time step
        self._min_power = {element: time_step * data_device["min_power"][element] for element in data_device["min_power"]}  # the minimum power is registered for each nature
        self._max_power = {element: time_step * data_device["max_power"][element] for element in data_device["max_power"]}  # the maximum power is registered for each nature

        # usage_profile
        self._demand = dict()
        self._usage_profile = data_device["usage_profile"]  # creation of an empty usage_profile with all cases ready
        for nature in self.natures:
            self._demand[nature.name] = 0  # the demand is initialized

        self._unused_nature_removal()  # remove unused natures

    def _randomize_start_variation(self, data):
        start_time_variation = self._catalog.get("gaussian")(0, data["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data["profile"]:
            line[0] += start_time_variation

    def _randomize_consumption(self, data):
        consumption_variation = self._catalog.get("gaussian")(1, data["consumption_variation"])  # modification of the consumption
        consumption_variation = max(0, consumption_variation)  # to avoid to shift from consumption to production and vice-versa
        for nature in data["usage_profile"]:
            data["usage_profile"][nature] *= consumption_variation

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        # first we second_update the time remaining until the next need
        if self._remaining_time:  # if we know when will be the next need
            self._remaining_time -= 1
        else:  # if we don't know when it will happen
            self._remaining_time = self._period  # we reinitialize the remaining_time
            for usage in self._user_profile:
                if usage[0] - self._moment > 0:  # if the need occurs during the ongoing period
                    remaining_time = usage[0] - self._moment
                else:  # if the need occurs during the next period
                    remaining_time = usage[0] - self._moment + self._period  # a period is added to know the real time remaining

                if remaining_time < self._remaining_time:
                    self._remaining_time = remaining_time  # the time kept is the shortest
                    for nature in self._usage_profile:
                        self._demand[nature] = usage[1] * self._usage_profile[nature]  # and the quantity associated is kept

        for nature in self._usage_profile:  # creating the demand in energy
            # physical data
            Cp = 4.18 * 10 ** 3  # thermal capacity of water in J.kg-1.K-1
            rho = 1  # density of water in kg.L-1
            hot_water_temperature = 60  # the temperature of the DHW in °C
            wanted_water_temperature = 40  # the final temperature of water in °C
            cold_water_temperature = self._catalog.get(f"{self._location}.cold_water_temperature")  # the temperature of cold water in °C
            # we suppose this temperature will not change until the fulfillment of the need
            month = self._catalog.get("physical_time").month - 1  # as months go from 1 to 12 but the list goes from 0 to 11

            # calculus of volume of hot water
            water_volume = self._demand[nature] * self._month_dependency[month] * \
                           (wanted_water_temperature - cold_water_temperature) / \
                           (   hot_water_temperature - cold_water_temperature)  # the volume of water in L
            # calculated through the proportion of hot water (60°C) necessary to have water at the wanted temperature (40°C)

            # calculus of energy
            energy_to_heat = water_volume * rho * Cp * (hot_water_temperature - cold_water_temperature) / (3.6 * 10 ** 6)  # the energy needed to heat the water, in kWh
            energy_wanted[nature]["energy_minimum"] = 0  # the energy needed to heat the water, in kWh
            energy_wanted[nature]["energy_nominal"] = max(min(energy_to_heat / (self._remaining_time + 1), self._max_power[nature]), 0)  # the energy needed to heat the water, in kWh
            energy_wanted[nature]["energy_maximum"] = max(min(energy_to_heat, self._max_power[nature]), 0)  # the energy needed to heat the water, in kWh

        # if self._remaining_time:  # if the device is active
        #     for nature in energy_wanted:
        #         energy_wanted[nature]["energy_minimum"] = self._min_power[nature]
        #         energy_wanted[nature]["energy_nominal"] = max(self._min_power[nature], min(self._max_power[nature], self._demand[nature] / self._remaining_time))  # the nominal energy demand is the total demand divided by the number of turns left
        #         # but it needs to be between the min and the max value
        #         energy_wanted[nature]["energy_maximum"] = min(self._max_power[nature], self._demand[nature])
        # print(energy_to_heat)

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):  # method updating the device according to the decisions taken by the supervisor
        Device.react(self)  # actions needed for all the devices

        # effort management
        energy_wanted = dict()
        energy_accorded = dict()

        # physical data
        Cp = 4.18 * 10 ** 3  # thermal capacity of water in J.kg-1.K-1
        rho = 1  # density of water in kg.L-1
        hot_water_temperature = 60  # the temperature of the DHW in °C
        wanted_water_temperature = 40  # the final temperature of water in °C
        cold_water_temperature = self._catalog.get(f"{self._location}.cold_water_temperature")  # the temperature of cold water in °C
        # we suppose this temperature will not change until the fulfillment of the need
        month = self._catalog.get("physical_time").month - 1  # as months go from 1 to 12 but the list goes from 0 to 11

        for nature in self._natures:
            energy_wanted[nature] = self.get_energy_wanted_nom(nature)
            energy_accorded[nature] = self.get_energy_accorded_quantity(nature)

            if energy_wanted[nature] > energy_accorded[nature]:  # if it is less than the nominal wanted energy, then it creates effort
                energy_wanted_min = self.get_energy_wanted_min(nature)  # minimum quantity of energy
                energy_wanted_max = self.get_energy_wanted_nom(nature)  # maximum quantity of energy

                effort = min(abs(energy_wanted_min - energy_accorded[nature]), abs(energy_wanted_max - energy_accorded[nature])) / energy_wanted[nature]  # effort increases
                self.agent.add_effort(effort, nature)  # effort increments

            volume_heated = energy_accorded[nature] / (rho * Cp * (hot_water_temperature - cold_water_temperature) / (3.6 * 10 ** 6))

            remaining_demand = volume_heated / ( self._month_dependency[month] *
                           (wanted_water_temperature - cold_water_temperature) /
                           (   hot_water_temperature - cold_water_temperature)  )

            self._demand[nature.name] += - remaining_demand   # the energy in excess or in default


