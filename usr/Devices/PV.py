from common.DeviceMainClasses import NonControllableDevice
from math import sin, pi


class PV(NonControllableDevice):

    def __init__(self, name,  agent_name, clusters, user_type, consumption_device, filename="usr/Datafiles/PV.json"):
        super().__init__(name, agent_name, clusters, filename, user_type, consumption_device)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _user_register(self):
        for line in self._user_profile:
            solar_prod = sin((line[0] - 8.5) * pi / 9) * line[1]
            line[1] = max(0, solar_prod)





