# Declaration of core classes
# ##############################################################################################
# Native packages
from datetime import datetime, timedelta
from os import makedirs, remove
from random import random, seed as random_generator_seed, randint, gauss
from json import load, dumps
from shutil import make_archive, unpack_archive, rmtree
from pickle import dump as pickle_dump, load as pickle_load
from math import inf
# Current packages
from src.common.Catalog import Catalog
from src.common.Strategy import Strategy
from src.common.Nature import Nature
from src.common.Aggregator import Aggregator
from src.common.Contract import Contract
from src.common.Agent import Agent
from src.common.Device import Device
from src.common.Daemon import Daemon
from src.common.Datalogger import Datalogger
from src.tools.GraphAndTex import GraphOptions

from src.tools.Utilities import big_separation, adapt_path, into_list
from src.tools.SubclassesDictionary import get_subclasses
from src.tools.GlobalWorld import set_world


# ##############################################################################################
# ##############################################################################################
# The world is the background of a case: it contains and organizes all elements of the code,
# from devices to Supervisors.
# First, it contains the catalog the time manager, the case directory and the strategy, which are all necessary
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

        self._catalog.add("additional_elements", dict())  # a dictionary containing the additional information added by the user to the messages exchanged between devices, contracts and aggregators

        # dictionaries contained by world
        self._subclasses_dictionary = get_subclasses()  # this dictionary contains all the classes defined by the user
        # it serves to re-instantiate daemons, devices, dataloggers, contracts and strategies
        dictionaries = dict()

        dictionaries["natures"] = dict()  # types of energy presents in world
        dictionaries["daemons"] = dict()  # dict containing the daemons
        dictionaries["strategies"] = dict()  # objects which perform the calculus
        dictionaries["aggregators"] = dict()  # a mono-energy sub-environment which favours self-consumption
        dictionaries["agents"] = dict()  # it represents an economic agent, and is attached to, in particular, a contract
        dictionaries["contracts"] = dict()  # dict containing the different contracts
        dictionaries["devices"] = dict()  # dict containing the devices
        dictionaries["dataloggers"] = dict()  # dict containing the dataloggers
        dictionaries["graph_options"] = dict()  # dict containing the graph options

        self._catalog.add("dictionaries", dictionaries)  # a sub-category of the catalog where are available all the elments constituting the model

        self._used_names = []  # this list contains the catalog name of all elements
        # It avoids to erase inadvertently pre-defined elements

        self._aggregator_order = []  # this list allows to know which aggregator have to be run first according to the converters

        set_world(self)  # set world as a global variable used later to instantiate objects

    # ##########################################################################################
    # Construction
    # methods are arranged in the order they are supposed to be used
    # ##########################################################################################

    # ##########################################################################################
    # settings

    def set_directory(self, path):  # definition of a case directory and creation of the directory
        instant_date = datetime.now()  # get the current time
        instant_date = instant_date.strftime("%Y_%m_%d-%H_%M_%S")  # the directory is named after the date

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

    def set_time(self, start_date, time_step_value, time_limit):  # definition of a time manager
        # verifications
        if not isinstance(start_date, type(datetime.now())):
            raise WorldException(f"The start_date argument must be givenin the datetime format.")
        if time_step_value <= 0:
            raise WorldException(f"The time_step_value argument must be a strictly positive number.")
        if time_limit <= 0 and not isinstance(time_limit, int):
            raise WorldException(f"The time_limit argument must be a strictly positive integer.")

        self._catalog.add("physical_time", start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        self._catalog.add("time_step", time_step_value)  # value of a time step, used to adapt hourly-defined profiles
        self._timestep_value = timedelta(hours=time_step_value)
        self._time_limit = time_limit  # the number of the last iteration
        self._catalog.add("time_limit", time_limit)

    # ##########################################################################################
    # options

    def complete_message(self, additional_element, default_value=None):  # this function adds more element in the message exchanged between devices, contracts and aggregators
        # this new element requires to modify the related device, contract and strategy subclasses to have some effect
        self._catalog.get("additional_elements")[additional_element] = default_value

    # ##########################################################################################
    # modelling

    def register_nature(self, nature):  # definition of natures dictionary
        if nature.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{nature.name} already in use")

        if isinstance(nature, Nature) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        for element in self._catalog.get("additional_elements"):  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{nature.name}.{element}", self._catalog.get("additional_elements")[element])

        self._catalog.natures[nature.name] = nature
        self._used_names.append(nature.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_daemon(self, daemon):  # link a daemon with a world (and its catalog)
        if daemon.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{daemon.name} already in use")

        if isinstance(daemon, Daemon) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._catalog.daemons[daemon.name] = daemon  # registering the daemon in the dedicated dictionary
        self._used_names.append(daemon.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_strategy(self, strategy):  # definition of the strategy
        if strategy.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{strategy.name} already in use")

        if isinstance(strategy, Strategy) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        strategy.complete_message(
            self._catalog.get("additional_elements"))  # the  message is completed with the new elements added in world

        self._catalog.strategies[strategy.name] = strategy  # registering the aggregator in the dedicated dictionary
        self._used_names.append(strategy.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_agent(self, agent):  # method connecting one agent to the world
        if agent.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{agent.name} already in use")

        if isinstance(agent, Agent) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        for element in self._catalog.get("additional_elements"):  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{agent.name}.{element}", self._catalog.get("additional_elements")[element])

        if agent.superior:  # if the agent has a superior
            self._catalog.agents[agent.superior]._owned_agents_name.append(agent)

        self._catalog.agents[agent.name] = agent  # registering the agent in the dedicated dictionary
        self._used_names.append(agent.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_contract(self, contract):
        if contract.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{contract.name} already in use")

        if isinstance(contract, Contract) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        for element in self._catalog.get("additional_elements"):  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{contract.name}.{element}", self._catalog.get("additional_elements")[element])

        self._catalog.contracts[contract.name] = contract  # registering the contract in the dedicated dictionary
        self._used_names.append(contract.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing   
        
    def register_aggregator(self, aggregator):  # method connecting one aggregator to the world
        if aggregator.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{aggregator.name} already in use")

        if isinstance(aggregator, Aggregator) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        for element in self._catalog.get("additional_elements"):  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{aggregator.name}.{element}", self._catalog.get("additional_elements")[element])

        if aggregator.superior:  # if the aggregator has a superior
            aggregator.superior._subaggregators.append(aggregator)

        self._catalog.aggregators[aggregator.name] = aggregator  # registering the aggregator in the dedicated dictionary
        self._used_names.append(aggregator.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_device(self, device):  # method connecting one device to the world
        if device.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        if isinstance(device, Device) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        # checking if the agent is defined correctly
        if device._agent.name not in self._catalog.agents:  # if the specified agent does not exist
            raise WorldException(f"{device._agent.name} does not exist")

        device.complete_message(self._catalog.get("additional_elements"))  # the  message is completed with the new elements added in world

        for nature in device.natures:
            device._natures[nature]["aggregator"].add_device(device.name)  # adding the device name to its aggregator list of devices

        self._catalog.devices[device.name] = device  # registering the device in the dedicated dictionary
        self._used_names.append(device.name)  # adding the name to the list of used names

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        if isinstance(datalogger, Datalogger) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._catalog.dataloggers[datalogger.name] = datalogger  # registering the datalogger in the dedicated dictionary
        self._used_names.append(datalogger.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_graph_option(self, graph_option):  # link a GraphOptions with a world (and its catalog)
        if graph_option.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{graph_option.name} already in use")

        if isinstance(graph_option, GraphOptions) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._catalog.graph_options[graph_option.name] = graph_option  # registering the GraphOptions in the dedicated dictionary
        self._used_names.append(graph_option.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    # ##########################################################################################
    # Automated generation of agents
    # ##########################################################################################

    def agent_generation(self, name, quantity, filename, aggregators, price_manager_daemon, data_daemons={}):  # this method creates several agents, each with a predefinite set of devices
        # loading the data in the file
        file = open(filename, "r")
        data = load(file)
        file.close()

        # creation of contracts
        contract_dict = {}
        for contract_type in data["contracts"]:  # for each contract
            contract_name = f"{name}_{data['template name']}_{contract_type}"
            nature = self._catalog.natures[data["contracts"][contract_type]["nature_name"]]
            identifier = price_manager_daemon[nature.name]
            contract_class = self._subclasses_dictionary["Contract"][data["contracts"][contract_type]["contract_subclass"]]

            if len(data["contracts"][contract_type]) == 2:  # if there are no parameters
                contract = contract_class(contract_name, nature, identifier)
            else:  # if there are parameters
                parameters = data["contracts"][contract_type]["contract_subclass"]
                contract = contract_class(contract_name, nature, identifier, parameters)

            contract_dict[contract_type] = contract

        # process of data daemon dictionary
        data_daemons = {key: data_daemons[key].name for key in data_daemons}  # transform the daemons objects into strings

        for i in range(quantity):

            # creation of an agent
            agent_name = f"{name}_{data['template name']}_{str(i)}"
            agent = Agent(agent_name)  # creation of the agent, which name is "Profile X"_"number"

            # creation of devices
            for device_data in data["composition"]:
                for profile in data["composition"][device_data]:
                    if profile["quantity"][0] > profile["quantity"][1]:
                        raise WorldException(f"The minimum number of devices {profile['name']} allowed must be inferior to the maximum number allowed in the profile {data['template name']}.")
                    number_of_devices = self._catalog.get("int")(profile["quantity"][0], profile["quantity"][1])  # the number of devices is chosen randomly inside the limits defined in the agent profile
                    for j in range(number_of_devices):
                        device_name = f"{agent_name}_{profile['name']}_{j}"  # name of the device, "Profile X"_5_Light_0
                        device_class = self._subclasses_dictionary["Device"][device_data]

                        # management of contracts
                        contracts = []
                        for contract_type in contract_dict:
                            if profile["contract"] == contract_type:
                                contracts.append(contract_dict[contract_type])

                        # management of devices needing data
                        if "parameters" in profile:
                            parameters = profile["parameters"]
                            parameters.update(data_daemons)
                        else:
                            parameters = data_daemons

                        device_class(device_name, contracts, agent, aggregators, profile["data_profiles"], parameters)  # creation of the device

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _check(self):  # a method checking if the world has been well defined
        # 3 things are necessary for world to be correctly defined:
        # 1/ time parameters
        # 2/ the random seed
        # 3/ the case directory

        # first, we check the presence of the necessary objects:
        # checking if time parameters are defined
        if "physical_time" not in self.catalog.keys or "simulation_time" not in self.catalog.keys:
            raise WorldException(f"Time parameters are needed")

        # checking if a random seed is defined
        if "float" not in self.catalog.keys:
            raise WorldException(f"A random seed is needed")

        # checking if a path is defined
        if "path" not in self.catalog.keys:
            raise WorldException(f"A path to the results files is needed")

    def _identify_independent_aggregators(self):
        # first, we identify all the highest rank aggregators, who are the sole being called directly by world
        independent_aggregators_list = []
        for aggregator in self._catalog.aggregators.values():
            if not aggregator.superior:
                independent_aggregators_list.append(aggregator)

        return independent_aggregators_list

    def _identify_independent_agents(self):
        independent_agent_list = []  # a list containing all the independant agents
        for agent in self._catalog.agents.values():
            if not agent.superior:  # if the agent has no superior, it is added to the list of independant agents
                independent_agent_list.append(agent)

        return independent_agent_list

    def start(self):
        self._check()  # check if everything is fine in world definition

        independent_aggregators_list = self._identify_independent_aggregators()

        independent_agents_list = self._identify_independent_agents()

        for datalogger in self._catalog.dataloggers.values():
            datalogger.initial_operations()

        # Resolution
        for i in range(0, self.time_limit, 1):

            # ###########################
            # Beginning of the turn
            # ###########################

            print(f"iteration {self._catalog.get('simulation_time')}")

            # reinitialization of values in the catalog
            # these values are, globally, the money and energy balances

            for nature in self._catalog.natures.values():
                nature.reinitialize()

            for strategy in self._catalog.strategies.values():
                strategy.reinitialize()

            for agent in self._catalog.agents.values():
                agent.reinitialize()

            for contract in self._catalog.contracts.values():
                contract.reinitialize()

            for aggregator in self._catalog.aggregators.values():
                aggregator.reinitialize()

            for device in self._catalog.devices.values():
                device.reinitialize()
                device.update()  # devices publish the quantities they are interested in (both in demand and in offer)

            # ###########################
            # Calculus phase
            # ###########################

            # ascendant phase: balances with local energy and formulation of needs (both in demand and in offer)
            for aggregator in independent_aggregators_list:  # aggregators are called according to the predefined order
                aggregator.ask()  # aggregators make local balances and then publish their needs (both in demand and in offer)
                # the method is recursive

            # descendant phase: balances with remote energy
            for aggregator in independent_aggregators_list:  # aggregators are called according to the predefined order
                aggregator.distribute()  # aggregators make local balances and then publish their needs (both in demand and in offer)
                # the method is recursive

            # ###########################
            # End of the turn
            # ###########################

            # devices update their state according to the quantity of energy received/given
            for device in self._catalog.devices.values():
                device.react()
                device.make_balances()

            # balance phase, where results are
            for aggregator in independent_aggregators_list:  # aggregators are called according to the predefined order
                aggregator.make_balances()  # aggregators make local balances and then publish their needs (both in demand and in offer)
                # the method is recursive

            # agent report what happened to their potential owner (i.e to another agent)
            for agent in independent_agents_list:
                agent.report()

            # data exporting
            for datalogger in self._catalog.dataloggers.values():
                datalogger.launch()

            # time update
            self._update_time()

            # daemons activation
            for daemon in self._catalog.daemons.values():
                daemon.launch()

            print()

        for datalogger in self._catalog.dataloggers.values():
            datalogger.final_process()
            datalogger.final_export()

        for daemon in self._catalog.daemons.values():
            daemon.final_process()

    # ##########################################################################################
    # Dynamic behavior
    ############################################################################################

    def _update_time(self):  # second_update the time entries in the catalog to the next iteration step
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

        # # personalized classes file
        #
        # filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Classes.pickle"])
        # file = open(filename, "wb")
        # pickle_dump(self._subclasses_dictionary, file)  # the dictionary containing the classes is exported entirely
        # file.close()

        # natures file
        natures_list = {nature.name: nature.description for nature in self.catalog.natures.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Natures.json"])
        file = open(filename, "w")
        file.write(dumps(natures_list, indent=2))
        file.close()

        # daemons file
        daemons_list = {daemon.name: [f"{type(daemon).__name__}",
                                      daemon._period,
                                      daemon._parameters
                                      ] for daemon in self.catalog.daemons.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Daemon.json"])
        file = open(filename, "w")
        file.write(dumps(daemons_list, indent=2))
        file.close()

        # strategies file
        strategies_list = {strategy.name: [f"{type(strategy).__name__}"] for strategy in self.catalog.strategies.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"strategy.json"])
        file = open(filename, "w")
        file.write(dumps(strategies_list, indent=2))
        file.close()

        # agents file
        agents_list = {agent.name: agent._superior_name for agent in self.catalog.agents.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Agents.json"])
        file = open(filename, "w")
        file.write(dumps(agents_list, indent=2))
        file.close()

        # contracts file
        contracts_list = {contract.name: [f"{type(contract).__name__}",
                                          contract.nature.name,
                                          contract._daemon_name,
                                          contract._parameters
                                          ] for contract in self.catalog.contracts.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Contract.json"])
        file = open(filename, "w")
        file.write(dumps(contracts_list, indent=2))
        file.close()

        # aggregators file
        aggregators_list = {}

        for aggregator in self.catalog.aggregators.values():
            aggregators_list[aggregator.name] = [aggregator.nature.name, aggregator.strategy.name, aggregator.agent.name]
            if aggregator.superior:
                aggregators_list[aggregator.name].append(aggregator.superior.name)
                aggregators_list[aggregator.name].append(aggregator.contract.name)
            else:
                aggregators_list[aggregator.name].append(None)
                aggregators_list[aggregator.name].append(None)

            aggregators_list[aggregator.name].append(aggregator.efficiency)
            if aggregator.capacity == inf:
                aggregators_list[aggregator.name].append("inf")
            else:
                aggregators_list[aggregator.name].append(aggregator.capacity)
            # rajouter forecaster plus tard

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Clusters.json"])
        file = open(filename, "w")
        file.write(dumps(aggregators_list, indent=2))
        file.close()

        # devices file
        devices_list = {device.name: [f"{type(device).__name__}",
                                      [element["contract"].name for element in device._natures.values()],  # contracts
                                      device.agent.name,  # agent
                                      [element["aggregator"].name for element in device._natures.values()],  # aggregators
                                      device._filename,  # where data profiles are found
                                      device._parameters  # the optional parameters used by the device
                                      ] for device in self.catalog.devices.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Device.json"])
        file = open(filename, "w")
        file.write(dumps(devices_list, indent=2))
        file.close()

        # # dataloggers file
        # dataloggers_list = {datalogger.name: [datalogger._filename,
        #                                       datalogger._period,
        #                                       datalogger._graph_options.name,
        #                                       datalogger._graph_labels,
        #                                       datalogger._list
        #                                       ] for datalogger in self.catalog.dataloggers.values()}
        #
        # filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Datalogger.json"])
        # file = open(filename, "w")
        # file.write(dumps(dataloggers_list, indent=2))
        # file.close()

        # creation of the archive
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

        # # personalized classes file
        # file = open("Classes.pickle", "rb")
        #
        # data = pickle_load(file)
        #
        # for user_class in data:
        #     self._subclasses_dictionary[user_class] = data[user_class]
        #
        # file.close()
        # remove("Classes.pickle")  # deleting the useless file

        # Natures file
        file = open("Natures.json", "r")
        data = load(file)

        for nature_name in data:
            nature = Nature(nature_name, data[nature_name])  # creation of a nature

        file.close()
        remove("Natures.json")  # deleting the useless file

        # Daemon file
        file = open("Daemon.json", "r")
        data = load(file)

        for daemon_name in data:
            daemon_period = data[daemon_name][1]
            daemon_parameters = data[daemon_name][2]
            daemon_class = self._subclasses_dictionary["Daemon"][data[daemon_name][0]]
            daemon = daemon_class(daemon_name, daemon_period, daemon_parameters)

        file.close()
        remove("Daemon.json")  # deleting the useless file
        
        # strategy file
        file = open("strategy.json", "r")
        data = load(file)

        for strategy_name in data:
            strategy_period = data[strategy_name][1]
            strategy_parameters = data[strategy_name][2]
            strategy_class = self._subclasses_dictionary["Strategy"][data[strategy_name][0]]
            strategy = strategy_class(strategy_name, strategy_period, strategy_parameters)

        file.close()
        remove("strategy.json")  # deleting the useless file

        # Agents file
        file = open("Agents.json", "r")
        data = load(file)

        for agent_name in data:
            agent = Agent(agent_name)  # creation of an agent

        file.close()
        remove("Agents.json")  # deleting the useless file

        # Contract file
        file = open("Contract.json", "r")
        data = load(file)

        for contract_name in data:
            contract_class = self._subclasses_dictionary["Contract"][data[contract_name][0]]
            contract_nature = self._natures[data[contract_name][1]]
            contract_parameters = data[contract_name][2]

            contract = contract_class(contract_name, contract_nature, contract_parameters)

        file.close()
        remove("Contract.json")  # deleting the useless file

        # Aggregator file
        file = open("Clusters.json", "r")
        data = load(file)

        for aggregator_name in data:
            aggregator_nature = self._natures[data[aggregator_name]]
            aggregator = Aggregator(aggregator_name, aggregator_nature)  # creation of a aggregator

        file.close()
        remove("Clusters.json")  # deleting the useless file

        # Device file
        file = open("Device.json", "r")
        data = load(file)

        for device_name in data:
            agent = self._agents[data[device_name][1]]
            aggregators = [self._aggregators[aggregator_name] for aggregator_name in data[device_name][2]]
            contracts = [self._contracts[contract_name] for contract_name in data[device_name][3]]
            device_class = self._subclasses_dictionary[data[device_name][0]]
            user_profile_name = data[device_name][7]  # loading the user profile name
            usage_profile_name = data[device_name][8]  # loading the usage profile name

            # loading the parameters
            device_parameters = data[device_name][10]

            # creation of the device
            device = device_class["Device"](device_name, contracts, agent, aggregators, user_profile_name, usage_profile_name, device_parameters, "loaded device")

            # loading the real hour
            device._hour = self._catalog.get("physical_time").hour  # loading the hour of the day
            device._period = data[device_name][4]  # loading the period
            device._moment = data[device_name][9]  # loading the initial moment

            # loading the profiles
            device._user_profile = data[device_name][5]  # loading the user profile
            device._usage_profile = data[device_name][6]  # loading the usage profile


        file.close()
        remove("Device.json")  # deleting the useless file

        # # Datalogger file
        # file = open("Datalogger.json", "r")
        # data = load(file)
        #
        # for datalogger_name in data:
        #     filename = data[datalogger_name][0]
        #     period = data[datalogger_name][1]
        #     sum_over_time = data[datalogger_name][2]
        #     logger = Datalogger(self, datalogger_name, filename, period, sum_over_time)  # creation
        #
        #     for entry in data[datalogger_name][3]:
        #         logger.add(entry)  # this datalogger exports all the data available in the catalog
        #
        # file.close()
        # remove("Datalogger.json")  # deleting the useless file

        file.close()

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
        return big_separation + f'\nWORLD = {self._name} : {len(self._catalog.devices)} devices'


# Exception
class WorldException(Exception):
    def __init__(self, message):
        super().__init__(message)


