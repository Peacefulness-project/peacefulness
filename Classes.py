# Declaration of classes


### DECLARATION OF THE ENVIRONMENT
# The environment is the container of all entities.
class World:

    def __init__(self):
        self.CurrentTime = 0  # current time step of the simulation
        self.EntityList = list()

    def add(self, entity):  # method adding entities in the environment
        if type(entity) != list:
            entity = [entity]
        [self.EntityList.append(elmt) for elmt in entity]

    def next(self):  # method incrementing the time step
        self.CurrentTime += 1

    def read(self):  # method extracting data for the current timestep
        pass


### DECLARATION OF ENTITIES
# Root class for all producers/consumers
class Entity:

    def __init__(self):
        self.Nature = ''  # only entities of same nature can interact
        # nature is an integer which corresponds to a predefinite energy vector
        self.Energy = 0  # the quantity of energy the system asks/proposes
        self.MinEnergy = self.Energy  # the minimal energy asked/delivered by the system


# Consumption entities
# They correspond to one engine only (one dishwasher e.g)
class Consumer(Entity):

    def __init__(self):
        Entity.__init__(self)
        self.Priority = 1  # the higher the priority, the higher the chance of being satisfied in the current time step
        self.Interruptibility = 0  # 1 means the system can be switched off while working
        self.Dissatisfaction = 0  # dissatisfaction accounts for the energy not delivered immediately
        # the higher it is, the higher is the chance of being served
        self.MaxEnergy= self.Energy  # the maximal energy the system can sustain
        # params eco, socio, etc


# Production entities
# They correspond to a group of plants of same nature (an eolian park e.g)
# The main grid is considered as a producer
class Producer(Entity):

    def __init__(self):
        Entity.__init__(self)
    #params eco, socio, etc


# Nature entity
# Nature corresponds to the type of energy
# It goes beyond electric/thermal separation and separates electricity of different voltage,...
# ...thermal flux of different temperatures, etc


# Plus tard
# class Storage
# class Converter
