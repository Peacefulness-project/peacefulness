# Declaration of core classes
# ##############################################################################################
# Native packages
import gc
from datetime import datetime, timedelta
from os import makedirs
from random import random, seed as random_generator_seed, randint, gauss, getstate, setstate
from typing import List, Callable
# Current packages
from src.common.Catalog import Catalog
from src.common.Messages import MessagesManager
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
    ref_world = None

    def __init__(self, name: str = None):
        if name:
            self._name = name
        else:  # By default, world is named after the date
            self._name = f"Unnamed ({datetime.now()})"

        self._catalog = Catalog()  # data catalog which gathers all data

        self._random_state = getstate()

        # Time management
        self._timestep_value = None  # value of the timestep used during the simulation (in hours)
        self._time_limit = None  # latest time step of the simulation (in number of iterations)

        # Randomness management
        self._random_seed = None  # the seed used in the random number generator of Python

        # dictionaries contained by world
        self._subclasses_dictionary = get_subclasses()  # this dictionary contains all the classes defined by the user
        # it serves to re-instantiate daemons, devices, dataloggers, contracts and strategies
        instance_dictionaries = dict()

        instance_dictionaries["natures"] = dict()  # types of energy presents in world
        instance_dictionaries["daemons"] = dict()  # dict containing the daemons
        instance_dictionaries["strategies"] = dict()  # objects which perform the calculus
        instance_dictionaries["aggregators"] = dict()  # a mono-energy sub-environment which favours self-consumption
        instance_dictionaries["agents"] = dict()  # it represents an economic agent, and is attached to, in particular, a contract
        instance_dictionaries["contracts"] = dict()  # dict containing the different contracts
        instance_dictionaries["devices"] = dict()  # dict containing the devices
        instance_dictionaries["forecasters"] = dict()  # dict containing the forecasters
        instance_dictionaries["dataloggers"] = dict()  # dict containing the dataloggers
        instance_dictionaries["graph_options"] = dict()  # dict containing the graph options

        self._catalog.add("dictionaries", instance_dictionaries)  # a sub-category of the catalog where are available all the elments constituting the model

        self._used_names = []  # this list contains the catalog name of all elements
        # It avoids to erase inadvertently pre-defined elements

        self._aggregator_order = []  # this list allows to know which aggregator have to be run first according to the converters

        self.__class__.ref_world = self  # set world as a global variable used later to instantiate objects

        self._catalog.add("incompatibility", False)  # a flag indicating if a second round is needed

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

        self._catalog.add("start_date", start_date)  # the start date in datetime format
        self._catalog.add("physical_time", start_date)  # physical time in seconds
        self._catalog.add("simulation_time", 0)  # simulation time in iterations

        self._catalog.add("time_step", time_step_value)  # value of a time step, used to adapt hourly-defined profiles
        self._timestep_value = timedelta(hours=time_step_value)
        self._time_limit = time_limit  # the number of the last iteration
        self._catalog.add("time_limit", time_limit)

    # ##########################################################################################
    # options

    def complete_message(self, additional_element: str, default_value=0):  # this function adds more element in the message exchanged between devices, contracts and aggregators
        # this new element requires to modify the related device, contract and strategy subclasses to have some effect
        MessagesManager.complete_all_messages(additional_element, default_value)

    # ##########################################################################################
    # modelling

    def register_nature(self, nature):  # definition of natures dictionary
        if nature.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{nature.name} already in use")

        for element_name, default_value in MessagesManager.added_information.items():  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{nature.name}.{element_name}", default_value)

        self._catalog.natures[nature.name] = nature
        self._used_names.append(nature.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_daemon(self, daemon):  # link a daemon with a world (and its catalog)
        if daemon.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{daemon.name} already in use")

        self._catalog.daemons[daemon.name] = daemon  # registering the daemon in the dedicated dictionary
        self._used_names.append(daemon.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_strategy(self, strategy):  # definition of the strategy
        if strategy.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{strategy.name} already in use")

        self._catalog.strategies[strategy.name] = strategy  # registering the aggregator in the dedicated dictionary
        self._used_names.append(strategy.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_agent(self, agent):  # method connecting one agent to the world
        if agent.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{agent.name} already in use")

        for element_name, default_value in MessagesManager.added_information.items():  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{agent.name}.{element_name}", default_value)

        if agent.superior:  # if the agent has a superior
            self._catalog.agents[agent.superior]._owned_agents_name.append(agent)

        self._catalog.agents[agent.name] = agent  # registering the agent in the dedicated dictionary
        self._used_names.append(agent.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_contract(self, contract):
        if contract.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{contract.name} already in use")

        for element_name, default_value in MessagesManager.added_information.items():  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{contract.name}.{element_name}", default_value)

        self._catalog.contracts[contract.name] = contract  # registering the contract in the dedicated dictionary
        self._used_names.append(contract.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing   
        
    def register_aggregator(self, aggregator):  # method connecting one aggregator to the world
        if aggregator.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{aggregator.name} already in use")

        for element_name, default_value in MessagesManager.added_information.items():  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{aggregator.name}.{element_name}", default_value)

        if aggregator.superior:  # if the aggregator has a superior
            aggregator.superior._subaggregators.append(aggregator)

        self._catalog.aggregators[aggregator.name] = aggregator  # registering the aggregator in the dedicated dictionary
        self._used_names.append(aggregator.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_forecaster(self, forecaster):
        if forecaster.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{forecaster.name} already in use")

        self._catalog.forecasters[forecaster.name] = forecaster  # registering the _forecaster in the dedicated dictionary
        self._used_names.append(forecaster.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_device(self, device):  # method connecting one device to the world
        if device.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{device.name} already in use")

        # checking if the agent is defined correctly
        if device._agent.name not in self._catalog.agents:  # if the specified agent does not exist
            raise WorldException(f"{device._agent.name} does not exist")

        for element_name, default_value in MessagesManager.added_information.items():  # for all new elements, an entry is created in the catalog
            self._catalog.add(f"{device.name}.{element_name}", default_value)

        for nature in device.natures:
            device._natures[nature]["aggregator"].add_device(device.name)  # adding the device name to its aggregator list of devices

        self._catalog.devices[device.name] = device  # registering the device in the dedicated dictionary
        self._used_names.append(device.name)  # adding the name to the list of used names

    def register_datalogger(self, datalogger):  # link a datalogger with a world (and its catalog)
        if datalogger.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{datalogger.name} already in use")

        self._catalog.dataloggers[datalogger.name] = datalogger  # registering the datalogger in the dedicated dictionary
        self._used_names.append(datalogger.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

    def register_graph_option(self, graph_option):  # link a GraphOptions with a world (and its catalog)
        if graph_option.name in self._used_names:  # checking if the name is already used
            raise WorldException(f"{graph_option.name} already in use")

        self._catalog.graph_options[graph_option.name] = graph_option  # registering the GraphOptions in the dedicated dictionary
        self._used_names.append(graph_option.name)  # adding the name to the list of used names
        # used_name is a general list: it avoids erasing

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

    def _identify_independent_aggregators(self) -> List:
        # first, we identify all the highest rank aggregators, who are the sole being called directly by world
        independent_aggregators_list = []
        for aggregator in self._catalog.aggregators.values():
            if not aggregator.superior:
                independent_aggregators_list.append(aggregator)

        return independent_aggregators_list

    def _identify_independent_agents(self) -> List:
        independent_agent_list = []  # a list containing all the independant agents
        for agent in self._catalog.agents.values():
            if not agent.superior:  # if the agent has no superior, it is added to the list of independant agents
                independent_agent_list.append(agent)

        return independent_agent_list

    def _clean_up(self):
        """
        Memory cleaning at the end of the run.
        Returns
        -------

        """
        self.catalog.remove("dictionaries")  # --> circular reference here
        gc.collect()

    def start(self, verbose=True, exogen_instruction: Callable = None):
        """

        Parameters
        ----------
        verbose: Bool, if True, gives indications on the progress of a run
        exogen_instruction: Callable,

        Returns
        -------

        """
        self._check()  # check if everything is fine in world definition

        if verbose:
            print(f"Start of the run named {self.name}.\n")

        independent_aggregators_list = self._identify_independent_aggregators()

        independent_agents_list = self._identify_independent_agents()

        for datalogger in self._catalog.dataloggers.values():
            datalogger.initial_operations()

        # Resolution
        for i in range(0, self.time_limit, 1):

            # ###########################
            # Beginning of the turn
            # ###########################

            if verbose:
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

            self._catalog.set("incompatibility", False)  # the flag indicating if a second round of decision is needed due to multi-energy devices

            if exogen_instruction:  # facultative instruction needed for a specific need
                exogen_instruction()

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

            # multi-energy devices management
            # as multi-energy devices state depends on different aggreators, a second round of distribution is performed in case of an incompability
            # multi-energy devices update their balances first and correct potential incompatibilities
            for device in self._catalog.devices.values():
                device.second_update()

            # aggregators then check if everything is fine and correct potential problems
            for aggregator in independent_aggregators_list:
                aggregator.check()
                # the method is recursive

            if self._catalog.get("incompatibility"):  # if a second round is needed
                for aggregator in independent_aggregators_list:  # aggregators are called according to the predefined order
                    aggregator.ask()  # aggregators make local balances and then publish their needs (both in demand and in offer)
                for aggregator in independent_aggregators_list:  # aggregators are called according to the predefined order
                    aggregator.distribute()  # aggregators make local balances and then publish their needs (both in demand and in offer)

            # ###########################
            # End of the turn
            # ###########################

            # devices update their state according to the quantity of energy received/given
            for device in self._catalog.devices.values():
                device.react()
                device.make_balances()

            # balance phase at the aggregator level
            for aggregator in independent_aggregators_list:  # aggregators are called according to the predefined order
                aggregator.make_balances()  # aggregators make their final balances of money anf energy
                # the method is recursive

            # agent report what happened to their potential owner (i.e to another agent)
            for agent in independent_agents_list:
                agent.report()

            # data exporting
            for datalogger in self._catalog.dataloggers.values():
                datalogger.launch()

            if exogen_instruction:  # facultative instruction needed for a specific need
                exogen_instruction(self)

            # time update
            self._update_time()

            # daemons activation
            for daemon in self._catalog.daemons.values():
                daemon.launch()

            if verbose:
                print()

        # end of the run
        if verbose:
            print("writing results")

        for datalogger in self._catalog.dataloggers.values():
            datalogger.final_process()
            datalogger.final_export()

        for daemon in self._catalog.daemons.values():
            daemon.final_process()

        if verbose:
            print("Done")

        self._clean_up()

        # reinitialize random state
        setstate(self._random_state)

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


