# This subclass inherits all the attributes and methods from regular Peacefulness World.
# The difference lies in the "start" method ; to get this interface with GYM to work.
# The simulation loop in "World.start" will be translated to 2 methods, "reseat" and "step".

# Imports
from src.common.World import *


class GymWorld(World):
    def __init__(self, name: str = None):
        super().__init__(name)
        World.ref_world = self

    def start(self, verbose=True, exogen_instruction: Callable = None):
        pass


