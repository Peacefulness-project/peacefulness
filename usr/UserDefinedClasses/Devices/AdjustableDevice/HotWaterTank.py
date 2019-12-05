from common.DeviceMainClasses import ChargerDevice
from tools.UserClassesDictionary import user_classes_dictionary


class HotWaterTank(ChargerDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/HotWaterTank.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)

        self._month_dependency = [1.07, 1.06, 1.07, 1.01, 1.01, 0.97, 0.86, 0.78, 0.96, 1.03, 1.08, 1.1]

    def update(self):
        energy_wanted = {nature: {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None}
                       for nature in self._usage_profile}  # consumption which will be asked eventually

        if self._remaining_time == 0:  # checking if the device has to start
            for usage in self._user_profile:
                if usage[0] == self._moment:  # if the current hour matches with the start of an usage
                    self._remaining_time = usage[1] - usage[0]  # incrementing usage duration
                    self._demand = self._usage_profile  # the demand for each nature of energy

        if self._remaining_time:  # if the device is active
            for nature in energy_wanted:
                energy_wanted[nature]["energy_minimum"] = self._min_power[nature]
                energy_wanted[nature]["energy_nominal"] = max(self._min_power[nature], min(self._max_power[nature], self._demand[nature] / self._remaining_time))  # the nominal energy demand is the total demand divided by the number of turns left
                # but it needs to be between the min and the max value
                energy_wanted[nature]["energy_maximum"] = self._max_power[nature]

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog


user_classes_dictionary[f"{HotWaterTank.__name__}"] = HotWaterTank

