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

    def __init__(self, name=None, catalog=None, timestep_value=3600, time_limit=24):
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

        self._timestep_value = timestep_value  # value of the timestep used during the simulation (in second)
        self._time_limit = time_limit  # latest time step of the simulation (in number of iterations)
        self._catalog.add("physical_time", 0)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        # objects contained by world
        # self._subworlds = dict()  # dict containing the subworlds, not used today
        self._clusters = dict()  # a mono-energy sub-environment which favours self-consumption
        self._agents = dict()  # it represents an economic agent, and is attached to, in particular, a contract

        self._consumptions = dict()  # dict containing the consumers
        self._productions = dict()  # dict containing the producers

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
            self._consumptions[entity.name] = entity  # ... it is put in a dedicated dict
        elif isinstance(entity, Production):  # If entity is a producer...
            self._productions[entity.name] = entity  # ... it is put in a dedicated dict
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

    def add_cluster(self, cluster):  # links the entity with a cluster
        if cluster._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{cluster._name} already in use")

        cluster.add_catalog(self._catalog)  # linking the cluster with the catalog of world
        self._clusters[cluster._name] = cluster  # registering the cluster in the dedicated dictionary
        self._used_name.append(cluster._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def add_agent(self, agent):  # links the entity with an agent
        if agent._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{agent._name} already in use")

        agent.add_catalog(self._catalog)   # linking the agent with the catalog of world
        self._agents[agent._name] = agent  # registering the agent in the dedicated dictionary
        self._used_name.append(agent._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def link_cluster(self, cluster, entity_list):  # link an entity with a cluster
        if isinstance(entity_list, str):  # if entity is not a list
            entity_list = [entity_list]  # it is transformed into a list
            # This operation allows to pass list of entities or single entities

        for key in entity_list:
            if key in self._consumptions:
                entity = self._consumptions[key]
            elif key in self._productions:
                entity = self._productions[key]
            else:
                raise WorldException(f"{key} is not an entity")

            if entity._nature == self._clusters[cluster]._nature:
                entity._cluster = cluster
            else:
                raise EntityException(f"cluster and entity must have the same nature")

    def link_agent(self, agent, entity_list):  # link an entity with an agent
        if isinstance(entity_list, str):  # if entity is not a list
            entity_list = [entity_list]  # it is transformed into a list
            # This operation allows to pass list of entities or single entities

        for key in entity_list:
            if key in self._consumptions:
                entity = self._consumptions[key]
            elif key in self._productions:
                entity = self._productions[key]
            else:
                raise WorldException(f"{key} is not an entity")

            if f"{agent}.{entity._nature}" in self._catalog.keys:
                entity._agent = agent
            else:
                raise EntityException(f"no {entity._nature} in {agent}")

    # def add_subworld(self, name):  # create a new world ruled by the present world
    #     self._subworlds[name] = World(name, self._catalog, 1, self._timestep_value, self._time_limit)
    #     # The subworld inherits the catalog, the timestep value and the time limit from the "world in chief"

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def check(self):  # a method checking if the world has been well defined

        problem = False

        # checking if each entity has an agent
        for consumption in self._consumptions:
            consumption = self._consumptions[consumption]
            if consumption._agent is None:
                print(f"    /!\\ consumption {consumption._name} has no agent")
                problem = True
        
        for production in self._productions:
            production = self._productions[production]
            if production._agent is None:
                print(f"    /!\\ production {production._name} has no agent")
                problem = True
        
        if problem:
            raise WorldException("All entities must have an agent")

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def next(self):  # method incrementing the time step and calling dataloggers and daemons
        # it is called after the resolution of the round

        current_time = self._catalog.get("simulation_time")

        for key in self._dataloggers:  # activation of the dataloggers, they must be called before the daemons,
            # who may have an impact on data
            self._dataloggers[key].launch()

        for key in self._daemons:  # activation of the daemons
            self._daemons[key].launch()

        physical_time = self._catalog.get("physical_time") + self._timestep_value  # new value of physical time
        self._catalog.set("physical_time", physical_time)  # updating the value of physical time
        self._catalog.set("simulation_time", current_time + 1)

        # for subworld in self._subworlds:   # for each subworld, the current time will be increased by one
        #     self._subworlds[subworld].next()

    def update(self):  # method updating data to the current timestep
        # for key in self._subworlds:  # subworlds are called recursively
        #     self._subworlds[key].update()

        for key in self._consumptions:
            self._consumptions[key].update()

        for key in self._productions:
            self._productions[key].update()

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def catalog(self):  # shortcut for read-only
        return self._catalog

    def __str__(self):
        return big_separation + f'\nWORLD = {self._name} : {len(self._consumptions)} consumers and ' \
            f'{len(self._productions)} producers'


# ##############################################################################################
# ##############################################################################################
# Root class for all elements constituting our environment
class Entity:

    def __init__(self, name, nature):
        self._nature = nature  # only entities of same nature can interact

        self._name = name  # the name which serve as root in the catalog entries

        self._cluster = None  # the cluster the entity belongs to
        self._agent = None  # the agent represents the owner of the entity

        self._catalog = None  # added later

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def register_entity(self):  # make the initialization operations undoable without a catalog
        self._catalog.add(f"{self._name}.energy", 0)  # writes directly in the catalog the energy
        self._catalog.add(f"{self._name}.min_energy", 0)  # writes directly in the catalog the minimum energy
        self._catalog.add(f"{self._name}.price", 0)  # writes directly in the catalog the price

    def register(self):  # make the initialization operations undoable without a catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self):  # method updating data to the current timestep
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

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

        self._interruptibility = 0  # 1 means the system can be switched off while working
        # params eco, socio, etc

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def register_consumption(self):  # make the initialization operations undoable without a catalog and
        # relevant for class consumption
        self.register_entity()  # make the operations relevant for all kind of entities

        self._catalog.add(f"{self._name}.priority", 1)  # the higher the priority, the higher the chance of
        # being satisfied in the current time step

    def register(self):  # make the initialization operations undoable without a catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self):  # method updating data to the current timestep
        pass

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
    # Initialization
    # ##########################################################################################

    def register_production(self):  # make the initialization operations undoable without a catalog and
        # relevant for class production
        self.register_entity()  # make the operations relevant for all kind of entities

    def register(self):  # make the initialization operations undoable without a catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def update(self):  # method updating data to the current timestep
        pass

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
