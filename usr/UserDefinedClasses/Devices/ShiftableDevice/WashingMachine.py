from common.DeviceMainClasses import ShiftableDevice


class WashingMachine(ShiftableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/WashingMachine.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)