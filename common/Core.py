# Declaration of core classes
import datetime
from common.Catalog import Catalog
from tools.Utilities import little_separation, middle_separation, big_separation
from common.lib.EnergyTypes import Nature
from common.Agent import Agent
from common.Cluster import Cluster


# ##############################################################################################
# ##############################################################################################
# The environment is the container of all entities.
class World:

    def __init__(self, name=None, catalog=None, subworld=0, timestep_value=3600, time_limit=24):
        if name:
            self._name = name
        else:  # By default, world is named after the date
            self._name = f"Unnamed ({datetime.datetime.now()})"

        if not catalog:  # By default, a catalog is created and named "catalog"
            catalog = Catalog()
        self._catalog = catalog
        # self._catalog.add("world.name", self._name)

        # self._is_subworld = subworld  # a boolean indicating if this world is a subworld
        # # Some tasks are performed only by the main world, like incrementing time

        self._timestep_value = timestep_value    # value of the timestep used during the simulation (in second)
        self._current_time = 0  # current time step of the simulation (in number of iterations)
        self._time_limit = time_limit  # latest time step of the simulation (in number of iterations)
        self._catalog.add("physical_time", 0)  # physical time in seconds, not used for the moment
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        # objects contained by world
        # self._subworlds = dict()  # dict containing the subworlds, not used today
        self._clusters = dict()  # a mono-energy sub-environment which favours self-consumption
        self._agents = dict()  # it represents an economic agent, and is attached to, in particular, a contract

        self._consumers = dict()  # dict containing the consumers
        self._producers = dict()  # dict containing the producers

        self._daemons = dict()  # dict containing the daemons
        self._dataloggers = dict()  # dict containing the dataloggers

        self._used_name = []  # to check name unicity

        self._natures = []  # all energy types of the entities in world, potentially obsolete

        # initialization of a vector nature, which gathers all the keys
        nature = Nature()
        self._catalog.add("Natures", nature.keys)

    # ##########################################################################################
    # Construction
    # ##########################################################################################

    def add(self, entity):  # method adding one entity to the world
        if entity.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{entity.name} already in use")

        if isinstance(entity, Consumption):  # If entity is a consumer...
            self._consumers[entity.name] = entity  # ... it is put in a dedicated dict
        elif isinstance(entity, Production):  # If entity is a producer...
            self._producers[entity.name] = entity  # ... it is put in a dedicated dict
        else:
            raise WorldException(f"Unable to add entity {entity.name}")

        self._used_name.append(entity.name)  # adding the name to the list of used names
        entity._catalog = self._catalog  # linking the catalog to the entity
        entity.register()  # registering of the entity in the catalog

    def register_daemon(self, daemon):  # link a daemon with a world (and its catalog)
        if daemon.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{daemon.name} already in use")

        daemon._catalog = self._catalog   # linking the daemon with the catalog of world
        self._daemons[daemon.name] = daemon  # registering the daemon in the dedicated dictionary
        self._used_name.append(daemon.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        datalogger._catalog = self._catalog   # linking the datalogger with the catalog of world
        self._dataloggers[datalogger.name] = datalogger  # registering the cluster in the dedicated dictionary
        self._used_name.append(datalogger.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def add_cluster(self, cluster):
        if cluster._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{cluster._name} already in use")

        cluster.add_catalog(self._catalog)  # linking the cluster with the catalog of world
        self._clusters[cluster._name] = cluster  # registering the cluster in the dedicated dictionary
        self._used_name.append(cluster._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def add_agent(self, agent):
        if agent._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{agent._name} already in use")

        agent.add_catalog(self._catalog)   # linking the agent with the catalog of world
        self._agents[agent._name] = agent  # registering the agent in the dedicated dictionary
        self._used_name.append(agent._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    # def add_subworld(self, name):  # create a new world ruled by the present world
    #     self._subworlds[name] = World(name, self._catalog, 1, self._timestep_value, self._time_limit)
    #     # The subworld inherits the catalog, the timestep value and the time limit from the "world in chief"

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def next(self):  # method incrementing the time step and calling dataloggers and daemons
        for key in self._dataloggers:  # activation of the dataloggers, they must be called before the daemons,
            # who may have an impact on data
            self._dataloggers[key].launch(self._current_time)

        for key in self._daemons:  # activation of the daemons
            self._daemons[key].launch(self._current_time)

        self._current_time += 1  # updating the simulation time

        physical_time = self._catalog.get("physical_time") + self._timestep_value  # new value of physical time
        self._catalog.set("physical_time", physical_time)  # updating the value of physical time
        self._catalog.set("simulation_time", self._current_time)

        # for subworld in self._subworlds:   # for each subworld, the current time will be increased by one
        #     self._subworlds[subworld].next()

    def update(self):  # method extracting data for the current timestep
        # for key in self._subworlds:  # subworlds are called recursively
        #     self._subworlds[key].update()

        for key in self._consumers:
            self._consumers[key].update()

        for key in self._producers:
            self._producers[key].update()

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def catalog(self):  # shortcut for read-only
        return self._catalog

    def __str__(self):
        return big_separation + f'\nWORLD = {self._name} : {len(self._consumers)} consumers and ' \
            f'{len(self._producers)} producers'


# ##############################################################################################
# ##############################################################################################
# Root class for all elements constituting our environment
class Entity:

    def __init__(self, name, nature):
        self._nature = nature  # only entities of same nature can interact
        self._energy = 0  # the quantity of energy the system asks/proposes
        self._min_energy = 0  # the minimal energy asked/delivered by the system
        self._price = 0  # the price announced by the system

        self._name = name

        self._cluster = None  # the cluster the entity belongs to
        self._agent = None  # the agent represents the owner of the entity

        self._catalog = None  # added later

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def register(self):
        # Add the entity to the catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    def link_cluster(self, cluster):  # link an entity with a cluster
        if self._nature == cluster._nature:
            self._cluster = cluster._name
        else:
            raise EntityException(f"cluster and entity must have the same nature")

    def link_agent(self, agent_name):  # link an entity with an agent
        if f"{agent_name}.{self._nature}" in self._catalog.keys():
            self._agent = agent_name
        else:
            raise EntityException(f"no {self._nature} in {agent_name}")

    def mass_create(cls, n, name, world):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self):
        pass

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    def __str__(self):
        return middle_separation + f"\nEntity {self.name} of type {self.__class__.__name__}"

# ##############################################################################################
# ##############################################################################################
# Consumer entity
# They correspond to one engine (one dishwasher e.g) with the same profile
class Consumption(Entity):

    def __init__(self, name, nature):
        super().__init__(name, nature)

        self._priority = 0  # the higher the priority, the higher the chance of
        # being satisfied in the current time step
        self._interruptibility = 0  # 1 means the system can be switched off while working
        self._dissatisfaction = 0  # dissatisfaction accounts for the energy not delivered immediately
        # the higher it is, the higher is the chance of being served
        self._max_energy = self._energy  # the maximal energy the system can sustain
        # params eco, socio, etc

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def register(self):
        # Add the entity to the catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    def update(self):
        pass

    def mass_create(cls, n, name, world):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

    # ##########################################################################################
    # Utility
    # ##########################################################################################


# ##############################################################################################
# ##############################################################################################
# Production entity
# They correspond to a group of plants of same nature (an eolian park e.g)
# The main grid is considered as a producer
class Production(Entity):

    def __init__(self, name, nature):
        super().__init__(name, nature)

#      if type(self) not in PROD:  # if it is a new type of consumer
#          PROD.append(type(self))  # it is added to the list

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def register(self):
        # Add the entity to the catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    def update(self):
        pass

    def mass_create(cls, n, name, world):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

    # ##########################################################################################
    # Utility
    # ##########################################################################################


# Plus tard
# class Storage
# class Converter


# Exception
class WorldException(Exception):
    def __init__(self, message):
        super().__init__(message)


class EntityException(Exception):
    def __init__(self, message):
        super().__init__(message)
