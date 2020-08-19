# device representing a fuell cell
from src.common.DeviceMainClasses import NonControllableDevice


class FuellCell(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib\Subclasses\Device\Fuell_Cell\Fuel_Cell.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._location = parameters["location"]  # the location of the device, in relation with the meteorological data

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        # power
        self._power = data_device["usage_profile"]["power"]

        # efficiency
        self._electric_efficiency = data_device["usage_profile"]["electric_efficiency"]
        self._thermal_efficiency = data_device["usage_profile"]["thermal_efficiency"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

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








