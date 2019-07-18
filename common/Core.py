# Declaration of core classes
# ##############################################################################################
# Native packages
import datetime
import os
import random as rnd
import json
import shutil
import inspect
import pickle
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

        # Randomness management
        self._random_seed = None  # yhe seed used in the random number generator of Python

        # dictionaries contained by world
        self._user_classes = dict()  # this dictionary contains all the classes defined by the user
        # it serves to re-instantiate daemons and devices

        self._natures = dict()  # energy present in world

        self._clusters = dict()  # a mono-energy sub-environment which favours self-consumption
        self._grids = dict()  # this dict repertories clusters which are identified as grids greater than world
        # they serve as a default cluster

        self._agents = dict()  # it represents an economic agent, and is attached to, in particular, a contract
        self._devices = dict()  # dict containing the devices

        self._dataloggers = dict()  # dict containing the dataloggers
        self._daemons = dict()  # dict containing the daemons

        self._supervisors = dict()  # objects which perform the calculus

        self._used_names = []  # this list contains the catalog name of all elements
        # It avoids to erase inadvertently pre-defined elements

    # ##########################################################################################
    # Construction
    # methods are arranged in the order they are supposed to be used
    # ##########################################################################################

    # the following methods concern objects absolutely needed for world to perform a calculus
    def set_catalog(self, catalog):  # definition of a catalog
        if not isinstance(catalog, Catalog):  # checking if the object has the expected type
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

    def set_random_seed(self, seed=datetime.datetime.now()):  # this method defines the seed used by the random number generator of Python
        self._random_seed = seed  # the seed is saved
        rnd.seed(self._random_seed)  # the seed is passed to world in order to save it somewhere

        def rand_float():  # function returning a float between 0 and 1
            return rnd.random()

        def rand_int(min_int, max_int):  # function returning an int between min and max
            return rnd.randint(min_int, max_int)

        self._catalog.add("float", rand_float)
        self._catalog.add("int", rand_int)

    def set_time(self, start_date=datetime.datetime.now(), timestep_value=1, time_limit=24):  # definition of a time manager
        self._catalog.add("physical_time", start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        self._catalog.add("time_step", timestep_value)  # value of a time step, used to adapt hourly-defined profiles
        self._timestep_value = datetime.timedelta(hours=timestep_value)
        self._time_limit = time_limit

    # the following methods concern objects modeling a case
    def register_nature(self, nature):  # definition of natures dictionary
        if isinstance(nature, Nature) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._natures[nature.name] = nature

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

    def register_agent(self, agent):  # method connecting one agent to the world
        if agent.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{agent.name} already in use")

        if isinstance(agent, Agent) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        agent._register(self._catalog)   # linking the agent with the catalog of world
        self._agents[agent.name] = agent  # registering the agent in the dedicated dictionary
        self._used_names.append(agent.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_device(self, device):  # method connecting one device to the world
        if device.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        if isinstance(device, Device) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        # checking if the agent is defined correctly
        if device._agent.name not in self._agents:  # if the specified agent does not exist
            raise WorldException(f"{device._agent.name} does not exist")

        # if the agent does not include the nature of the device
        for nature in device.natures:
            if nature not in device.agent.natures:
                raise WorldException(f"{device._agent.name} has no contracts for nature {nature.name}")

        if type(device) not in self._user_classes:  # saving the class in the dedicated dict
            absolute_path = inspect.getfile(type(device))  # this is the absolute path to the file where the class is defined
            module_name = absolute_path.split("usr")[-1]
            module_name = module_name.replace("/" or "\\", ".")  # the syntax for module importation in python needs "." instead of "/" or "\"
            module_name = "usr" + module_name[:-3]  # here we add the usr we delete earlier and we delete the ".py"
            self._user_classes[f"{type(device).__name__}"] = [module_name, type(device)]
        
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
        
        if type(daemon) not in self._user_classes:  # saving the class in the dedicated dict
            absolute_path = inspect.getfile(type(daemon))  # this is the absolute path to the file where the class is defined
            module_name = absolute_path.split("usr")[-1]
            module_name = module_name.replace("/" or "\\", ".")  # the syntax for module importation in python needs "." instead of "/" or "\"
            module_name = "usr" + module_name[:-3]  # here we add the usr we delete earlier and we delete the ".py"
            self._user_classes[f"{type(daemon).__name__}"] = [module_name, type(daemon)]

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

    def agent_generation(self, quantity, filename, clusters):  # this method creates several agents, each with a predefinite set of devices

        # loading the data in the file
        file = open(filename, "r")
        data = json.load(file)
        file.close()

        for i in range(quantity):

            # creation of an agent
            agent_name = f"{data['template name']}_{str(i)}"
            agent = Agent(agent_name)  # creation of the agent, which name is "Profile X"_5
            self.register_agent(agent)
            for nature in data["contracts"]:  # for each nature, the relevant contract is set
                contract = data["contracts"][nature]
                agent.set_contract(self._natures[nature], contract)  # definition of a contract

            # creation of devices
            for device_data in data["composition"]:
                for j in range(device_data[2]):
                    device_name = f"{agent.name}_{device_data[1]}_{j}"  # name of the device, "Profile X"_5_Light_0
                    device_class = self._user_classes[device_data[0]][1]
                    device = device_class(device_name, agent, clusters, device_data[3])  # creation of the device
                    self.register_device(device)

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

        # checking if a supervisor is defined
        if not self._supervisors:
            raise WorldException(f"At least one supervisor is needed")

    def start(self):

        self._check()  # check if everything is fine in world definition

        world = self
        catalog = self._catalog

        for supervisor in self._supervisors:
            path = adapt_path(["usr", "supervisors", self.supervisors[supervisor].filename])

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

    def save(self):  # this method allows to export world
        # the idea is to save the minimum information given by the user in the main
        # to be able to reconstruct it later

        filepath = adapt_path([self._catalog.get("path"), "inputs", "save"])
        os.makedirs(filepath)

        # world file
        world_dict = {"name": self.name,

                      "random seed": self._random_seed,

                      # time management
                      "start date": self._catalog.get("physical_time").strftime("%d %b %Y %H:%M:%S"),  # converting the datetime object into a string
                      "time step": self.catalog.get("time_step"),
                      "time limit": self.time_limit
                      }

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"World.json"])
        file = open(filename, "w")
        file.write(json.dumps(world_dict, indent=2))

        # pour le(s) superviseur(s), on verra plus tard

        # personalized classes file
        user_classes_list = dict()
        # for user_class in self._user_classes:
        #     user_classes_list[user_class] = [self._user_classes[user_class][0]]
        #     string_class = str(pickle.dumps(self._user_classes[user_class][1]))  # a format allowing to serialize a class to JSON and then deserialize it
        #     user_classes_list[user_class].append(string_class)

        for user_class in self._user_classes:
            user_classes_list[user_class] = self._user_classes[user_class]

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Classes.pickle"])
        file = open(filename, "wb")
        pickle.dump(user_classes_list, file)
        # file.write(json.dumps(user_classes_list, indent=2))

        # natures file
        natures_list = {nature.name: nature.description for nature in self._natures.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Natures.json"])
        file = open(filename, "w")
        file.write(json.dumps(natures_list, indent=2))

        # clusters file
        clusters_list = {cluster.name: cluster.nature.name for cluster in self._clusters.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Clusters.json"])
        file = open(filename, "w")
        file.write(json.dumps(clusters_list, indent=2))

        # agents file
        agents_list = {agent.name: {nature.name: agent._contract[nature] for nature in agent._contract} for agent in self._agents.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Agents.json"])
        file = open(filename, "w")
        file.write(json.dumps(agents_list, indent=2))

        # devices file
        devices_list = {device.name: [f"{type(device).__name__}", device._agent.name, [cluster.name for cluster in device._natures.values()], device._period, device._usage_profile, device._user_profile] for device in self.devices.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Devices.json"])
        file = open(filename, "w")
        file.write(json.dumps(devices_list, indent=2))

        # dataloggers file
        dataloggers_list = {datalogger.name: [datalogger._filename, datalogger._period, datalogger._sum, datalogger._list] for datalogger in self.dataloggers.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Dataloggers.json"])
        file = open(filename, "w")
        file.write(json.dumps(dataloggers_list, indent=2))

        # daemons file
        daemons_list = {daemon.name: [f"{type(daemon).__name__}", daemon._period, daemon._parameters] for daemon in self.daemons.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Daemons.json"])
        file = open(filename, "w")
        file.write(json.dumps(daemons_list, indent=2))

        file.close()

        shutil.make_archive(filepath, "tar", filepath)  # packing the archive
        shutil.rmtree(filepath)  # deleting the directory with all the now useless files

    def load(self, filename):
        shutil.unpack_archive(filename, format="tar")  # unpacking the archive

        # World file
        file = open("World.json", "r")
        data = json.load(file)

        self.set_random_seed(data["random seed"])

        start_date = data["start date"]
        start_date = datetime.datetime.strptime(start_date, "%d %b %Y %H:%M:%S")  # converting the string into a datetime object
        time_step = data["time step"]
        time_limit = data["time limit"]
        self.set_time(start_date, time_step, time_limit)

        os.remove("World.json")  # deleting the useless world file
        # personalized_classs_list = [personalized_class for personalized_class in self._personalized_classes]

        # # personalized classes file
        file = open("Classes.pickle", "rb")

        data = pickle.load(file)

        for user_class in data:
            self._user_classes[user_class] = data[user_class]

        # for user_class in data:
        #     truc = data[user_class][1]
        #     truc = truc[2:-1]
        #     truc = bytes(truc, 'ASCII')
        #     print(truc)
        #     truc = pickle.loads(truc)
        #     print(truc)
        #
        # test = __import__('usr.Devices.DummyDevice', globals(), locals(), ['DummyNonControllableDevice'])
        # # print(inspect.getfile(test.DummyNonControllableDevice))
        # DummyNonControllableDevice = test.DummyNonControllableDevice()

        #
        # personalized_classs_list = {class_name: globals()[class_name] for class_name in data }
        #
        os.remove("Classes.pickle")  # deleting the useless world file

        # Natures file
        file = open("Natures.json", "r")
        data = json.load(file)

        for nature_name in data:
            nature = Nature(nature_name, data[nature_name])  # creation of a nature
            self.register_nature(nature)  # registration

        os.remove("Natures.json")  # deleting the useless file

        # Clusters file
        file = open("Clusters.json", "r")
        data = json.load(file)

        for cluster_name in data:
            cluster_nature = self._natures[data[cluster_name]]
            cluster = Cluster(cluster_name, cluster_nature)  # creation of a cluster
            self.register_cluster(cluster)  # registration

        os.remove("Clusters.json")  # deleting the useless file

        # Agents file
        file = open("Agents.json", "r")
        data = json.load(file)

        for agent_name in data:
            agent = Agent(agent_name)  # creation of an agent
            self.register_agent(agent)  # registration

            for nature_name in data[agent_name]:
                contract = data[agent_name]
                nature = self._natures[nature_name]
                agent.set_contract(nature, contract)  # definition of a contract

        os.remove("Agents.json")  # deleting the useless file

        # Devices file
        file = open("Devices.json", "r")
        data = json.load(file)

        for device_name in data:
            agent = self._agents[data[device_name][1]]
            clusters = [self._clusters[cluster_name] for cluster_name in data[device_name][2]]
            device_class = self._user_classes[data[device_name][0]][1]

            device = device_class(device_name, agent, clusters, "loaded device")

            # getting the real hour
            device._hour = self._catalog.get("physical_time").hour  # getting the hour of the day
            device._period = data[device_name][3]
            device._usage_profile = data[device_name][4]
            device._user_profile = data[device_name][5]

            self.register_device(device)

        os.remove("Devices.json")  # deleting the useless file

        # Dataloggers file
        file = open("Dataloggers.json", "r")
        data = json.load(file)

        for datalogger_name in data:
            filename = data[datalogger_name][0]
            period = data[datalogger_name][1]
            sum_over_time = data[datalogger_name][2]
            logger = Datalogger(datalogger_name, filename, period, sum_over_time)  # creation
            self.register_datalogger(logger)  # registration

            for entry in data[datalogger_name][3]:
                logger.add(entry)  # this datalogger exports all the data available in the catalog

        os.remove("Dataloggers.json")  # deleting the useless file

        # Daemons file
        file = open("Daemons.json", "r")
        data = json.load(file)

        for daemon_name in data:
            daemon_period = data[daemon_name][1]
            daemon_parameters = data[daemon_name][2]
            daemon_class = self._user_classes[data[daemon_name][0]][1]
            daemon = daemon_class(daemon_name, daemon_period, daemon_parameters)
            self.register_daemon(daemon)

        os.remove("Daemons.json")  # deleting the useless file

        file.close()

    # properties
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
    def clusters(self):  # shortcut for read-only
        return self._clusters

    @property
    def agents(self):  # shortcut for read-only
        return self._agents

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

    def __init__(self, name, agent_name, clusters, filename):
        self._name = name  # the name which serve as root in the catalog entries

        self._filename = filename  # the name of the data file

        self._remaining_time = 0  # this counter indicates if a usage is running and how much time is will run
        self._hour = None  # the hour of the day

        self._user_profile = []  # user profile of utilisation, describing user's priority
        # hour since the beginning of the period : [ priority, usage ID ]
        # the user profile lasts 1 day and starts at 00:00 AM

        self._usage_profile = []  # energy and interruptibility for one usage
        # [ energy consumption, priority ]

        # here are data dicts dedicated to different levels of energy needed/proposed each turn
        # 1 key <=> 1 energy nature
        self._natures = dict()
        self._inputs = dict()
        self._outputs = dict()

        clusters = into_list(clusters)  # make it iterable
        for cluster in clusters:
            if cluster.nature in self.natures:
                raise DeviceException(f"a cluster has already been defined for nature {cluster.nature}")
            else:
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
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted", 0)  # the energy asked or proposed by the device
            self._catalog.add(f"{self.name}.{nature.name}.energy_accorded", 0)  # the energy delivered or accpeted by the supervisor
        self._catalog.add(f"{self.name}.price", 0)  # write directly in the catalog the price
        self._catalog.add(f"{self.name}.priority", 1)   # the higher the priority, the higher the chance of
                                                        # being satisfied in the current time step

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
        self._register_device(catalog)
        self._user_register()
        if self._filename != "loaded device":  # if a filename has been defined
            self._get_consumption()
            # else, it is assumed that the device has been load

    def _user_register(self):  # where users put device-specific behaviors
        pass

    def _get_consumption(self):
        pass

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def _update(self):  # method updating needs of the devices before the supervision
        pass

    def react(self):  # method updating the device according to the decisions taken by the supervisor
        #
        #

        self._user_react()

    def _user_react(self):  # where users put device-specific behaviors
        pass

    # ##########################################################################################
    # Class method
    # ##########################################################################################

    def create_devices(cls, quantity, name_root, world, agent, clusters, filename):
        pass

    create_devices = classmethod(create_devices)

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
