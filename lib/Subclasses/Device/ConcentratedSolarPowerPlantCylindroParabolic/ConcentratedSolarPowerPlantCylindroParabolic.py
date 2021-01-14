# A device representing solar thermal collectors
from src.common.DeviceMainClasses import NonControllableDevice
from math import cos, asin, pi, fabs


class ConcentratedSolarPowerPlantCylindroParabolic(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters, filename="lib/Subclasses/Device/ConcentratedSolarPowerPlantCylindroParabolic/ConcentratedSolarPowerPlantCylindroParabolic.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

        self._catalog.add(f"{self.name}_exergy_in", 0)
        self._catalog.add(f"{self.name}_exergy_out", 0)

        irradiation_daemon = self._catalog.daemons[parameters["irradiation_daemon"]]  # the irradiation daemon
        self._irradiation_location = irradiation_daemon.location  # the location of the device, in relation with the meteorological data

        sun_position_daemon = self._catalog.daemons[parameters["sun_position_daemon"]]  # the sun position daemon
        self._sun_position_location = sun_position_daemon.location  # the location of the device, in relation with the meteorological data

        self._surface = parameters["surface"]

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._technical_profile = dict()

        # usage profile
        self._technical_profile[data_device["usage_profile"]["nature"]] = None

        self._reflector_efficiency = data_device["usage_profile"]["reflector_efficiency"]

        self._cycle_efficiency = data_device["usage_profile"]["cycle_efficiency"]

        self._unused_nature_removal()

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        message = {element: self._messages["bottom-up"][element] for element in self._messages["bottom-up"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        irradiation = self._catalog.get(f"{self._irradiation_location}.direct_normal_irradiation_value") / 1000  # the value is divided by 1000 to transfrom w into kW

        azimut = self._catalog.get(f"{self._sun_position_location}.azimut")

        sun_height = self._catalog.get(f"{self._sun_position_location}.sun_height")

        alpha = fabs(asin(cos(azimut * 2 * pi / 360) * cos(sun_height * 2 * pi / 360)) * 360 / (2 * pi))

        optic_efficiency = (cos(alpha) + 0.000884 * alpha - 0.00005369 * alpha**2) * self._reflector_efficiency

        thermal_energy = self._surface * irradiation * optic_efficiency

        energy_received = thermal_energy * self._cycle_efficiency

        for nature in energy_wanted:
            energy_wanted[nature]["energy_minimum"] = - energy_received  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_nominal"] = - energy_received  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_maximum"] = - energy_received  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog



