# This device represents all the devices that are not explicitly described otherwise because one or several of the following reasons:
# - they are rare;
# - they don't consume a lot of energy nor they have an important power demand;
# - patterns of use or of consumption are difficult to model;
# - they are non-controllable, i.e the supervisor has no possibility to interact with them.

from common.DeviceMainClasses import NonControllableDevice
from tools.UserClassesDictionary import user_classes_dictionary


class Background(NonControllableDevice):

    def __init__(self, name, contracts, agent, clusters, user_type, consumption_device, parameters=None, filename="usr/DevicesProfiles/Background.json"):
        super().__init__(name, contracts, agent, clusters, filename, user_type, consumption_device, parameters)


user_classes_dictionary[f"{Background.__name__}"] = Background


