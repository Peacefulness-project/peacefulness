from common.DeviceMainClasses import AdjustableDevice


class Refrigerator(AdjustableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/Refrigerator.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)