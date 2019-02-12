# Declaration of core classes
import datetime
from common.Catalog import Catalog
from tools.Utilities import little_separation, middle_separation, big_separation


# The environment is the container of all entities.
class World:

    def __init__(self, name=None, catalog=None):
        if name:
            self._name = name
        else:  # By default, world is named after the date
            self._name = f"Unnamed ({datetime.datetime.now()})"

        if not catalog:  # By default, a catalog is created and named "catalog"
            catalog = Catalog()
        self._catalog = catalog
        # at least, the catalog contains the name of the world and the current time step
        self._catalog.add("world.name", self._name)
        self._catalog.add("time", 0)

        self.current_time = 0  # current time step of the simulation
        self.time_limit = 0  # latest time step of the simulation

        self._consumers = dict()  # dict containing the consumers
        self._producers = dict()  # dict containing the producers

        self._used_name = []  # to check name unicity

    # ##########################################################################################
    # Entity management
    # ##########################################################################################

    def add(self, entity):  # method adding one entity to the world
        if entity.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{entity.name} already in use")

        if isinstance(entity, Consumer):  # If entity is a consumer...
            self._consumers[entity.name] = entity  # ... it is put in a dedicated dict
        elif isinstance(entity, Producer):  # If entity is a producer...
            self._producers[entity.name] = entity  # ... it is put in a dedicated dict
        else:
            raise WorldException(f"Unable to add entity {entity.name}")

        self._used_name.append(entity.name)  # adding the name to the list of used names
        entity.register(self.catalog)  # registering of the entity in the catalog

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def next(self):  # method incrementing the time step
        self.current_time += 1

    def update(self):  # method extracting data for the current timestep
        pass
        # for entity in self.entity_dict:
        #     self.entity_dict[entity].update(self)

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def catalog(self):
        return self._catalog

    def __str__(self):
        return big_separation + f'\nWORLD = {self._name} : {len(self._consumers)} consumers and ' \
            f'{len(self._producers)} producers'


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

    def register(self, catalog):
        # Add published data to the catalog
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
        return middle_separation + f"\nEntity {self.name} of type {self.__class__.__name__}"


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
# The main grid is considered as a producer
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

#    create = classmethod(create)


# Plus tard
# class Storage
# class Converter


# Exception
class WorldException(Exception):
    def __init__(self, message):
        super().__init__(message)
