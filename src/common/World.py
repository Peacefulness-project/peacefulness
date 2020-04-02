# Declaration of core classes
# ##############################################################################################
# Native packages
from datetime import datetime, timedelta
from os import makedirs, remove
from random import random, seed as random_generator_seed, randint, gauss
from json import load, dumps
from shutil import make_archive, unpack_archive, rmtree
from pickle import dump as pickle_dump, load as pickle_load
# Current packages
from src.common.Catalog import Catalog
from src.common.Strategy import Strategy
from src.common.Nature import Nature
from src.common.Aggregator import Aggregator
from src.common.Contract import Contract
from src.common.Agent import Agent
from src.common.Device import Device
from src.common.Converter import Converter
from src.common.Daemon import Daemon
from src.common.Datalogger import Datalogger
from src.tools.Utilities import big_separation, adapt_path
from src.tools.SubclassesDictionary import get_subclasses


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

        # dictionaries contained by world
        self._subclasses_dictionary = get_subclasses()  # this dictionary contains all the classes defined by the user
        # it serves to re-instantiate daemons, devices and Supervisors
        dictionaries = dict()

        dictionaries["forecasters"] = dict()  # objects which are responsible for predicting both quantities produced and consumed
        dictionaries["strategys"] = dict()  # objects which perform the calculus

        dictionaries["natures"] = dict()  # types of energy presents in world

        dictionaries["aggregators"] = dict()  # a mono-energy sub-environment which favours self-consumption
        dictionaries["exchange_nodes"] = dict()  # objects organizing exchanges between aggregators
        
        dictionaries["contracts"] = dict()  # dict containing the different contracts
        dictionaries["agents"] = dict()  # it represents an economic agent, and is attached to, in particular, a contract
        dictionaries["devices"] = dict()  # dict containing the devices
        dictionaries["converters"] = dict()  # dict containing the conversion points

        dictionaries["dataloggers"] = dict()  # dict containing the dataloggers
        dictionaries["daemons"] = dict()  # dict containing the daemons

        self._catalog.add("dictionaries", dictionaries)  # a sub-category of the catalog where are available all the elments constituting the model

        self._used_names = []  # this list contains the catalog name of all elements
        # It avoids to erase inadvertently pre-defined elements

        self._aggregator_order = []  # this list allows to know which aggregator have to be run first according to the converters

    # ##########################################################################################
    # Construction
    # methods are arranged in the order they are supposed to be used
    # ##########################################################################################

    # the following methods concern objects absolutely needed for world to perform a calculus
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

    def set_time(self, start_date=datetime.now(), timestep_value=1, time_limit=24):  # definition of a time manager
        self._catalog.add("physical_time", start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        self._catalog.add("time_step", timestep_value)  # value of a time step, used to adapt hourly-defined profiles
        self._timestep_value = timedelta(hours=timestep_value)
        self._time_limit = time_limit
        self._catalog.add("time_limit", time_limit)

    # the following methods concern objects modeling a case
    def register_strategy(self, strategy):  # definition of the strategy
        if strategy.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{strategy.name} already in use")

        if isinstance(strategy, Strategy) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        strategy._register(self._catalog)   # linking the strategy with the catalog of world
        self._catalog.strategies[strategy.name] = strategy  # registering the aggregator in the dedicated dictionary
        self._used_names.append(strategy.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_nature(self, nature):  # definition of natures dictionary
        if nature.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{nature.name} already in use")

        if isinstance(nature, Nature) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._catalog.natures[nature.name] = nature
        self._used_names.append(nature.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_aggregator(self, aggregator):  # method connecting one aggregator to the world
        if aggregator.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{aggregator.name} already in use")

        if isinstance(aggregator, Aggregator) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        if isinstance(aggregator.superior, Aggregator):  # if the superior of the aggregator is another aggregator
            aggregator.superior._subaggregators.append(aggregator)
        elif aggregator.superior == "exchange":  # if the superior of the aggregator is the exchange node
            self._catalog.exchange_nodes[aggregator] = []

        self._catalog.aggregators[aggregator.name] = aggregator  # registering the aggregator in the dedicated dictionary
        self._used_names.append(aggregator.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_contract(self, contract):
        if contract.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{contract.name} already in use")        
    
        if isinstance(contract, Contract) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")
        
        self._catalog.contracts[contract.name] = contract  # registering the contract in the dedicated dictionary
        self._used_names.append(contract.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing   
        
    def register_agent(self, agent):  # method connecting one agent to the world
        if agent.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{agent.name} already in use")

        if isinstance(agent, Agent) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

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

        for nature in device.natures:  # adding the device name to its aggregator list of devices
            device._natures[nature]["aggregator"].add_device(device.name)

        self._catalog.devices[device.name] = device  # registering the device in the dedicated dictionary
        self._used_names.append(device.name)  # adding the name to the list of used names

    def _search_superior_aggregator(self, aggregator):  # this method returns he ultimate chief of the given aggregator
        if aggregator.superior:
            chief = self._search_superior_aggregator(aggregator.superior)
        else:  # it the aggregator of highest rank
            chief = aggregator

        return chief

    def register_converter(self, converter):  # method connecting one device to the world
        if converter.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{converter.name} already in use")

        if isinstance(converter, Converter) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        # checking if the agent is defined correctly
        if converter._agent.name not in self._catalog.agents:  # if the specified agent does not exist
            raise WorldException(f"{converter._agent.name} does not exist")

        converter.aggregators["downstream_aggregator"].add_converter(converter.name)  # adding the device name to the list of converters of its donwstream aggregator
        converter.aggregators["upstream_aggregator"].add_device(converter.name)  # adding the converter name to the list of devices fo its upstream aggregator

        downstream_aggregator = self._search_superior_aggregator(converter.aggregators["downstream_aggregator"])
        upstream_aggregator = self._search_superior_aggregator(converter.aggregators["upstream_aggregator"])

        # adding these aggregators to the correct order of passage
        if [downstream_aggregator, upstream_aggregator] in self._aggregator_order:  # if a bridge has already been created in the same sense between these two aggregators
            pass  # we do nothing
        else:  # else we check that they have not been engaged somewhere
            registered_downstream_aggregators = [couple[0] for couple in self._aggregator_order]
            registered_upstream_aggregators = [couple[1] for couple in self._aggregator_order]

            if downstream_aggregator not in registered_downstream_aggregators and upstream_aggregator not in registered_upstream_aggregators:
                self._aggregator_order.append([downstream_aggregator, upstream_aggregator])
            else:
                raise WorldException(f"il ne faut pas croiser les effluves, c'est mal")  # virer cette blague eud'brun

        self._catalog.converters[converter.name] = converter  # registering the device in the dedicated dictionary
        self._used_names.append(converter.name)  # adding the name to the list of used names

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        if isinstance(datalogger, Datalogger) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._catalog.dataloggers[datalogger.name] = datalogger  # registering the datalogger in the dedicated dictionary
        self._used_names.append(datalogger.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_daemon(self, daemon):  # link a daemon with a world (and its catalog)
        if daemon.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{daemon.name} already in use")

        if isinstance(daemon, Daemon) is False:  # checking if the object has the expected type
            raise WorldException("The object is not of the correct type")

        self._catalog.daemons[daemon.name] = daemon  # registering the daemon in the dedicated dictionary
        self._used_names.append(daemon.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    # ##########################################################################################
    # Automated generation of agents
    # ##########################################################################################

    def agent_generation(self, quantity, filename, aggregators, contract_identifier):  # this method creates several agents, each with a predefinite set of devices
        # loading the data in the file
        file = open(filename, "r")
        data = load(file)
        file.close()

        # creation of contracts
        contract_dict = {}
        for contract_type in data["contracts"]:  # for each contract
            contract_name = f"{data['template name']}_{contract_type}"
            nature = self._catalog.natures[data["contracts"][contract_type][0]]
            identifier = contract_identifier[nature.name]
            contract_class = self._subclasses_dictionary[data["contracts"][contract_type][1]]

            if len(data["contracts"][contract_type]) == 2:  # if there are no parameters
                contract = contract_class(self, contract_name, nature, identifier)
            else:  # if there are parameters
                parameters = data["contracts"][contract_type][1]
                contract = contract_class(contract_name, nature, identifier, parameters)

            contract_dict[contract_type] = contract

        for i in range(quantity):

            # creation of an agent
            agent_name = f"{data['template name']}_{str(i)}"
            agent = Agent(self, agent_name)  # creation of the agent, which name is "Profile X"_5

            # creation of devices
            for device_data in data["composition"]:
                for profile in data["composition"][device_data]:
                    if profile[3][0] > profile[3][1]:
                        raise WorldException(f"The minimum number of devices {profile[0]} allowed must be inferior to the maximum number allowed in the profile {data['template name']}.")
                    number_of_devices = self._catalog.get("int")(profile[3][0], profile[3][1])  # the number of devices is chosen randomly inside the limits defined in the agent profile
                    for j in range(number_of_devices):
                        device_name = f"{agent_name}_{profile[0]}_{j}"  # name of the device, "Profile X"_5_Light_0
                        device_class = self._subclasses_dictionary[device_data]

                        contracts = []
                        for contract_type in contract_dict:
                            if profile[4] == contract_type:
                                contracts.append(contract_dict[contract_type])

                        if len(profile) == 5:  # if there are no parameters
                            device = device_class(self, device_name, contracts, agent, aggregators, profile[1], profile[2])  # creation of the device
                        else:  # if there are parameters
                            device = device_class(self, device_name, contracts, agent, aggregators, profile[1], profile[2], profile[5])  # creation of the device

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

    def _set_order_of_aggregators(self):
        # first, we identify all the highest rank aggregators, who are the sole being called directly by world
        highest_rank_aggregators = []
        for aggregator in self._catalog.aggregators.values():
            if not aggregator.superior:
                highest_rank_aggregators.append(aggregator)

        organized_aggregators_list = []
        downstream_aggregator_list = [couple[0] for couple in self._aggregator_order]  # the list of upstream aggregators
        upstream_aggregator_list = [couple[1] for couple in self._aggregator_order]  # the list of upstream aggregators
        aggregators_to_tidy = [couple for couple in self._aggregator_order]  # this list contains the aggregators not organized yet
        # writing directly aggregators_to_tidy = aggregator_order just creates a pointer

        # TODO: trouver un moyen d'ordonner les agrégateurs proprement

        # first try
        # for couple in self._aggregator_order:
        #     if couple[0] not in organized_aggregators_list:  # if the couple is not already integrated in the chain
        #         i = len(organized_aggregators_list) - 1
        #         organized_aggregators_list.append(couple[0])  # the downstream aggregator is added first (as it orders a quantity of energy to its converters)...
        #         organized_aggregators_list.append(couple[1])  # ... and the upstream one in second
        #         aggregators_to_tidy.remove(couple)
        #
        #         for couple in aggregators_to_tidy:  # among the not organized yet aggregators...
        #             toto  # we check if

        # second try
        # flag = False
        #
        # for couple in self._aggregator_order:
        #     for i in range(len(organized_aggregators_list)):
        #         if couple[0] == organized_aggregators_list[i]:  # if the downstream aggregator is already present
        #             organized_aggregators_list.insert(i, couple[1])  # we insert the upstream aggregator just after
        #             flag = True
        #         if couple[1] == organized_aggregators_list[i]:  # if the upstream aggregator is already present
        #             organized_aggregators_list.insert(i-1, couple[0])  # we insert the upstream aggregator just after
        #             flag = True
        #
        #     if flag :

        # béquille
        unclassed_aggregators = []
        for aggregator in highest_rank_aggregators:  # as we have just implemented heatpumps, we only need to treat heat aggregators before
            if aggregator.nature.name == "Heat":
                organized_aggregators_list.append({"aggregator": aggregator, "converters": aggregator.converters})
            else:
                unclassed_aggregators.append(aggregator)

        for aggregator in unclassed_aggregators:
            if aggregator not in organized_aggregators_list:
                organized_aggregators_list.append({"aggregator": aggregator, "converters": aggregator.converters})

        return organized_aggregators_list

    def start(self):
        self._check()  # check if everything is fine in world definition

        classed_aggregator_list = self._set_order_of_aggregators()

        # Resolution
        for i in range(0, self.time_limit, 1):

            # ###########################
            # Beginning of the turn
            # ###########################

            print(f"iteration {self._catalog.get('simulation_time')}")

            # reinitialization of values in the catalog
            # these values are, globally, the money and energy balances
            for strategy in self._catalog.strategies.values():
                strategy.reinitialize()

            for nature in self._catalog.natures.values():
                nature.reinitialize()

            for contract in self._catalog.contracts.values():
                contract.reinitialize()

            for agent in self._catalog.agents.values():
                agent.reinitialize()

            for aggregator in self._catalog.aggregators.values():
                aggregator.reinitialize()

            for device in self._catalog.devices.values():
                device.reinitialize()

            for converter in self._catalog.converters.values():
                converter.reinitialize()

            # devices and converters publish the quantities they are interested in (both in demand and in offer)
            for device in self._catalog.devices.values():
                device.update()

            for converter in self._catalog.converters.values():
                converter.first_update()

            # ###########################
            # Calculus phase
            # ###########################

            # forecasting
            for forecaster in self._catalog.forecasters.values():  # forecasters compute predictions
                forecaster.fait_quelque_chose()

            # ascendant phase: balances with local energy and formulation of needs (both in demand and in offer)
            for element in classed_aggregator_list:  # aggregators are called according to the predefined order
                element["aggregator"].ask()  # aggregators make local balances and then publish their needs (both in demand and in offer)
                # the method is recursive
                for converter_name in element["converters"]:
                    converter = self._catalog.converters[converter_name]
                    converter.second_update()
            classed_aggregator_list.reverse()  # we have to reverse the order in the descendant phase, as upstream aggregator have tot ake their decision before downstream ones

            # descendant phase: balances with remote energy
            for element in classed_aggregator_list:  # aggregators are called according to the predefined order
                for converter_name in element["converters"]:
                    converter = self._catalog.converters[converter_name]
                    converter.first_react()
                element["aggregator"].distribute()  # aggregators make local balances and then publish their needs (both in demand and in offer)
                # the method is recursive
            classed_aggregator_list.reverse()

            # ###########################
            # End of the turn
            # ###########################

            # devices and converters update their state according to the quantity of energy received/given
            for device in self._catalog.devices.values():
                device.react()

            for converter in self._catalog.converters.values():
                converter.second_react()

            # data exporting
            for datalogger in self._catalog.dataloggers.values():
                datalogger.launch()

            # daemons activation
            for daemon in self._catalog.daemons.values():
                daemon.launch()

            # time second_update
            self._update_time()

            print()

        # self.catalog.print_debug()  # display the content of the catalog
        # print(self)  # give the name of the world and the quantity of productions and consumptions

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

        # pour le(s) superviseur(s), on verra plus tard

        # personalized classes file

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Classes.pickle"])
        file = open(filename, "wb")
        pickle_dump(self._subclasses_dictionary, file)  # the dictionary containing the classes is exported entirely
        file.close()

        # natures file
        natures_list = {nature.name: nature.description for nature in self._natures.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Natures.json"])
        file = open(filename, "w")
        file.write(dumps(natures_list, indent=2))
        file.close()

        # aggregators file
        aggregators_list = {aggregator.name: [aggregator.nature.name,
                                        aggregator.devices
                                        ]for aggregator in self._aggregators.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Clusters.json"])
        file = open(filename, "w")
        file.write(dumps(aggregators_list, indent=2))
        file.close()

        # contracts file
        contracts_list = {contract.name: [f"{type(contract).__name__}",
                                          contract.nature.name,
                                          contract._parameters
                                          ] for contract in self._contracts.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Contract.json"])
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
                                      [aggregator[0].name for aggregator in device._natures.values()],  # aggregators
                                      [contract[1].name for contract in device._natures.values()],  # contracts
                                      device._period,  # the period of the device
                                      device._user_profile, device._usage_profile,  # the data of the profiles
                                      device.user_profile, device.usage_profile,  # the name of the profiles
                                      device._moment,  # the current moment in the period
                                      device._parameters  # the optional parameters used by the device
                                      ] for device in self.devices.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Device.json"])
        file = open(filename, "w")
        file.write(dumps(devices_list, indent=2))
        file.close()

        # dataloggers file
        dataloggers_list = {datalogger.name: [datalogger._filename, datalogger._period, datalogger._sum, datalogger._list] for datalogger in self.dataloggers.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Datalogger.json"])
        file = open(filename, "w")
        file.write(dumps(dataloggers_list, indent=2))
        file.close()

        # daemons file
        daemons_list = {daemon.name: [f"{type(daemon).__name__}", daemon._period, daemon._parameters] for daemon in self.daemons.values()}

        filename = adapt_path([self._catalog.get("path"), "inputs", "save", f"Daemon.json"])
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
            self._subclasses_dictionary[user_class] = data[user_class]

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

        for aggregator_name in data:
            aggregator_nature = self._natures[data[aggregator_name]]
            aggregator = Aggregator(aggregator_name, aggregator_nature)  # creation of a aggregator
            self.register_aggregator(aggregator)  # registration

        file.close()
        remove("Clusters.json")  # deleting the useless file

        # Contract file
        file = open("Contract.json", "r")
        data = load(file)

        for contract_name in data:
            contract_class = self._subclasses_dictionary[data[contract_name][0]]
            contract_nature = self._natures[data[contract_name][1]]
            contract_parameters = data[contract_name][2]

            contract = contract_class(contract_name, contract_nature, contract_parameters)
            self.register_contract(contract)           

        file.close()
        remove("Contract.json")  # deleting the useless file

        # Agents file
        file = open("Agents.json", "r")
        data = load(file)

        for agent_name in data:
            agent = Agent(agent_name)  # creation of an agent
            self.register_agent(agent)  # registration

        file.close()
        remove("Agents.json")  # deleting the useless file

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
            device = device_class(device_name, contracts, agent, aggregators, user_profile_name, usage_profile_name, device_parameters, "loaded device")

            # loading the real hour
            device._hour = self._catalog.get("physical_time").hour  # loading the hour of the day
            device._period = data[device_name][4]  # loading the period
            device._moment = data[device_name][9]  # loading the initial moment

            # loading the profiles
            device._user_profile = data[device_name][5]  # loading the user profile
            device._usage_profile = data[device_name][6]  # loading the usage profile

            self.register_device(device)

        file.close()
        remove("Device.json")  # deleting the useless file

        # Datalogger file
        file = open("Datalogger.json", "r")
        data = load(file)

        for datalogger_name in data:
            filename = data[datalogger_name][0]
            period = data[datalogger_name][1]
            sum_over_time = data[datalogger_name][2]
            logger = Datalogger(self, datalogger_name, filename, period, sum_over_time)  # creation
            self.register_datalogger(logger)  # registration

            for entry in data[datalogger_name][3]:
                logger.add(entry)  # this datalogger exports all the data available in the catalog

        file.close()
        remove("Datalogger.json")  # deleting the useless file

        # Daemon file
        file = open("Daemon.json", "r")
        data = load(file)

        for daemon_name in data:
            daemon_period = data[daemon_name][1]
            daemon_parameters = data[daemon_name][2]
            daemon_class = self._subclasses_dictionary[data[daemon_name][0]]
            daemon = daemon_class(daemon_name, daemon_period, daemon_parameters)
            self.register_daemon(daemon)

        file.close()
        remove("Daemon.json")  # deleting the useless file

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


# Exception
class WorldException(Exception):
    def __init__(self, message):
        super().__init__(message)


