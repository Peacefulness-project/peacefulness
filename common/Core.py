# Declaration of core classes
import datetime
from common.Catalog import Catalog
from tools.Utilities import little_separation, middle_separation, big_separation
from common.lib.NatureList import NatureList
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

        self._time_manager = None  # object which manages time

        self._case_directory = None  # object which manages the result directory

        self._natures = None  # object which lists the nature present in world

        # dictionaries contained by world
        self._clusters = dict()  # a mono-energy sub-environment which favours self-consumption
        self._agents = dict()  # it represents an economic agent, and is attached to, in particular, a contract

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
        self._case_directory.add_catalog(self._catalog)  # linking the case_directory with the catalog of world
        case_directory.create()  # create the directory and publish its path in the catalog

    def set_time_manager(self, time_manager):  # definition of a time manager
        self._time_manager = time_manager
        self._time_manager.add_catalog(self._catalog)  # linking the time_manager with the catalog of world

    def set_natures(self, nature):  # definition of natures dictionary
        self._natures = nature
        self._catalog.add("Natures", nature.keys)

    def register_device(self, device):  # method adding one device to the world
        if device.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        if isinstance(device, Consumption):  # If device is a consumer...
            self._consumptions[device.name] = device  # ... it is put in a dedicated dict
        elif isinstance(device, Production):  # If device is a producer...
            self._productions[device.name] = device  # ... it is put in a dedicated dict
        else:
            raise WorldException(f"Unable to add device {device.name}")

        self._used_name.append(device.name)  # adding the name to the list of used names
        device._catalog = self._catalog  # linking the catalog to the device
        device.register()  # registering of the device in the catalog

    def register_cluster(self, cluster):  # links the device with a cluster
        if cluster._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{cluster._name} already in use")

        cluster.add_catalog(self._catalog)  # linking the cluster with the catalog of world
        self._clusters[cluster._name] = cluster  # registering the cluster in the dedicated dictionary
        self._used_name.append(cluster._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_agent(self, agent):  # links the device with an agent
        if agent._name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{agent._name} already in use")

        agent.add_catalog(self._catalog)   # linking the agent with the catalog of world
        self._agents[agent._name] = agent  # registering the agent in the dedicated dictionary
        self._used_name.append(agent._name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def link_cluster(self, cluster, device_list):  # link an device with a cluster
        if isinstance(device_list, str):  # if device is not a list
            device_list = [device_list]  # it is transformed into a list
            # This operation allows to pass list of entities or single entities

        for key in device_list:
            if key in self._consumptions:
                device = self._consumptions[key]
            elif key in self._productions:
                device = self._productions[key]
            else:
                raise WorldException(f"{key} is not a device")

            if device._nature == self._clusters[cluster]._nature:
                device._cluster = cluster
            else:
                raise DeviceException(f"cluster and device must have the same nature")

    def link_agent(self, agent, device_list):  # link an device with an agent
        if isinstance(device_list, str):  # if device is not a list
            device_list = [device_list]  # it is transformed into a list
            # This operation allows to pass list of entities or single entities

        for key in device_list:
            if key in self._consumptions:
                device = self._consumptions[key]
            elif key in self._productions:
                device = self._productions[key]
            else:
                raise WorldException(f"{key} is not an device")

            if f"{agent}.{device._nature}" in self._catalog.keys:
                device._agent = agent
            else:
                raise DeviceException(f"no {device._nature} in {agent}")

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_name:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        datalogger.add_catalog(self._catalog)   # linking the datalogger with the catalog of world
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

    def check(self):  # a method checking if the world has been well defined
        # 3 things are necessary for world which are not created when it is defined:
        # the time manager, the case directory and the ownership of an entity

        # checking if a time manager is defined
        if self._time_manager is None:
            raise WorldException(f"A time manager is needed")

        # checking if a case directory is defined
        if self._case_directory is None:
            raise WorldException(f"A case directory is needed")

        # checking if each device has an agent
        problem = False  # it allows to print every absence before raising an error
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

        for key in self._dataloggers:  # activation of the dataloggers, they must be called before the daemons,
            # who may have an impact on data
            self._dataloggers[key].launch()

        for key in self._daemons:  # activation of the daemons
            self._daemons[key].launch()

        self._time_manager.update_time()

    def update(self):  # method updating data to the current timestep

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
# Root class for all devices constituting a case
class Device:

    def __init__(self, name, nature):
        self._nature = nature  # only entities of same nature can interact

        self._name = name  # the name which serve as root in the catalog entries

        self._cluster = None  # the cluster the device belongs to
        self._agent = None  # the agent represents the owner of the device

        self._catalog = None  # added later

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def register_device(self):  # make the initialization operations undoable without a catalog
        # and relevant for all devices
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
        return middle_separation + f"\nDevice {self.name} of type {self.__class__.__name__}"


# ##############################################################################################
# ##############################################################################################
# Consumer device
# They correspond to one engine (one dishwasher e.g)
class Consumption(Device):

    def __init__(self, name, nature):
        super().__init__(name, nature)

        self._interruptibility = 0  # 1 means the system can be switched off while working
        # params eco, socio, etc

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def register_consumption(self):  # make the initialization operations undoable without a catalog and
        # relevant for class consumption
        self.register_device()  # make the operations relevant for all kind of entities

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
# Production device
# They correspond to a group of plants of same nature (an eolian park e.g)
class Production(Device):

    def __init__(self, name, nature):
        super().__init__(name, nature)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def register_production(self):  # make the initialization operations undoable without a catalog and
        # relevant for class production
        self.register_device()  # make the operations relevant for all kind of entities

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


class DeviceException(Exception):
    def __init__(self, message):
        super().__init__(message)
