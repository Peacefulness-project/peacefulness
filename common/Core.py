# Declaration of core classes
# ##############################################################################################
# Native packages
import datetime
import os
# Current packages
from common.Catalog import Catalog
from common.Nature import Nature
from common.Agent import Agent
from common.Cluster import Cluster
from common.Datalogger import Datalogger
from common.Daemon import Daemon
from common.Supervisor import Supervisor
from tools.Utilities import middle_separation, big_separation, adapt_path, into_list


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

        # Time management
        self._timestep_value = None  # value of the timestep used during the simulation (in hours)
        self._time_limit = None  # latest time step of the simulation (in number of iterations)

        # dictionaries contained by world
        self._natures = dict()  # energy present in world

        self._agents = dict()  # it represents an economic agent, and is attached to, in particular, a contract

        self._clusters = dict()  # a mono-energy sub-environment which favours self-consumption
        self._grids = dict()  # this dict repertories clusters which are identified as grids greater than world
        # they serve as a default cluster

        self._devices = dict()  # dict containing the devices
        self._consumptions = dict()  # dict containing the consumptions
        self._productions = dict()  # dict containing the productions

        self._daemons = dict()  # dict containing the daemons
        self._dataloggers = dict()  # dict containing the dataloggers

        self._supervisors = dict()  # objects which perform the calculus

        self._used_names = []  # this list contains the catalog name of all elements
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

    def set_time_manager(self, start_date=datetime.datetime.now(), timestep_value=1, time_limit=24):  # definition of a time manager
        self._catalog.add("physical_time", start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        self._timestep_value = datetime.timedelta(hours=timestep_value)
        self._time_limit = time_limit

    # the following methods concern objects modeling a case
    def register_nature(self, nature):  # definition of natures dictionary
        if isinstance(nature, Nature) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._natures[nature.name] = nature

    def register_agent(self, agent):  # method connecting one agent to the world
        if agent.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{agent.name} already in use")

        if isinstance(agent, Agent) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        agent._register(self._catalog)   # linking the agent with the catalog of world
        self._agents[agent.name] = agent  # registering the agent in the dedicated dictionary
        self._used_names.append(agent.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_cluster(self, cluster):  # method connecting one cluster to the world
        if cluster.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{cluster.name} already in use")

        if isinstance(cluster, Cluster) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        if cluster.is_grid:  # if the cluster is identified as a greater grid than world
            # it serves a default cluster for the corresponding nature
            self._grids[cluster.nature] = cluster.name  # and is indexed in a special dict
        
        cluster._register(self._catalog)  # linking the cluster with the catalog of world
        self._clusters[cluster.name] = cluster  # registering the cluster in the dedicated dictionary
        self._used_names.append(cluster.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_device(self, device):  # method connecting one device to the world
        if device.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        if isinstance(device, Device) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        # checking if a cluster has been defined for each nature
        for nature in device.natures:
            if device.natures[nature] is None:  # if it has not:
                if nature.has_external_grid:  # if a grid is defined, it is attached to it
                    device._natures[nature] = self._clusters[self._grids[nature]]
                else:  # otherwise, an exception is raised
                    raise DeviceException(f"a cluster is needed for {device.name}, as no default grid is defined for {nature.name}")

        # checking if the agent is defined correctly
        if device._agent.name not in self._agents:  # if the specified agent does not exist
            raise WorldException(f"{device._agent.name} does not exist")

        # if the agent does not include the nature of the device
        for nature in device.natures:
            if nature not in device.agent.natures:
                raise WorldException(f"{device._agent.name} has no contracts for nature {nature.name}")

        self._devices[device.name] = device
        device._register(self._catalog)  # registering of the device in the catalog
        self._used_names.append(device.name)  # adding the name to the list of used names

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        if isinstance(datalogger, Datalogger) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        datalogger._register(self._catalog)   # linking the datalogger with the catalog of world
        self._dataloggers[datalogger.name] = datalogger  # registering the cluster in the dedicated dictionary
        self._used_names.append(datalogger.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_daemon(self, daemon):  # link a daemon with a world (and its catalog)
        if daemon.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{daemon.name} already in use")

        if isinstance(daemon, Daemon) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        daemon._register(self._catalog)  # registering of the device in the catalog
        self._daemons[daemon.name] = daemon  # registering the daemon in the dedicated dictionary
        self._used_names.append(daemon.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_supervisor(self, supervisor):  # definition of the supervisor
        if supervisor.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{supervisor.name} already in use")

        if isinstance(supervisor, Supervisor) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        supervisor._register(self._catalog)   # linking the supervisor with the catalog of world
        self._supervisors[supervisor.name] = supervisor  # registering the cluster in the dedicated dictionary
        self._used_names.append(supervisor.name)  # adding the name to the list of used names
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

    def start(self):

        self._check()  # check if everything is fine in world definition

        world = self
        catalog = self._catalog

        path = adapt_path(["usr", "supervisors", "DummySupervisorMain.py"])

        exec(open(path).read())

    # ##########################################################################################
    # Dynamic behavior
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

    def __str__(self):
        return big_separation + f'\nWORLD = {self._name} : {len(self.devices)} devices'

    # shortcuts to access the dictionaries
    @property
    def natures(self):  # shortcut for read-only
        return self._natures

    @property
    def agents(self):  # shortcut for read-only
        return self._agents

    @property
    def clusters(self):  # shortcut for read-only
        return self._clusters

    @property
    def devices(self):  # shortcut for read-only
        return self._devices

    @property
    def daemons(self):  # shortcut for read-only
        return self._daemons

    @property
    def dataloggers(self):  # shortcut for read-only
        return self._dataloggers

    @property
    def supervisors(self):  # shortcut for read-only
        return self._supervisors


# ##############################################################################################
# ##############################################################################################
# Root class for all devices constituting a case
class Device:

    def __init__(self, name, natures, agent_name, clusters):
        self._name = name  # the name which serve as root in the catalog entries

        # here are data dicts dedicated to different levels of energy needed/proposed each turn
        # 1 key <=> 1 energy nature
        self._natures = dict()
        self._inputs = dict()
        self._outputs = dict()

        natures = into_list(natures)
        for nature in natures:
            self._natures[nature] = None
            self._inputs[nature] = [0, 0, 0]
            self._outputs[nature] = [0, 0, 0]

        if clusters:
            clusters = into_list(clusters)
            for cluster in clusters:
                self._natures[cluster.nature] = cluster

        self._agent = agent_name  # the agent represents the owner of the device

        self._catalog = None  # added later

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register_device(self, catalog):  # make the initialization operations undoable without a catalog
        # and relevant for all devices
        self._catalog = catalog  # linking the catalog to the device

        for nature in self.natures:
            self._catalog.add(f"{self.name}.{nature.name}.asked_energy", 0)  # write directly in the catalog the energy
            self._catalog.add(f"{self.name}.{nature.name}.proposed_energy", 0)  # write directly in the catalog the energy
            self._catalog.add(f"{self.name}.{nature.name}.min_energy", 0)  # write directly in the catalog the minimum energy
            self._catalog.add(f"{self.name}.{nature.name}.max_energy", 0)  # write directly in the catalog the maximum energy
        self._catalog.add(f"{self.name}.price", 0)  # write directly in the catalog the price
        self._catalog.add(f"{self.name}.priority", 1)   # the higher the priority, the higher the chance of
                                                        # being satisfied in the current time step

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
        self._register_device(catalog)
        self._user_register()

    def _user_register(self):  # where users put device-specific behaviors
        pass

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # method updating needs of the devices before the supervision
        pass

    def react(self):  # method updating the device according to the decisions taken by the supervisor
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def mass_create(cls, n, name, world, agent_name, cluster_name=None):
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
    def natures(self):  # shortcut for read-only
        return self._natures

    @property
    def agent(self):  # shortcut for read-only
        return self._agent

    def __str__(self):
        return middle_separation + f"\nDevice {self.name} of type {self.__class__.__name__}"


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
