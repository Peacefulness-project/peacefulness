from common.DeviceMainClasses import ChargerDevice


class HotWaterTank(ChargerDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/HotWaterTank.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)