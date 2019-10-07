from common.DeviceMainClasses import NonControllableDevice


class VacuumCleaner(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/VacuumCleaner.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)