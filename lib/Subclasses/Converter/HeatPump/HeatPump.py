from src.common.Converter import Converter


class Heatpump(Converter):

    def __init__(self, name, contract, agent, clusters, user_profile_name, usage_profile_name, parameters=None):
        super().__init__(name, contract, agent, clusters, "lib/Subclasses/Converter/HeatPump/HeatPump.json", user_profile_name, usage_profile_name, parameters)


