from common.DeviceMainClasses import AdjustableDevice


class Heating(AdjustableDevice):

    def __init__(self, name,  agent_name, clusters, user_type, consumption_device, filename="usr/Datafiles/Heating.json"):
        super().__init__(name, agent_name, clusters, filename, user_type, consumption_device)


