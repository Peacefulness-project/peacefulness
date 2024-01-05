# device representing a fuell cell
from src.common.DeviceMainClasses import Converter


class FuellCell(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregator, profiles, filename="lib\Subclasses\Device\Fuell_Cell\Fuel_Cell.json"):
        super().__init__(name, contracts, agent, filename, upstream_aggregator, downstream_aggregator, profiles)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._energy_physical_limits = {"minimum_energy": 0, "maximum_energy": data_device["capacity"]}

        self._technical_profile = dict()

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        # efficiency
        self._efficiency = {"LVE": data_device["usage_profile"]["electric_efficiency"], "LTH":data_device["usage_profile"]["thermal_efficiency"]}

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        # TODO: mettre à jour la fonction
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        for nature in energy_wanted:
            if nature == "LVE":
                efficiency = self._electric_efficiency
            elif nature == "LTH":
                efficiency = self._thermal_efficiency
            energy_wanted[nature]["energy_minimum"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = 0  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - self._power * efficiency  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog








