# Declaration of core classes
# ##############################################################################################
# Native packages
from datetime import datetime, timedelta
from os import makedirs, remove
from random import random, seed as random_generator_seed, randint, gauss
from json import load, dumps
from shutil import make_archive, unpack_archive, rmtree
from math import ceil
from pickle import dump as pickle_dump, load as pickle_load
# Current packages
from common.Catalog import Catalog
from common.ExchangeNode import ExchangeNode
from common.Nature import Nature
from common.Contract import Contract
from common.Agent import Agent
from common.Cluster import Cluster
from common.Datalogger import Datalogger
from common.Daemon import Daemon
from common.Supervisor import Supervisor
from tools.Utilities import middle_separation, big_separation, adapt_path, into_list
from tools.UserClassesDictionary import user_classes_dictionary


# ##############################################################################################
# ##############################################################################################
# The world is the background of a case: it contains and organizes all elements of the code,
# from devices to Supervisors.
# First, it contains the catalog the time manager, the case directory and the supervisor, which are all necessary
# Then, it contains dictionaries of elements that describe the studied case, such as devices or agents
# Lastly, it contains a dictionary, of so-called data-loggers, who are in charge of exporting the data into files
class World:

    def __init__(self, name=None):
        if name:
            self._name = name
        else:  # By default, world is named after the date
            self._name = f"Unnamed ({datetime.now()})"

        self._catalog = Catalog()  # data catalog which gathers all data

        # Time management
        self._timestep_value = None  # value of the timestep used during the simulation (in hours)
        self._time_limit = None  # latest time step of the simulation (in number of iterations)

        # Randomness management
        self._random_seed = None  # the seed used in the random number generator of Python

        # dictionaries contained by world
        self._user_classes = user_classes_dictionary  # this dictionary contains all the classes defined by the user
        # it serves to re-instantiate daemons, devices and Supervisors
        dictionaries = dict()

        dictionaries["forecasters"] = dict()  # objects which are responsible for predicting both quantities produced and consumed
        dictionaries["supervisors"] = dict()  # objects which perform the calculus

        dictionaries["natures"] = dict()  # types of energy presents in world

        dictionaries["clusters"] = dict()  # a mono-energy sub-environment which favours self-consumption
        dictionaries["exchange_nodes"] = dict()  # objects organizing exchanges between clusters
        
        dictionaries["contracts"] = dict()  # dict containing the different contracts
        dictionaries["agents"] = dict()  # it represents an economic agent, and is attached to, in particular, a contract
        dictionaries["devices"] = dict()  # dict containing the devices

        dictionaries["dataloggers"] = dict()  # dict containing the dataloggers
        dictionaries["daemons"] = dict()  # dict containing the daemons

        self._catalog.add("dictionaries", dictionaries)  # a sub-category of the catalog where are available all the elments constituting the model

        self._used_names = []  # this list contains the catalog name of all elements
        # It avoids to erase inadvertently pre-defined elements

    # ##########################################################################################
    # Construction
    # methods are arranged in the order they are supposed to be used
    # ##########################################################################################

    # the following methods concern objects absolutely needed for world to perform a calculus
    def set_directory(self, path):  # definition of a case directory and creation of the directory
        instant_date = datetime.now()  # get the current time
        instant_date = instant_date.strftime("%d_%m_%Y-%H_%M_%S")  # the directory is named after the date

        path = adapt_path([path, f"Case_{instant_date}"])  # path is the root for all files relative to the case

        makedirs(path)
        makedirs(adapt_path([path, "inputs"]))
        makedirs(adapt_path([path, "outputs"]))

        self._catalog.add("path", path)

    def set_random_seed(self, seed=datetime.now()):  # this method defines the seed used by the random number generator of Python
        self._random_seed = seed  # the seed is saved
        random_generator_seed(self._random_seed)  # the seed is passed to world in order to save it somewhere

        def rand_float():  # function returning a float between 0 and 1
            return random()

        def rand_int(min_int, max_int):  # function returning an int between min and max
            return randint(min_int, max_int)

        def rand_gauss(mean, standard_deviation):
            return gauss(mean, standard_deviation)

        self._catalog.add("float", rand_float)
        self._catalog.add("int", rand_int)
        self._catalog.add("gaussian", rand_gauss)

    def set_time(self, start_date=datetime.now(), timestep_value=1, time_limit=24):  # definition of a time manager
        self._catalog.add("physical_time", start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        self._catalog.add("time_step", timestep_value)  # value of a time step, used to adapt hourly-defined profiles
        self._timestep_value = timedelta(hours=timestep_value)
        self._time_limit = time_limit

    # the following methods concern objects modeling a case
    def register_supervisor(self, supervisor):  # definition of the supervisor
        if supervisor.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{supervisor.name} already in use")

        if isinstance(supervisor, Supervisor) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        supervisor._register(self._catalog)   # linking the supervisor with the catalog of world
        self._catalog.supervisors[supervisor.name] = supervisor  # registering the cluster in the dedicated dictionary
        self._used_names.append(supervisor.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_nature(self, nature):  # definition of natures dictionary
        if nature.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{nature.name} already in use")

        if isinstance(nature, Nature) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        nature.register(self._catalog)
        self._catalog.natures[nature.name] = nature
        self._used_names.append(nature.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_cluster(self, cluster):  # method connecting one cluster to the world
        if cluster.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{cluster.name} already in use")

        if isinstance(cluster, Cluster) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        if isinstance(cluster.superior, Cluster):  # if the superior of the cluster is another cluster
            cluster.superior._subclusters.append(cluster)
        elif cluster.superior == "exchange":  # if the superior of the cluster is the exchange node
            self._catalog.exchange_nodes[cluster] = []

        cluster._register(self._catalog)  # linking the cluster with the catalog of world
        self._catalog.clusters[cluster.name] = cluster  # registering the cluster in the dedicated dictionary
        self._used_names.append(cluster.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def create_link_between_clusters(self, cluster_source, cluster_destination, efficiency, capacity):  # enables the possbility for cluster source to sell energy to cluster destination
        if isinstance(cluster_destination, Cluster) is False:
            raise WorldException(f"{cluster_destination} is not a cluster")

        try:  # check if the cluster destination is registered in the exchange leader
            self._catalog.exchange_nodes[cluster_source] = [cluster_destination, efficiency, capacity]
        except:
            raise WorldException(f"{cluster_source} is not registered as eligible to exchanges")

        if cluster_destination not in self._catalog.exchange_nodes:  # check if the cluster destination is registered in the exchange leader
            raise WorldException(f"{cluster_source} is not registered as eligible to exchanges")

    def register_contract(self, contract):
        if contract.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{contract.name} already in use")        
    
        if isinstance(contract, Contract) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")
        
        contract._register(self._catalog)   # linking the agent with the catalog of world
        self._catalog.contracts[contract.name] = contract  # registering the contract in the dedicated dictionary
        self._used_names.append(contract.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing   
        
    def register_agent(self, agent):  # method connecting one agent to the world
        if agent.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{agent.name} already in use")

        if isinstance(agent, Agent) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        agent._register(self._catalog)   # linking the agent with the catalog of world
        self._catalog.agents[agent.name] = agent  # registering the agent in the dedicated dictionary
        self._used_names.append(agent.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_device(self, device):  # method connecting one device to the world
        if device.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        if isinstance(device, Device) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        # checking if the agent is defined correctly
        if device._agent.name not in self._catalog.agents:  # if the specified agent does not exist
            raise WorldException(f"{device._agent.name} does not exist")

        for nature in device.natures:  # adding the device name to its cluster list of device
            device._natures[nature]["cluster"]._devices.append(device.name)

        self._catalog.devices[device.name] = device  # registering the device in the dedicated dictionary
        device._register(self._catalog)  # registering of the device in the catalog
        self._used_names.append(device.name)  # adding the name to the list of used names

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        if isinstance(datalogger, Datalogger) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        datalogger._register(self._catalog)   # linking the datalogger with the catalog of world
        self._catalog.dataloggers[datalogger.name] = datalogger  # registering the datalogger in the dedicated dictionary
        self._used_names.append(datalogger.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_daemon(self, daemon):  # link a daemon with a world (and its catalog)
        if daemon.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{daemon.name} already in use")

        if isinstance(daemon, Daemon) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        daemon._register(self._catalog)  # registering of the device in the catalog
        self._catalog.daemons[daemon.name] = daemon  # registering the daemon in the dedicated dictionary
        self._used_names.append(daemon.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    # ##########################################################################################
    # Automated generation of agents
    # ##########################################################################################

    def agent_generation(self, quantity, filename, clusters):  # this method creates several agents, each with a predefinite set of devices

        # loading the data in the file
        file = open(filename, "r")
        data = load(file)
        file.close()

        for i in range(quantity):

            # creation of an agent
            agent_name = f"{data['template name']}_{str(i)}"
            agent = Agent(agent_name)  # creation of the agent, which name is "Profile X"_5
            self.register_agent(agent)

            # creation of contracts
            contract_list = []
            for nature_name in data["contracts"]:  # for each nature, the relevant contract is set
                contract_name = f"{agent_name}_{nature_name}_contract"
                contract_class = self._user_classes[data["contracts"][nature_name][0]]
                parameters = data["contracts"][nature_name][1]
                nature = self._catalog.natures[nature_name]
                contract = contract_class(contract_name, nature, parameters)
                self.register_contract(contract)
                contract_list.append(contract)
                agent.set_contract(nature, contract)

            # creation of devices
            for device_data in data["composition"]:
                for profile in data["composition"][device_data]:
                    number_of_devices = self._catalog.get("int")(profile[3][0], profile[3][1])  # the number of devices is chosen randomly inside the limits defined in the agent profile
                    for j in range(number_of_devices):
                        device_name = f"{agent_name}_{profile[0]}_{j}"  # name of the device, "Profile X"_5_Light_0
                        device_class = self._user_classes[device_data]

                        device = device_class(device_name, contract_list, agent, clusters, profile[1], profile[2])  # creation of the device
                        self.register_device(device)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _check(self):  # a method checking if the world has been well defined
        # 2 things are necessary for world to be correctly defined:
        # 1/ time parameters
        # 2/ the random seed
        # 3/ the case directory

        # first, we check the presence of the necessary objects:
        # checking if time parameters are defined
        if "physical_time" not in self.catalog.keys or "simulation_time" not in self.catalog.keys:
            raise WorldException(f"Time parameters are needed")

        # checking if a random seed is defined
        if "path" not in self.catalog.keys:
            raise WorldException(f"A random seed is needed")

        # checking if a path is defined
        if "path" not in self.catalog.keys:
            raise WorldException(f"A path is to the results files is needed")

    def start(self):
        self._check()  # check if everything is fine in world definition

        # add for each type of contracts

        # Resolution
        for i in range(0, self.time_limit, 1):

            # ###########################
            # Beginning of the turn
            # ###########################

            # reinitialization of values in the catalog
            # these values are, globally, the money and energy balances
            for supervisor in self._catalog.supervisors.values():
                supervisor.reinitialize()

            for nature in self._catalog.natures.values():
                nature.reinitialize()

            for contract in self._catalog.contracts.values():
                contract.reinitialize()

            for agent in self._catalog.agents.values():
                agent.reinitialize()

            for cluster in self._catalog.clusters.values():
                cluster.reinitialize()

            # devices publish the quantities they are interested in (both in demand and in offer)
            for device in self._catalog.devices.values():
                device.update()

            # ###########################
            # Calculus phase
            # ###########################

            # forecasting
            for forecaster in self._catalog.forecasters.values():
                forecaster.fait_quelque_chose()

            # ascendant phase: balances with local energy and formulation of needs (both in demand and in offer)
            for cluster in self._catalog.exchange_nodes:  # clusters make local balances and then publish their needs (both in demand and in offer)
                cluster.ask()  # recursive function to make sure all clusters are reached

            # high-level exchange phase
            # self._catalog.exchange_nodes.organise_exchanges()  # decides of who exchanges what with who

            # descendant phase: balances with remote energy
            for cluster in self._catalog.exchange_nodes:  # clusters distribute the energy they exchanged with outside
                cluster.distribute()  # recursive function to make sure all clusters are reached

            # ###########################
            # End of the turn
            # ###########################

            # devices update their state according to the quantity of energy received/given
            for device in self._catalog.devices.values():
                device.react()

            # data exporting
            for datalogger in self._catalog.dataloggers.values():
                datalogger.launch()

            # daemons activation
            for daemon in self._catalog.daemons.values():
                daemon.launch()

            # time update
            self._update_time()

            print("\n")

        # self.catalog.print_debug()  # display the content of the catalog
        # print(self)  # give the name of the world and the quantity of productions and consumptions

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
    # save/load system
    # ##########################################################################################
    # this method allows to export world
    # the idea is to save the minimum information given by the user in the main
    # to be able to reconstruct it later

    def save(self):
        filepath = adapt_path([self._catalog.get("path"), "inputs", "save"])
        makedirs(filepath)

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
        file.write(dumps(world_dict, indent=2))
        file.close()

        # pour le(s) superviseur(s), on verra plus tard

        # personalized classes file

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Classes.pickle"])
        file = open(filename, "wb")
        pickle_dump(self._user_classes, file)  # the dictionary containing the classes is exported entirely
        file.close()

        # natures file
        natures_list = {nature.name: nature.description for nature in self._natures.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Natures.json"])
        file = open(filename, "w")
        file.write(dumps(natures_list, indent=2))
        file.close()

        # clusters file
        clusters_list = {cluster.name: [cluster.nature.name,
                                        cluster.devices
                                        ]for cluster in self._clusters.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Clusters.json"])
        file = open(filename, "w")
        file.write(dumps(clusters_list, indent=2))
        file.close()

        # contracts file
        contracts_list = {contract.name: [f"{type(contract).__name__}",
                                          contract.nature.name,
                                          contract._parameters
                                          ] for contract in self._contracts.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Contracts.json"])
        file = open(filename, "w")
        file.write(dumps(contracts_list, indent=2))
        file.close()

        # agents file
        agents_list = {agent.name: {nature.name: [nature.name, agent._contracts[nature].name] for nature in agent._contracts} for agent in self._agents.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Agents.json"])
        file = open(filename, "w")
        file.write(dumps(agents_list, indent=2))
        file.close()

        # devices file
        devices_list = {device.name: [f"{type(device).__name__}", device._agent.name,
                                      [cluster[0].name for cluster in device._natures.values()],  # clusters
                                      [contract[1].name for contract in device._natures.values()],  # contracts
                                      device._period,  # the period of the device
                                      device._user_profile, device._usage_profile,  # the data of the profiles
                                      device.user_profile, device.usage_profile,  # the name of the profiles
                                      device._moment,  # the current moment in the period
                                      device._parameters  # the optional parameters used by the device
                                      ] for device in self.devices.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Devices.json"])
        file = open(filename, "w")
        file.write(dumps(devices_list, indent=2))
        file.close()

        # dataloggers file
        dataloggers_list = {datalogger.name: [datalogger._filename, datalogger._period, datalogger._sum, datalogger._list] for datalogger in self.dataloggers.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Dataloggers.json"])
        file = open(filename, "w")
        file.write(dumps(dataloggers_list, indent=2))
        file.close()

        # daemons file
        daemons_list = {daemon.name: [f"{type(daemon).__name__}", daemon._period, daemon._parameters] for daemon in self.daemons.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Daemons.json"])
        file = open(filename, "w")
        file.write(dumps(daemons_list, indent=2))
        file.close()

        make_archive(filepath, "tar", filepath)  # packing the archive
        rmtree(filepath)  # deleting the directory with all the now useless files

    def load(self, filename):
        unpack_archive(filename, format="tar")  # unpacking the archive

        # World file
        file = open("World.json", "r")
        data = load(file)

        self.set_random_seed(data["random seed"])

        start_date = data["start date"]
        start_date = datetime.strptime(start_date, "%d %b %Y %H:%M:%S")  # converting the string into a datetime object
        time_step = data["time step"]
        time_limit = data["time limit"]
        self.set_time(start_date, time_step, time_limit)

        file.close()
        remove("World.json")  # deleting the useless world file

        # personalized classes file
        file = open("Classes.pickle", "rb")

        data = pickle_load(file)

        for user_class in data:
            self._user_classes[user_class] = data[user_class]

        file.close()
        remove("Classes.pickle")  # deleting the useless file

        # Natures file
        file = open("Natures.json", "r")
        data = load(file)

        for nature_name in data:
            nature = Nature(nature_name, data[nature_name])  # creation of a nature
            self.register_nature(nature)  # registration

        file.close()
        remove("Natures.json")  # deleting the useless file

        # Clusters file
        file = open("Clusters.json", "r")
        data = load(file)

        for cluster_name in data:
            cluster_nature = self._natures[data[cluster_name]]
            cluster = Cluster(cluster_name, cluster_nature)  # creation of a cluster
            self.register_cluster(cluster)  # registration

        file.close()
        remove("Clusters.json")  # deleting the useless file

        # Contracts file
        file = open("Contracts.json", "r")
        data = load(file)

        for contract_name in data:
            contract_class = self._user_classes[data[contract_name][0]]
            contract_nature = self._natures[data[contract_name][1]]
            contract_parameters = data[contract_name][2]

            contract = contract_class(contract_name, contract_nature, contract_parameters)
            self.register_contract(contract)           

        file.close()
        remove("Contracts.json")  # deleting the useless file

        # Agents file
        file = open("Agents.json", "r")
        data = load(file)

        for agent_name in data:
            agent = Agent(agent_name)  # creation of an agent
            self.register_agent(agent)  # registration

        file.close()
        remove("Agents.json")  # deleting the useless file

        # Devices file
        file = open("Devices.json", "r")
        data = load(file)

        for device_name in data:
            agent = self._agents[data[device_name][1]]
            clusters = [self._clusters[cluster_name] for cluster_name in data[device_name][2]]
            contracts = [self._contracts[contract_name] for contract_name in data[device_name][3]]
            device_class = self._user_classes[data[device_name][0]]
            user_profile_name = data[device_name][7]  # loading the user profile name
            usage_profile_name = data[device_name][8]  # loading the usage profile name

            # loading the parameters
            device_parameters = data[device_name][10]

            # creation of the device
            device = device_class(device_name, contracts, agent, clusters, user_profile_name, usage_profile_name, device_parameters, "loaded device")

            # loading the real hour
            device._hour = self._catalog.get("physical_time").hour  # loading the hour of the day
            device._period = data[device_name][4]  # loading the period
            device._moment = data[device_name][9]  # loading the initial moment

            # loading the profiles
            device._user_profile = data[device_name][5]  # loading the user profile
            device._usage_profile = data[device_name][6]  # loading the usage profile

            self.register_device(device)

        file.close()
        remove("Devices.json")  # deleting the useless file

        # Dataloggers file
        file = open("Dataloggers.json", "r")
        data = load(file)

        for datalogger_name in data:
            filename = data[datalogger_name][0]
            period = data[datalogger_name][1]
            sum_over_time = data[datalogger_name][2]
            logger = Datalogger(datalogger_name, filename, period, sum_over_time)  # creation
            self.register_datalogger(logger)  # registration

            for entry in data[datalogger_name][3]:
                logger.add(entry)  # this datalogger exports all the data available in the catalog

        file.close()
        remove("Dataloggers.json")  # deleting the useless file

        # Daemons file
        file = open("Daemons.json", "r")
        data = load(file)

        for daemon_name in data:
            daemon_period = data[daemon_name][1]
            daemon_parameters = data[daemon_name][2]
            daemon_class = self._user_classes[data[daemon_name][0]]
            daemon = daemon_class(daemon_name, daemon_period, daemon_parameters)
            self.register_daemon(daemon)

        file.close()
        remove("Daemons.json")  # deleting the useless file

        file.close()

    # ##########################################################################################
    # Utility
    # ##########################################################################################

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
        return big_separation + f'\nWORLD = {self._name} : {len(self._catalog.devices)} devices'


# ##############################################################################################
# ##############################################################################################
# Root class for all devices constituting a case
class Device:

    def __init__(self, name, contracts, agent, clusters, filename, user_type, consumption_device, parameters=None):
        self._name = name  # the name which serve as root in the catalog entries

        self._filename = filename  # the name of the data file

        self._moment = None  # the current moment in the period
        self._period = None  # the duration of a classic cycle of use for the user of the device
        self._offset = None  # the delay between the beginning of the period and the beginning of the year

        self._user_profile_name = user_type
        self._user_profile = []  # user profile of utilisation, describing user's priority
        # the content differs depending on the kind of device

        self._usage_profile_name = consumption_device
        self._usage_profile = []  # energy profile dor one usage of the device
        # the content differs depending on the kind of device

        # here are data dicts dedicated to different levels of energy needed/proposed each turn
        # 1 key <=> 1 energy nature
        self._natures = dict() # contains, for each energy nature used by the device, the cluster and the nature associated
        self._inputs = dict()
        self._outputs = dict()

        clusters = into_list(clusters)  # make it iterable
        for cluster in clusters:
            if cluster.nature in self.natures:
                raise DeviceException(f"a cluster has already been defined for nature {cluster.nature}")
            else:
                self._natures[cluster.nature] = {"cluster": None, "contract": None}
                self._natures[cluster.nature]["cluster"] = cluster

        contracts = into_list(contracts)  # make it iterable
        for contract in contracts:
            if self.natures[contract.nature]["contract"]:
                raise DeviceException(f"a contract has already been defined for nature {contract.nature}")
            else:
                try:  # "try" allows to test if self._natures[nature of the contract] was created in the cluster definition step
                    self._natures[contract.nature]["contract"] = contract  # add the contract
                except:
                    raise DeviceException(f"a cluster is missing for nature {contract.nature}")

        self._agent = agent  # the agent represents the owner of the device

        self._catalog = None  # added later

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # make the initialization operations undoable without a catalog
        self._catalog = catalog  # linking the catalog to the device

        for nature in self.natures:
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted", {"energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": None})  # the energy asked or proposed by the device ant the price associated
            # [ [Emin, Enom, Emax], price]
            self._catalog.add(f"{self.name}.{nature.name}.energy_accorded", {"quantity": 0, "price": 0})  # the energy delivered or accepted by the supervisor

        self._user_register()  # here the possibility is let to the user to modify things according to his needs

        if self._filename != "loaded device":  # if a filename has been defined...
            self._get_consumption()  # ... then the file is converted into consumption profiles
            # else, the device has been loaded and does not need a data file

    def _user_register(self):  # where users put device-specific behaviors
        pass

    # ##########################################################################################
    # Consumption reading
    # ##########################################################################################

    def _get_consumption(self):
        pass

    def _read_consumption_data(self):

        # parsing the data
        file = open(self._filename, "r")
        data = load(file)

        # getting the user profile
        try:
            data_user = data["user_profile"][self._user_profile_name]
        except:
            raise DeviceException(f"{self._user_profile_name} does not belong to the list of predefined user profiles for the class {type(self).__name__}: {data['user_profile'].keys()}")

        # getting the usage profile
        try:
            data_device = data["device_consumption"][self._usage_profile_name]
        except:
            raise DeviceException(f"{self._usage_profile_name} does not belong to the list of predefined device profiles for the class {type(self).__name__}: {data['device_consumption'].keys()}")

        file.close()

        return [data_user, data_device]

    def _data_user_creation(self, data_user):  # modification to enable the device to have a period starting a saturday at 0:00 AM

        # creation of the consumption data
        time_step = self._catalog.get("time_step")
        self._period = int(data_user["period"]//time_step)  # the number of rounds corresponding to a period
        # the period MUST be a multiple of the time step

        if type(data_user["offset"]) is float or type(data_user["offset"]) is int:
            self._offset = data_user["offset"]  # the delay between the beginning of the period and the beginning of the year
        elif data_user["offset"] == "Week":  # if the usage takes place the WE, the offset is set at saturday at 0:00 AM
            year = self._catalog.get("physical_time").year  # the year at the beginning of the simulation
            weekday = datetime(year=year, month=1, day=1).weekday()  # the day corresponding to the first day of the year: 0 for Monday, 1 for Tuesday, etc
            offset = weekday  # delay in days between monday and the day
            # without the max(), for a sunday, offset would have been -1, which cause trouble if the period is superior to 1 week
            offset *= 24  # delay in hours between saturday and the day

            self._offset = offset

    def _offset_management(self):
        time_step = self._catalog.get("time_step")
        year = self._catalog.get("physical_time").year  # the year at the beginning of the simulation
        beginning = self._catalog.get("physical_time") - datetime(year=year, month=1, day=1)  # number of hours elapsed since the beginning of the year
        beginning = beginning.total_seconds()/3600  # hours -> seconds
        beginning = (beginning - self._offset)/time_step % self._period
        self._moment = ceil(beginning)  # the position in the period where the device starts

        return beginning

    def _unused_nature_removal(self):  # removal of unused natures in the self._natures i.e natures with no profiles
        nature_to_remove = []  # buffer (as it is not possible to remove keys in a dictionary being read)

        for nature in self._natures:
            if nature.name not in self._usage_profile.keys():
                nature_to_remove.append(nature)

        for nature in nature_to_remove:
            self._natures[nature]["cluster"].devices.remove(self.name)
            self._natures.pop(nature)
            self._catalog.remove(f"{self.name}.{nature.name}.energy_accorded")
            self._catalog.remove(f"{self.name}.{nature.name}.energy_wanted")

    def publish_wanted_energy(self, energy_wanted):  # apply the contract to the energy wanted and then publish it in the catalog
        for nature in self.natures:  # publication of the consumption in the catalog
            energy_wanted[nature.name] = self.natures[nature]["contract"].quantity_modification(energy_wanted[nature.name], self.agent.name)  # the contract may modify the energy wanted
            self.set_energy_wanted_quantity(nature, energy_wanted[nature.name]["energy_minimum"],
                                            energy_wanted[nature.name]["energy_nominal"],
                                            energy_wanted[nature.name]["energy_maximum"])  # publication of the energy wanted in the catalog
            self.set_energy_wanted_price(nature, energy_wanted[nature.name]["price"])  # publication of the price of the energy wanted in the catalog

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        pass

    def react(self):  # method updating the device according to the decisions taken by the supervisor
        self._user_react()

        energy_sold = dict()
        energy_bought = dict()

        for nature in self._natures:
            energy_amount = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]
            # self._natures[nature][1]._billing(energy_amount, self._agent.name)  # call the method billing from the contract

            if energy_amount < 0:  # if the device consumes energy
                energy_sold[nature.name] = energy_amount
                energy_bought[nature.name] = 0
            else:  # if the device delivers energy
                energy_bought[nature.name] = energy_amount
                energy_sold[nature.name] = 0

            # # balance at the cluster level
            # energy_sold_cluster = self._catalog.get(f"{self.natures[nature][0].name}.{nature.name}.energy_sold")["inside"]
            # energy_bought_cluster = self._catalog.get(f"{self.natures[nature][0].name}.{nature.name}.energy_bought")["inside"]
            # money_spent_cluster = self._catalog.get(f"{self.natures[nature][0].name}.{nature.name}.money_spent")
            # money_earned_cluster = self._catalog.get(f"{self.natures[nature][0].name}.{nature.name}.money_earned")
            #
            # self._catalog.set(f"{self.natures[nature][0].name}.{nature.name}.energy_sold", energy_sold_cluster + energy_sold[nature.name])  # report the energy delivered by the device
            # self._catalog.set(f"{self.natures[nature][0].name}.{nature.name}.energy_bought", energy_bought_cluster + energy_bought[nature.name])  # report the energy consumed by the device
            # self._catalog.set(f"{self.natures[nature][0].name}.{nature.name}.money_spent", money_spent_cluster)  # money spent by the cluster to buy energy during the round
            # self._catalog.set(f"{self.natures[nature][0].name}.{nature.name}.money_earned", money_earned_cluster)  # money earned by the cluster by selling energy during the round

            # balance for different natures
            energy_sold_nature = self._catalog.get(f"{nature.name}.energy_produced")
            energy_bought_nature = self._catalog.get(f"{nature.name}.energy_consumed")
            money_spent_nature = self._catalog.get(f"{nature.name}.money_spent")
            money_earned_nature = self._catalog.get(f"{nature.name}.money_earned")

            self._catalog.set(f"{nature.name}.energy_produced", energy_sold_nature + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{nature.name}.energy_consumed", energy_bought_nature + energy_bought[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{nature.name}.money_spent", money_spent_nature)  # money spent by the cluster to buy energy during the round
            self._catalog.set(f"{nature.name}.money_earned", money_earned_nature)  # money earned by the cluster by selling energy during the round

            # balance at the contract level
            energy_sold_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.energy_sold")
            energy_bought_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.energy_bought")
            money_spent_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.money_spent")
            money_earned_contract = self._catalog.get(f"{self.natures[nature]['contract'].name}.money_earned")

            self._catalog.set(f"{self.natures[nature]['contract'].name}.energy_sold", energy_sold_contract + energy_sold[nature.name])  # report the energy delivered by the device
            self._catalog.set(f"{self.natures[nature]['contract'].name}.energy_bought", energy_bought_contract + energy_bought[nature.name])  # report the energy consumed by the device
            self._catalog.set(f"{self.natures[nature]['contract'].name}.money_spent", money_spent_contract)  # money spent by the contract to buy energy during the round
            self._catalog.set(f"{self.natures[nature]['contract'].name}.money_earned", money_earned_contract)  # money earned by the contract by selling energy during the round

        # balance at the agent level
        energy_sold_agent = self._catalog.get(f"{self.agent.name}.energy_sold")
        energy_bought_agent = self._catalog.get(f"{self.agent.name}.energy_bought")
        money_spent_agent = self._catalog.get(f"{self.agent.name}.money_spent")
        money_earned_agent = self._catalog.get(f"{self.agent.name}.money_earned")

        self._catalog.set(f"{self.agent.name}.energy_sold", energy_sold_agent + sum(energy_sold.values()))  # report the energy delivered by the device
        self._catalog.set(f"{self.agent.name}.energy_bought", energy_bought_agent + sum(energy_bought.values()))  # report the energy consumed by the device
        self._catalog.set(f"{self.agent.name}.money_spent", money_spent_agent)  # money spent by the cluster to buy energy during the round
        self._catalog.set(f"{self.agent.name}.money_earned", money_earned_agent)  # money earned by the cluster by selling energy during the round

    def _user_react(self):  # where users put device-specific behaviors
        pass

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    # getter/setter for the accorded energy
    def get_energy_accorded_quantity(self, nature):  # return the quantity of energy accorded to the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["quantity"]

    def set_energy_accorded_quantity(self, nature, value):  # set the quantity of energy accorded to the device during the round
        energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")
        energy_accorded["quantity"] = value
        self._catalog.set(f"{self.name}.{nature.name}.energy_accorded", energy_accorded)

    def get_energy_accorded_price(self, nature):  # return the price of the energy accorded to the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")["price"]

    def set_energy_accorded_price(self, nature, value):  # set the price of the energy accorded to the device during the round
        energy_accorded = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")
        energy_accorded["price"] = value
        self._catalog.set(f"{self.name}.{nature.name}.energy_accorded", energy_accorded)
        
    # getter/setter for the wanted energy
    def get_energy_wanted_min(self, nature):  # return the minimum quantity of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["energy_minimum"]

    def get_energy_wanted_nom(self, nature):  # return the nominal quantity of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["energy_nominal"]

    def get_energy_wanted_max(self, nature):  # return the maximum quantity of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["energy_maximum"]

    def get_energy_wanted_price(self, nature):  # return the price for the quantity of energy wanted by the device during the round
        return self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")["price"]

    def set_energy_wanted_quantity(self, nature, Emin, Enom, Emax):  # set the quantity of energy wanted by the device during the round
        energy_wanted = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")
        energy_wanted["energy_minimum"] = Emin
        energy_wanted["energy_nominal"] = Enom
        energy_wanted["energy_maximum"] = Emax
        self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted)

    def set_energy_wanted_price(self, nature, value):  # set the price for the quantity of energy wanted by the device during the round
        energy_wanted = self._catalog.get(f"{self.name}.{nature.name}.energy_wanted")
        energy_wanted["price"] = value
        self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted)

    @property
    def name(self):  # shortcut for read-only
        return self._name

    @property
    def natures(self):  # shortcut for read-only
        return self._natures

    @property
    def usage_profile(self):  # shortcut for read-only
        return self._usage_profile_name

    @property
    def user_profile(self):  # shortcut for read-only
        return self._user_profile_name

    @property
    def agent(self):  # shortcut for read-only
        return self._agent

    def __str__(self):
        return middle_separation + f"\nDevice {self.name} of type {self.__class__.__name__}"


# Exception
class WorldException(Exception):
    def __init__(self, message):
        super().__init__(message)


class DeviceException(Exception):
    def __init__(self, message):
        super().__init__(message)
