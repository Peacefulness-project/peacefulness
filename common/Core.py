# Declaration of classes
import datetime
from common.Catalog import Catalog


# The environment is the container of all entities.
class World:

    def __init__(self, name=None, catalog = None):
        if name:
            self._name= name
        else:
            self._name = f"Unnamed ({datetime.datetime.now()})"

        if not catalog:
            catalog = Catalog() # create if none
        self._catalog = catalog
        self._catalog.add("wolrd.name", self._name)
        self._catalog.add("time",0)


        self.current_time = 0  # current time step of the simulation
        self.time_limit = 0  # latest time step of the simulation

        self._consumers = dict()  # a list containing all the actors of the environment
        self._producers = dict()  # a list containing all the actors of the environment

        self._used_name = []    # to check name unicity


    # ##########################################################################################
    # Entity management
    # ##########################################################################################

    def add(self, entity):  # method adding a list of entities in the environment
        if entity.name in self._used_name:
            raise WorldException(f"{entity.name} already in use")

        if isinstance(entity, Consumer):
            self._consumers[entity.name] = entity
        elif isinstance(entity, Producer):
            self._producers[entity.name] = entity
        else:
            raise WorldException(f"Unable to add entity {entity.name}")

        self._used_name.append(entity.name)
        entity.register(self.catalog)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def next(self):  # method incrementing the time step
        # on mettra les donnees a jour ici
        self.current_time += 1

    def update(self):  # method extracting data for the current timestep
        # tous les calculs de mise à jour devront etre faits la
        for entity in self.entity_dict:
            self.entity_dict[entity].update(self)


    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def catalog(self):
        return self._catalog

    def __str__(self):
        return f'WORLD = {self._name} : {len(self._consumers)} consumers and {len(self._producers)} producers'


# Root class for all elements constituting our environment
class Entity:

    def __init__(self, name, nature=''):
        self.nature = nature  # only entities of same nature can interact
        self.energy = 0  # the quantity of energy the system asks/proposes
        self.min_energy = 0  # the minimal energy asked/delivered by the system
        self.price = 0  # the price announced by the system

        self._name = name

#        if nature not in NATURE:  # if it is a new nature of energy
#            NATURE.append(nature)  # it is added to the list of different natures of energy

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################


    def register(self,catalog):
        ''' Add published data to the catalog
        '''
        pass

    def update(self, world):
        pass

#    def create(cls, n, dict_name, base_of_name, nature):
#        pass

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):
        return self._name

    def __str__(self):
        return f"Entity {self.name} of type {self.__class__.__name__}"



# Consumer entity
# They correspond to one engine (one dishwasher e.g) with the same profile
class Consumer(Entity):

    def __init__(self, name):
        super().__init__(name)

        self.priority = 0  # the higher the priority, the higher the chance of...

        #  ...being satisfied in the current time step
        self.interruptibility = 0  # 1 means the system can be switched off while working
        self.dissatisfaction = 0  # dissatisfaction accounts for the energy not delivered immediately
        # the higher it is, the higher is the chance of being served
        self.max_energy = self.energy  # the maximal energy the system can sustain
        # params eco, socio, etc

#        if type(self) not in CONS:  # if it is a new type of consumer
 #           CONS.append(type(self))  # it is added to the list

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self, world):
        pass

    # ##########################################################################################
    # Utility
    # ##########################################################################################


#    def create(cls, n, dict_name, base_of_name, nature):
#        Entity.create(n, dict_name, base_of_name, nature)

#    create = classmethod(create)


# Production entity
# They correspond to a group of plants of same nature (an eolian park e.g)
# The main grname is consnameered as a producer
class Producer(Entity):

    def __init__(self, name):
        super().__init__(name)
        # params eco, socio, etc

  #      if type(self) not in PROD:  # if it is a new type of consumer
  #          PROD.append(type(self))  # it is added to the list

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self, world):
        pass

    # ##########################################################################################
    # Utility
    # ##########################################################################################


#    def create(cls, n, dict_name, base_of_name, nature):
 #       Entity.create(n, dict_name, base_of_name, nature)

  #  create = classmethod(create)


# Plus tard
# class Storage
# class Converter


# Exception
class WorldException(Exception):
    def __init__(self, message):
        super().__init__(message)