# Declaration of core classes
# ##############################################################################################
# Native packages
import datetime
import os
from copy import deepcopy
# Current packages
from common.Catalog import Catalog
from common.lib.NatureList import NatureList
from common.LocalGrid import LocalGrid
from common.ExternalGrid import ExternalGrid
from common.Agent import Agent
from common.Cluster import Cluster
from common.Datalogger import Datalogger
from common.Daemon import Daemon
from common.Supervisor import Supervisor
from tools.Utilities import little_separation, middle_separation, big_separation, adapt_path


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

        self._natures = None  # object which lists the nature present in world

        # Time management
        self._timestep_value = None  # value of the timestep used during the simulation (in hours)
        self._time_limit = None  # latest time step of the simulation (in number of iterations)

        # dictionaries contained by world
        self._local_grid = dict()  # grids interns to world
        self._external_grid = dict()  # grids external to world

        self._agents = dict()  # it represents an economic agent, and is attached to, in particular, a contract
        self._clusters = dict()  # a mono-energy sub-environment which favours self-consumption

        self._consumptions = dict()  # dict containing the consumptions
        self._productions = dict()  # dict containing the productions

        self._daemons = dict()  # dict containing the daemons
        self._dataloggers = dict()  # dict containing the dataloggers

        self._supervisors = dict()  # objects which perform the calculus

        self._used_name = []  # this list contains the catalog name of all elements
        # It avoids to erase inadvertently pre-defined elements

    # ##########################################################################################
    # Construction
    # methods are arranged in the order they are supposed to be used
    # ##########################################################################################

    # the following methods concern objects absolutely needed for world to perform a calculus
    def set_catalog(self, catalog):  # definition of a catalog
        if isinstance(catalog, Catalog) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._catalog = catalog

    def set_directory(self, path):  # definition of a case directory and creation of the directory
        instant_date = datetime.datetime.now()  # get the current time
        instant_date = instant_date.strftime("%d_%m_%Y-%H_%M_%S")  # the directory is named after the date

        path = adapt_path([path, f"Case_{instant_date}"])  # path is the root for all files relative to the case

        os.makedirs(path)
        os.makedirs(adapt_path([path, "inputs"]))
        os.makedirs(adapt_path([path, "outputs"]))

        self._catalog.add("path", path)

    def set_natures(self, nature):  # definition of natures dictionary
        if isinstance(nature, NatureList) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._natures = nature
        self._catalog.add("Natures", nature.keys)

    def set_time_manager(self, start_date=datetime.datetime.now(), timestep_value=1, time_limit=24):  # definition of a time manager
        self._catalog.add("physical_time", start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        self._timestep_value = datetime.timedelta(hours=timestep_value)
        self._time_limit = time_limit

    # the following methods concern objects modeling a case
    def register_local_grid(self, local_grid):  # method connecting one local grid to the world
        if local_grid._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{local_grid._name} already in use")

        if isinstance(local_grid, LocalGrid) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        local_grid._register(self._catalog)  # add a catalog to local grid and create relevant entries
        self._local_grid[local_grid._name] = local_grid  # registering the local grid in the dedicated dictionary
        self._used_name.append(local_grid._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_external_grid(self, external_grid):  # method connecting one external grid to the world
        if external_grid._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{external_grid._name} already in use")

        if isinstance(external_grid, ExternalGrid) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")
        
        # checking if the grid is defined correctly
        if external_grid._grid not in self._local_grid:  # if the specified grid does not exist
            raise WorldException(f"{external_grid._grid} does not exist")
        elif external_grid.nature != self._local_grid[external_grid._grid]._nature:  # if the natures are not the sames
            raise WorldException(f"{external_grid._grid} is {self._local_grid[external_grid._grid]._nature}, not {external_grid.nature}")

        external_grid._register(self._catalog)  # add a catalog to external grid and create relevant entries
        self._external_grid[external_grid._name] = external_grid  # registering the external grid in the dedicated
        # dictionary
        self._used_name.append(external_grid._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_agent(self, agent):  # method connecting one agent to the world
        if agent._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{agent._name} already in use")

        if isinstance(agent, Agent) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        agent._register(self._catalog)   # linking the agent with the catalog of world
        self._agents[agent._name] = agent  # registering the agent in the dedicated dictionary
        self._used_name.append(agent._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_cluster(self, cluster):  # method connecting one cluster to the world
        if cluster._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{cluster._name} already in use")

        if isinstance(cluster, Cluster) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        # checking if the grid is defined correctly
        if cluster._grid not in self._local_grid:  # if the specified grid does not exist
            raise WorldException(f"{cluster._grid} does not exist")
        elif cluster.nature != self._local_grid[cluster._grid]._nature:  # if the natures are not the sames
            raise WorldException(f"{cluster._grid} is {self._local_grid[cluster._grid]._nature}, not {cluster.nature}")
        
        cluster._register(self._catalog)  # linking the cluster with the catalog of world
        self._clusters[cluster._name] = cluster  # registering the cluster in the dedicated dictionary
        self._used_name.append(cluster._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_device(self, device):  # method connecting one device to the world
        if device.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        if isinstance(device, Device) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        # checking if the grid is defined correctly
        if device._grid not in self._local_grid:  # if the specified grid does not exist
            raise WorldException(f"{device._grid} does not exist")
        elif device.nature != self._local_grid[device._grid]._nature:  # if the natures are not the sames
            raise WorldException(f"{device._grid} is {self._local_grid[device._grid]._nature}, not {device.nature}")

        # checking if the agent is defined correctly
        if device._agent not in self._agents:  # if the specified agent does not exist
            raise WorldException(f"{device._agent} does not exist")
        elif f"{device._agent}.{device._nature}" not in self._catalog.keys:  # if the agent does not include the
            # nature of the device
            raise WorldException(f"{device._agent} has no contracts for nature {device.nature}")

        # checking if the cluster is defined correctly
        if device._cluster is not None:
            if device._cluster not in self._clusters:  # if the specified cluster does not exist
                raise WorldException(f"{device._cluster} does not exist")
            elif device.nature != self._clusters[device._cluster]._nature:  # if the natures are not the sames
                raise WorldException(f"{device._cluster} is {self._clusters[device._cluster]._nature}, "
                                      f"not {device.nature}")

        if isinstance(device, Consumption):  # If device is a consumer...
            self._consumptions[device.name] = device  # ... it is put in a dedicated dict
        elif isinstance(device, Production):  # If device is a producer...
            self._productions[device.name] = device  # ... it is put in a dedicated dict
        else:
            raise WorldException(f"Unable to add device {device.name}")

        device._register(self._catalog)  # registering of the device in the catalog
        self._used_name.append(device.name)  # adding the name to the list of used names

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        if isinstance(datalogger, Datalogger) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        datalogger._register(self._catalog)   # linking the datalogger with the catalog of world
        self._dataloggers[datalogger.name] = datalogger  # registering the cluster in the dedicated dictionary
        self._used_name.append(datalogger.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_daemon(self, daemon):  # link a daemon with a world (and its catalog)
        if daemon.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{daemon.name} already in use")

        if isinstance(daemon, Daemon) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        daemon._register(self._catalog)  # registering of the device in the catalog
        self._daemons[daemon.name] = daemon  # registering the daemon in the dedicated dictionary
        self._used_name.append(daemon.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_supervisor(self, supervisor):  # definition of the supervisor
        if supervisor.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{supervisor.name} already in use")

        if isinstance(supervisor, Supervisor) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        supervisor._register(self._catalog)   # linking the supervisor with the catalog of world
        self._supervisors[supervisor.name] = supervisor  # registering the cluster in the dedicated dictionary
        self._used_name.append(supervisor.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _check(self):  # a method checking if the world has been well defined
        # 4 things are necessary for world to be correctly defined:
        # 1/ the time manager,
        # 2/ the case directory,
        # 3/ the nature list,
        # 4/ the supervisor

        # first, we check the presence of the necessary objects:
        # checking if a time manager is defined
        if "physical_time" not in self.catalog.keys or "simulation_time" not in self.catalog.keys:
            raise WorldException(f"A time manager is needed")

        # checking if a path is defined
        if "path" not in self.catalog.keys:
            raise WorldException(f"A path is specified for the results files")

        # checking if a nature list is defined
        if self._natures is None:
            raise WorldException(f"A nature list is needed")

        # checking if a supervisor is defined
        if not self._supervisors:
            raise WorldException(f"At least one supervisor is needed")

        # secondly, we check and correct the redundancies
        # removing unused natures (it saves time as the natures list is browsed several times)
        used_natures = list()

        # we concatenate all the the objects having a nature in one dict
        aggregated_dict = dict(self._local_grid)
        aggregated_dict.update(self._external_grid)
        aggregated_dict.update(self._clusters)
        aggregated_dict.update(self._productions)
        aggregated_dict.update(self._consumptions)

        # then we create a list containing all the effectively used natures
        for key in aggregated_dict:
            nature = aggregated_dict[key].nature
            if nature not in used_natures:
                used_natures.append(nature)

        self._natures.purge(used_natures)  # a method which removes the natures not present in used_natures

    def start(self):

        self._check()  # check if everything is fine in world definition

        world = self
        catalog = self._catalog

        path = adapt_path(["usr", "supervisors", "DummySupervisorMain.py"])

        exec(open(path).read())

    # ##########################################################################################
    # Dynamic behaviour
    ############################################################################################

    def _update_time(self):  # update the time entries in the catalog to the next iteration step

        current_time = self._catalog.get("simulation_time")

        physical_time = self._catalog.get("physical_time")
        physical_time += self._timestep_value  # new value of physical time

        self._catalog.set("physical_time", physical_time)  # updating the value of physical time
        self._catalog.set("simulation_time", current_time + 1)

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
        return self._time_limit

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
        self._name = name  # the name which serve as root in the catalog entries
        self._nature = nature  # only entities of same nature can interact

        self._grid = grid_name  # the grid the device belongs to
        self._cluster = cluster_name  # the cluster the device belongs to
        self._agent = agent_name  # the agent represents the owner of the device

        self._catalog = None  # added later

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register_device(self, catalog):  # make the initialization operations undoable without a catalog
        # and relevant for all devices
        self._catalog = catalog  # linking the catalog to the device

        self._catalog.add(f"{self._name}.energy", 0)  # write directly in the catalog the energy
        self._catalog.add(f"{self._name}.min_energy", 0)  # write directly in the catalog the minimum energy
        self._catalog.add(f"{self._name}.price", 0)  # write directly in the catalog the price

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
        pass

    # ##########################################################################################
    # Dynamic behavior
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

    def _register_consumption(self, catalog):  # make the initialization operations undoable without a catalog and
        # relevant for class consumption
        self._register_device(catalog)  # make the operations relevant for all kind of entities

        self._catalog.add(f"{self._name}.priority", 1)  # the higher the priority, the higher the chance of
        # being satisfied in the current time step

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
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

    def _register_production(self, catalog):  # make the initialization operations undoable without a catalog and
        # relevant for class production
        self._register_device(catalog)  # make the operations relevant for all kind of entities

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
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
