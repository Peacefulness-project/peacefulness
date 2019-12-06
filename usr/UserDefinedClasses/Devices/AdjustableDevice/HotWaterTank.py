from common.DeviceMainClasses import ChargerDevice
from tools.UserClassesDictionary import user_classes_dictionary


class HotWaterTank(ChargerDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/HotWaterTank.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)

        self._month_dependency = [1.07, 1.06, 1.07, 1.01, 1.01, 0.97, 0.86, 0.78, 0.96, 1.03, 1.08, 1.1]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):  # make the initialization operations specific to the device
        pass

    def _get_consumption(self):

        [data_user, data_device] = self._read_consumption_data()  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._offset_management()  # implementation of the offset

        # we randomize a bit in order to represent reality better
        start_time_variation = self._catalog.get("gaussian")(0, data_user["start_time_variation"])  # creation of a displacement in the user_profile
        for line in data_user["profile"]:
            line[0] += start_time_variation
            line[1] += start_time_variation

        consumption_variation = self._catalog.get("gaussian")(1, data_device["consumption_variation"])  # modification of the consumption
        for nature in data_device["usage_profile"].values():
            nature *= consumption_variation

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        for i in range(len(data_user["profile"])):
            self._user_profile.append([])
            for proportion in data_user["profile"][i]:
                self._user_profile[-1].append(proportion)  # adding the proportion of energy needed for this usage comprared tot the total value consumed during the period

        # min and max power allowed
        # these power are converted into energy quantities according to the time step
        self._min_power = {element: time_step * data_device["min_power"][element] for element in data_device["min_power"]}  # the minimum power is registered for each nature
        self._max_power = {element: time_step * data_device["max_power"][element] for element in data_device["max_power"]}  # the maximum power is registered for each nature

        # usage_profile
        self._usage_profile = data_device["usage_profile"]  # creation of an empty usage_profile with all cases ready
        self._demand = self._usage_profile  # if the simulation begins during an usage, the demand has to be initialized

        self._unused_nature_removal()  # remove unused natures

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                       for nature in self._usage_profile}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # checking if the device has to start
            # print(self._moment)

            for usage in self._user_profile:
                # print(usage[0])
                if usage[0] == self._moment:  # if the current hour matches with the start of an usage
                    self._remaining_time = 1  # incrementing usage duration

                    # print(self._catalog.get("physical_time"))
                    # print(usage)

                    for nature in self._usage_profile:  # creating the demand in energy
                        # physical data
                        Cp = 4.18 * 10 ** 3  # thermal capacity of water in J.kg-1.K-1
                        rho = 1  # density of water in kg.L-1
                        hot_water_temperature = 60  # the temperature of the DHW in °C
                        wanted_water_temperature = 40  # the final temperature of water in °C
                        cold_water_temperature = self._catalog.get("cold_water_temperature")  # the temperature of cold water in °C
                        # we suppose this temperature will not change until the fulfillment of the need
                        month = self._catalog.get("physical_time").month

                        # calculus of volume of hot water
                        water_volume = self._usage_profile[nature] * usage[1] * self._month_dependency[month] * \
                                       (wanted_water_temperature - cold_water_temperature) / \
                                       (   hot_water_temperature - cold_water_temperature)  # the volume of water in L
                        # calculated through the proportion of hot water (60°C) necessary to have water at the wanted temperature (40°C)

                        # calculus of energy
                        energy_to_heat = water_volume * rho * Cp * (hot_water_temperature - cold_water_temperature)  # the energy needed to heat the water, in J
                        self._demand[nature] = energy_to_heat / (3.6 * 10 ** 6)  # the energy needed to heat the water, in kWh

        if self._remaining_time:  # if the device is active
            for nature in energy_wanted:
                # print(self._catalog.get("physical_time"))
                # print(self._demand)
                energy_wanted[nature]["energy_minimum"] = self._min_power[nature]
                energy_wanted[nature]["energy_nominal"] = max(self._min_power[nature], min(self._max_power[nature], self._demand[nature] / self._remaining_time))  # the nominal energy demand is the total demand divided by the number of turns left
                # but it needs to be between the min and the max value
                energy_wanted[nature]["energy_maximum"] = min(self._max_power[nature], self._demand[nature])

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


user_classes_dictionary[f"{HotWaterTank.__name__}"] = HotWaterTank

