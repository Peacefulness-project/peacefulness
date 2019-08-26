from common.DeviceMainClasses import NonControllableDevice


class Light(NonControllableDevice):

    def __init__(self, name,  agent_name, clusters, user_type, consumption_device, filename="usr/Datafiles/Light.json"):
        super().__init__(name, agent_name, clusters, filename, user_type, consumption_device)


