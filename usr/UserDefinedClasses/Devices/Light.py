from common.DeviceMainClasses import NonControllableDevice


class Light(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, filename="usr/DevicesProfiles/Light.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device)


