# Declaration of classes


# The environment is the container of all entities.
class World:

    def __init__(self, time_limit):
        self.current_time = 0  # current time step of the simulation
        self.time_limit = time_limit  # latest time step of the simulation
        self.entity_dict = dict()  # a list containing all the actors of the environment
        # self.temperature = 0  # outdoor temperature in °C

    def add(self, new_entities):  # method adding a list of entities in the environment
        # rajouter erreur quand cles identiques
        for entity in new_entities:
            self.entity_dict[entity] = new_entities[entity]

    def next(self):  # method incrementing the time step
        # on mettra les donnees a jour ici
        self.current_time += 1

    def update(self):  # method extracting data for the current timestep
        # tous les calculs de mise à jour devront etre faits la
        for entity in self.entity_dict:
            self.entity_dict[entity].update(self)


# Root class for all elements constituting our environment
class Entity:

    def __init__(self, nature=''):
        self.nature = nature  # only entities of same nature can interact
        self.energy = 0  # the quantity of energy the system asks/proposes
        self.min_energy = 0  # the minimal energy asked/delivered by the system
        self.price = 0  # the price announced by the system

        if nature not in NATURE:  # if it is a new nature of energy
            NATURE.append(nature)  # it is added to the list of different natures of energy

    def update(self, world):
        pass

    def create(cls, n, dict_name, base_of_name, nature):
        pass

    create = classmethod(create)


# Consumer entity
# They correspond to one engine (one dishwasher e.g) with the same profile
class Consumer(Entity):

    def __init__(self, nature='', interruptibility=0):
        Entity.__init__(self, nature)
        self.priority = 0  # the higher the priority, the higher the chance of...
        #  ...being satisfied in the current time step
        self.interruptibility = interruptibility  # 1 means the system can be switched off while working
        self.dissatisfaction = 0  # dissatisfaction accounts for the energy not delivered immediately
        # the higher it is, the higher is the chance of being served
        self.max_energy = self.energy  # the maximal energy the system can sustain
        # params eco, socio, etc

        if type(self) not in CONS:  # if it is a new type of consumer
            CONS.append(type(self))  # it is added to the list

    def update(self, world):
        pass

    def create(cls, n, dict_name, base_of_name, nature):
        Entity.create(n, dict_name, base_of_name, nature)

    create = classmethod(create)


# Production entity
# They correspond to a group of plants of same nature (an eolian park e.g)
# The main grid is considered as a producer
class Producer(Entity):

    def __init__(self, nature=''):
        Entity.__init__(self, nature)
        # params eco, socio, etc

        if type(self) not in PROD:  # if it is a new type of consumer
            PROD.append(type(self))  # it is added to the list

    def update(self, world):
        pass

    def create(cls, n, dict_name, base_of_name, nature):
        Entity.create(n, dict_name, base_of_name, nature)

    create = classmethod(create)


# Plus tard
# class Storage
# class Converter
