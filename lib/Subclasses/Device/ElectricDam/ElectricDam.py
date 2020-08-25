# device representing an electric dams
from src.common.DeviceMainClasses import NonControllableDevice


class ElectricDam(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/ElectricDam/ElectricDam.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._height = parameters["height"]
        self._location = parameters["water_flow_daemon"].location  # the location of the device, in relation with the meteorological data

        # creation of keys for exergy
        self._catalog.add(f"{self.name}_exergy_in", 0)
        self._catalog.add(f"{self.name}_exergy_out", 0)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        # efficiency
        self._max_efficiency = data_device["usage_profile"]["max_efficiency"]

        # max power
        self._max_power = data_device["usage_profile"]["max_power"]

        # relative flow
        self._relative_flow = data_device["usage_profile"]["efficiency"]["relative_flow"]

        # relative efficiency
        self._relative_efficiency = data_device["usage_profile"]["efficiency"]["relative_efficiency"]

        self._relative_min_flow = data_device["usage_profile"]["relative_min_flow"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        reserved_flow = self._catalog.get(f"{self._location}.reserved_flow")
        flow = self._catalog.get(f"{self._location}.flow_value") * (1 - reserved_flow)
        max_flow = self._catalog.get(f"{self._location}.max_flow") * (1 - reserved_flow)

        coeff_efficiency = 0

        for i in range(len(self._relative_flow)):
            if (flow / max_flow > self._relative_flow[i]) and (flow / max_flow < self._relative_flow[i+1]):
                coeff_efficiency = self._relative_efficiency(i)

        water_density = 1000
        efficiency = self._max_efficiency * coeff_efficiency

        if flow > self._relative_min_flow * max_flow:
            energy_received = water_density * 9.81 * flow * self._height / 1000  # as irradiation is in W, it is transformed in kW
        else:
            energy_received = 0

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = - min(self._max_power, energy_received * efficiency) # energy produced by the device
            energy_wanted[nature]["energy_nominal"] = - min(self._max_power, energy_received * efficiency)  # energy produced by the device
            energy_wanted[nature]["energy_maximum"] = - min(self._max_power, energy_received * efficiency)  # energy produced by the device
            # the value is negative because it is produced

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog








