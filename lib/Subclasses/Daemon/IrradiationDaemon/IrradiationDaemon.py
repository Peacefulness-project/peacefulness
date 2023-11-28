# this daemon is designed to manage the price of a given energy for sellers or buyers
from lib.Subclasses.Daemon.DataReadingDaemon.DataReadingDaemon import DataReadingDaemon


class IrradiationDaemon(DataReadingDaemon):
    def __init__(self, parameters, period=1, filename="lib/Subclasses/Daemon/IrradiationDaemon/IrradiationProfiles.json", direct_normal_irradiation: bool = True):
        name = "solar_irradiation_in_"
        super().__init__(name, period, parameters, filename)

        if direct_normal_irradiation:
            self._managed_keys = [("total_irradiation", f"{self._location}.total_irradiation_value", "extensive"),
                                  ("direct_normal_irradiation", f"{self._location}.direct_normal_irradiation_value", "extensive"),
                                  ]
        else:
            self._managed_keys = [("total_irradiation", f"{self._location}.total_irradiation_value", "extensive")]

        self._initialize_managed_keys()

