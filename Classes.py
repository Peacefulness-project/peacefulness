# Declaration of classes


### DECLARATION OF THE ENVIRONMENT
# The environment is the container of all entities.
class World:

    def __init__(self):
        self.current_time = 0  # current time step of the simulation
        self.entity_list = list()
        self.temperature = 0 # outdoor temperature in °C

    def add(self, entity):  # method adding entities in the environment
        if type(entity) != list:
            entity = [entity]
        [self.entity_list.append(elmt) for elmt in entity]

    def next(self):  # method incrementing the time step
        self.current_time += 1

    def read(self):  # method extracting data for the current timestep
        pass

    def set_temperature(self, temperature):
        self.temperature = temperature


### DECLARATION OF ENTITIES
# Root class for all producers/consumers
class Entity:

    def __init__(self, nature=''):
        self.nature = nature  # only entities of same nature can interact
        # nature is an integer which corresponds to a predefinite energy vector
        self.energy = 0  # the quantity of energy the system asks/proposes
        self.min_energy = 0  # the minimal energy asked/delivered by the system

    def set_energy(self, quantity):
        self.energy = quantity

    def set_min_energy(self, quantity):
        self.min_energy = quantity


# Consumption entities
# They correspond to one engine only (one dishwasher e.g)

# The main class
class Consumer(Entity):

    def __init__(self, nature='', priority=0, interruptibility=0):
        Entity.__init__(self, nature)
        self.priority = priority  # the higher the priority, the higher the chance of...
                                  #  ...being satisfied in the current time step
        self.interruptibility = interruptibility  # 1 means the system can be switched off while working
        self.dissatisfaction = 0  # dissatisfaction accounts for the energy not delivered immediately
        # the higher it is, the higher is the chance of being served
        self.max_energy = self.energy  # the maximal energy the system can sustain
        # params eco, socio, etc


# The subclasses, which describe more precisely the behavior of different usages


# The "NonSchedulable" class regroups all applications which are non schedulable...
# ... i.e all non-interruptible and always primary for the grid
# It contains lights, TVs, computers, ovens, refrigerators, etc
class NonSchedulable(Consumer):

    def __init__(self, nature=''):
        Consumer.__init__(self, nature, 1, 0)  # always primary, non-interruptible


# The "Heating" subclass regroups heating and cooling devices
class Heating(Consumer):

    def __init__(self, nature='', ):
        Consumer.__init__(self, nature)
        self.objective_temperature = -1  # User-defined temperature in °C
        # Negative temperature means that nothing is required
        self.indoor_temperature = 0  # temperature indoor in °C


# Production entities
# They correspond to a group of plants of same nature (an eolian park e.g)
# The main grid is considered as a producer
class Producer(Entity):

    def __init__(self, nature=''):
        Entity.__init__(self, nature)
    #params eco, socio, etc


# This subclass represents the main grid
# It corresponds to a producer of an infinite capacity
class MainGrid(Producer):

    def __init__(self, nature):
        Producer.__init__(self, nature)
        self.set_energy(mt.inf)


# This subclass corresponds to PV panels
class PV(Producer):

    def __init__(self):
        Producer.__init__(self, 'LVelec')


# This subclass corresponds to wind turbines
class WindTurbine(Producer):
    pass


# Nature entity
# Nature corresponds to the type of energy
# It goes beyond electric/thermal separation and separates electricity of different voltage,...
# ...thermal flux of different temperatures, etc


# Plus tard
# class Storage
# class Converter
