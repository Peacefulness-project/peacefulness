from common.DeviceMainClasses import ShiftableDevice


class Dishwasher(ShiftableDevice):

    def __init__(self, name,  agent_name, clusters, user_type, consumption_device, filename = "usr/DevicesProfiles/Dishwasher.json"):
        super().__init__(name, agent_name, clusters, filename, user_type, consumption_device)


