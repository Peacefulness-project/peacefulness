# This class represents devices whose main activity is to heat water, like coffee makers or kettles.

from common.DeviceMainClasses import ShiftableDevice


class WaterHeater(ShiftableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/WaterHeater.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)


