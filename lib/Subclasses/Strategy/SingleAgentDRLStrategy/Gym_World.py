# This subclass inherits all the attributes and methods from regular Peacefulness World.
# The difference lies in the "start" method ; to get this interface with GYM to work.
# The simulation loop in "World.start" will be translated to 2 methods, "reseat" and "step".

# Imports
from src.common.World import *


class GymWorld(World):
    def __init__(self, name: str = None):
        super().__init__(name)
        World.ref_world = self

    def register_device(self, device):
        if device.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        # checking if the agent is defined correctly
        if device._agent.name not in self._catalog.agents:  # if the specified agent does not exist
            raise WorldException(f"{device._agent.name} does not exist")

        for element_name, default_value in MessagesManager.added_information.items():  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{device.name}.{element_name}", default_value)

        for nature in device.natures:
            if isinstance(device._natures[nature], dict):
                device._natures[nature]["aggregator"].add_device(device.name)  # adding the device name to its aggregator list of devices
            else:
                for agg in device._natures[nature]:
                    agg["aggregator"].add_device(device.name)

        self._catalog.devices[device.name] = device  # registering the device in the dedicated dictionary
        self._used_names.append(device.name)  # adding the name to the list of used names

    def start(self, verbose=True, exogen_instruction: Callable = None):  # TODO uncomment for rule-based comparison
        pass


