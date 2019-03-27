# Declaration of core classes
import datetime
from common.Catalog import Catalog
from tools.Utilities import little_separation, middle_separation, big_separation, adapt_path
from copy import deepcopy
from common.lib.NatureList import NatureList
from common.ExternalGrid import ExternalGrid
from common.LocalGrid import LocalGrid
from common.Agent import Agent
from common.Cluster import Cluster
from common.CaseDirectory import CaseDirectory
from common.TimeManager import TimeManager


# ##############################################################################################
# ##############################################################################################
# The world is the background of a case: it contains and organizes all elements of the code,
# from devices to supervisors.
# First, it contains the catalog the time manager, the case directory and the supervisor, which are all necessary
# Then, it contains dictionaries of elements that describe the studied case, such as devices or agents
# Lastly, it contains a dictionary, of so-called data-loggers, who are in charge of exporting the data into files
class World:

    def __init__(self, name=None):
        if name:
            self._name = name
        else:  # By default, world is named after the date
            self._name = f"Unnamed ({datetime.datetime.now()})"

        self._catalog = None  # data catalog which gathers all data

        self._case_directory = None  # object which manages the result directory

        self._natures = None  # object which lists the nature present in world

        self.supervisor = None  # object which performs the calculus

        self._time_manager = None  # object which manages time
        
        # dictionaries contained by world
        self._local_grid = dict()  # grids interns to world
        self._external_grid = dict()  # grids external to world

        self._agents = dict()  # it represents an economic agent, and is attached to, in particular, a contract
        self._clusters = dict()  # a mono-energy sub-environment which favours self-consumption

        self._consumptions = dict()  # dict containing the consumptions
        self._productions = dict()  # dict containing the productions

        self._daemons = dict()  # dict containing the daemons
        self._dataloggers = dict()  # dict containing the dataloggers

        self._used_name = []  # this list contains the catalog name of all elements
        # It avoids to erase inadvertently pre-defined elements

    # ##########################################################################################
    # Construction
    # methods are arranged in the order they are supposed to be used
    # ##########################################################################################

    def set_catalog(self, catalog):  # definition of a catalog
        self._catalog = catalog

    def set_directory(self, case_directory):  # definition of a case directory and creation of the directory
        self._case_directory = case_directory
        self._case_directory._add_catalog(self._catalog)  # linking the case_directory with the catalog of world
        case_directory.create()  # create the directory and publish its path in the catalog

    def set_natures(self, nature):  # definition of natures dictionary
        self._natures = nature
        self._catalog.add("Natures", nature.keys)

    def set_supervisor(self, supervisor):  # definition of the supervisor
        self.supervisor = supervisor

    def set_time_manager(self, time_manager):  # definition of a time manager
        self._time_manager = time_manager
        self._time_manager._add_catalog(self._catalog)  # linking the time_manager with the catalog of world

    def register_local_grid(self, local_grid):
        if local_grid._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{local_grid._name} already in use")

        local_grid._add_catalog(self._catalog)  # linking the local grid with the catalog of world
        self._local_grid[local_grid._name] = local_grid  # registering the local grid in the dedicated dictionary
        self._used_name.append(local_grid._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_external_grid(self, external_grid):
        if external_grid._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{external_grid._name} already in use")
        
        # checking if the grid is defined correctly
        if external_grid._grid not in self._local_grid:  # if the specified grid does not exist
            raise DeviceException(f"{external_grid._grid} does not exist")
        elif external_grid.nature != self._local_grid[external_grid._grid]._nature:  # if the natures are not the sames
            raise DeviceException(f"{external_grid._grid} is {self._local_grid[external_grid._grid]._nature}, not {external_grid.nature}")

        external_grid._add_catalog(self._catalog)  # linking the external grid with the catalog of world
        self._external_grid[external_grid._name] = external_grid  # registering the external grid in the dedicated
        # dictionary
        self._used_name.append(external_grid._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_agent(self, agent):  # links the device with an agent
        if agent._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{agent._name} already in use")

        agent._add_catalog(self._catalog)   # linking the agent with the catalog of world
        self._agents[agent._name] = agent  # registering the agent in the dedicated dictionary
        self._used_name.append(agent._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_cluster(self, cluster):  # links the device with a cluster
        if cluster._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{cluster._name} already in use")

        # checking if the grid is defined correctly
        if cluster._grid not in self._local_grid:  # if the specified grid does not exist
            raise DeviceException(f"{cluster._grid} does not exist")
        elif cluster.nature != self._local_grid[cluster._grid]._nature:  # if the natures are not the sames
            raise DeviceException(f"{cluster._grid} is {self._local_grid[cluster._grid]._nature}, not {cluster.nature}")
        
        cluster._add_catalog(self._catalog)  # linking the cluster with the catalog of world
        self._clusters[cluster._name] = cluster  # registering the cluster in the dedicated dictionary
        self._used_name.append(cluster._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_device(self, device):  # method adding one device to the world
        if device.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        # checking if the grid is defined correctly
        if device._grid not in self._local_grid:  # if the specified grid does not exist
            raise DeviceException(f"{device._grid} does not exist")
        elif device.nature != self._local_grid[device._grid]._nature:  # if the natures are not the sames
            raise DeviceException(f"{device._grid} is {self._local_grid[device._grid]._nature}, not {device.nature}")

        # checking if the agent is defined correctly
        if device._agent not in self._agents:  # if the specified agent does not exist
            raise DeviceException(f"{device._agent} does not exist")
        elif f"{device._agent}.{device._nature}" not in self._catalog.keys:  # if the agent does not include the
            # nature of the device
            raise DeviceException(f"{device._agent} has no contracts for nature {device.nature}")

        # checking if the cluster is defined correctly
        if device._cluster is not None:
            if device._cluster not in self._clusters:  # if the specified cluster does not exist
                raise DeviceException(f"{device._cluster} does not exist")
            elif device.nature != self._clusters[device._cluster]._nature:  # if the natures are not the sames
                raise DeviceException(f"{device._cluster} is {self._clusters[device._cluster]._nature}, "
                                      f"not {device.nature}")

        if isinstance(device, Consumption):  # If device is a consumer...
            self._consumptions[device.name] = device  # ... it is put in a dedicated dict
        elif isinstance(device, Production):  # If device is a producer...
            self._productions[device.name] = device  # ... it is put in a dedicated dict
        else:
            raise WorldException(f"Unable to add device {device.name}")

        self._used_name.append(device.name)  # adding the name to the list of used names
        device._catalog = self._catalog  # linking the catalog to the device
        device._register()  # registering of the device in the catalog

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        datalogger._add_catalog(self._catalog)   # linking the datalogger with the catalog of world
        self._dataloggers[datalogger.name] = datalogger  # registering the cluster in the dedicated dictionary
        self._used_name.append(datalogger.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_daemon(self, daemon):  # link a daemon with a world (and its catalog)
        if daemon.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{daemon.name} already in use")

        daemon._catalog = self._catalog   # linking the daemon with the catalog of world
        self._daemons[daemon.name] = daemon  # registering the daemon in the dedicated dictionary
        self._used_name.append(daemon.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _check(self):  # a method checking if the world has been well defined
        # 4 things are necessary for world to be correctly defined:
        # the time manager, the case directory, the nature list and the supervisor

        # first, we check the 4 necessary objects:
        # checking if a time manager is defined
        if self._time_manager is None:
            raise WorldException(f"A time manager is needed")

        # checking if a case directory is defined
        if self._case_directory is None:
            raise WorldException(f"A case directory is needed")

        # checking if a nature list is defined
        if self._natures is None:
            raise WorldException(f"A nature list is needed")

        # checking if a supervisor is defined
        if self.supervisor is None:
            raise WorldException(f"A supervisor is needed")

    def start(self):

        self._check()  # check if everything is fine in world definition

        world = self
        catalog = self._catalog

        path = adapt_path(["usr", "supervisors", self.supervisor._filename])

        exec(open(path).read())

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def catalog(self):  # shortcut for read-only
        return self._catalog

    @property
    def time_limit(self):  # shortcut for read-only
        return self._time_manager._time_limit

    @property
    def natures(self):  # shortcut for read-only
        return self._natures.keys

    def __str__(self):
        return big_separation + f'\nWORLD = {self._name} : {len(self._consumptions)} consumers and ' \
            f'{len(self._productions)} producers'

    def duplicate(cls, old_world, new_world_name):  # not functional yet
        new_world = deepcopy(old_world)
        new_world._name = new_world_name
        return new_world

    duplicate = classmethod(duplicate)


# ##############################################################################################
# ##############################################################################################
# Root class for all devices constituting a case
class Device:

    def __init__(self, name, nature, grid_name, agent_name, cluster_name=None):
        self._nature = nature  # only entities of same nature can interact

        self._name = name  # the name which serve as root in the catalog entries

        self._grid = grid_name  # the grid the device belongs to
        self._cluster = cluster_name  # the cluster the device belongs to
        self._agent = agent_name  # the agent represents the owner of the device

        self._catalog = None  # added later

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register_device(self):  # make the initialization operations undoable without a catalog
        # and relevant for all devices
        self._catalog.add(f"{self._name}.energy", 0)  # write directly in the catalog the energy
        self._catalog.add(f"{self._name}.min_energy", 0)  # write directly in the catalog the minimum energy
        self._catalog.add(f"{self._name}.price", 0)  # write directly in the catalog the price

    def _register(self):  # make the initialization operations undoable without a catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _update(self):  # method updating data to the current timestep
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, grid_name, agent_name, cluster_name=None):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def nature(self):  # shortcut for read-only
        return self._nature

    def __str__(self):
        return middle_separation + f"\nDevice {self.name} of type {self.__class__.__name__}"


# ##############################################################################################
# ##############################################################################################
# Consumer device
# They correspond to one engine (one dishwasher e.g)
class Consumption(Device):

    def __init__(self, name, nature, grid_name, agent_name, cluster_name=None):
        super().__init__(name, nature, grid_name, agent_name, cluster_name)

        self._interruptibility = 0  # 1 means the system can be switched off while working
        # params eco, socio, etc

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register_consumption(self):  # make the initialization operations undoable without a catalog and
        # relevant for class consumption
        self._register_device()  # make the operations relevant for all kind of entities

        self._catalog.add(f"{self._name}.priority", 1)  # the higher the priority, the higher the chance of
        # being satisfied in the current time step

    def _register(self):  # make the initialization operations undoable without a catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, grid_name, agent_name, cluster_name=None):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _update(self):  # method updating data to the current timestep
        pass

    # ##########################################################################################
    # Utility
    # ##########################################################################################


# ##############################################################################################
# ##############################################################################################
# Production device
# They correspond to a group of plants of same nature (an eolian park e.g)
class Production(Device):

    def __init__(self, name, nature, grid_name, agent_name, cluster_name=None):
        super().__init__(name, nature, grid_name, agent_name, cluster_name)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register_production(self):  # make the initialization operations undoable without a catalog and
        # relevant for class production
        self._register_device()  # make the operations relevant for all kind of entities

    def _register(self):  # make the initialization operations undoable without a catalog
        pass

    def init(self):
        # Add published data to the catalog
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, grid_name, agent_name, cluster_name=None):
        # a class method allowing to create several instance of a same class
        pass

    mass_create = classmethod(mass_create)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def _update(self):  # method updating data to the current timestep
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


class DeviceException(Exception):
    def __init__(self, message):
        super().__init__(message)
