# # # # # TODO get_subclasses et subclasses_dictionary
# # # # # from importlib import import_module  # this library allows to import modules defined as str
# # # # # import inspect
# # # # #
# # # # # from src.tools.Utilities import list_files_and_folders
# # # # #
# # # # #
# # # # # class SubclassesInstantiationException(Exception):
# # # # #     def __init__(self, message):
# # # # #         super().__init__(message)
# # # # #
# # # # #
# # # # #
# # # # # subclasses_dictionary = {}  # a dictionary containing all the subclasses
# # # # #
# # # # # classes_concerned = list_files_and_folders("lib/Subclasses/")  # the list of all classes concerned by subclasses
# # # # #
# # # # # for class_name in classes_concerned:
# # # # #     subclasses_dictionary[class_name] = {}  # a sub-dictionary containing all the subclasses of the concerned class
# # # # #     class_directory = "lib/Subclasses/" + class_name  # the directory containing subclasses of one class
# # # # #     subclasses_list = list_files_and_folders(class_directory)  # list of all subclasses for a given class
# # # # #
# # # # #     for subclass_folder in subclasses_list:  # for each subclass
# # # # #         subclass_file = "lib.Subclasses." + class_name + "." + subclass_folder + "." + subclass_folder  # the file where the module is defined
# # # # #         if subclass_folder + ".py" in list_files_and_folders("lib/Subclasses/" + class_name + "/" + subclass_folder):
# # # # #             # subclass_module = import_module(subclass_file)  # we import the .py file
# # # # #             try:
# # # # #                 subclass_module = import_module(subclass_file)  # we import the .py file
# # # # #             except:
# # # # #                 raise SubclassesInstantiationException(f"An error occured during the instantiation of the module {subclass_file}.\n"
# # # # #                                                            "Please check that there is a module there and that it bears the same name as the directory. If it is not the case, please add one or remove the directory from the lib/subclasses directory.")
# # # # #             for subclass_name, subclass_class in inspect.getmembers(subclass_module):
# # # # #                 # print(subclass_name)
# # # # #                 # print(subclass_class)
# # # # #                 if inspect.isclass(subclass_class) and subclass_name != class_name:  # get back only the subclasses
# # # # #                     subclasses_dictionary[class_name][subclass_name] = subclass_class  # the subclass is added to the subclass list
# # # #
# # # #
# # # # # TODO getting the current world instance
# # # # # class MyClass:
# # # # #     def __init__(self, name):
# # # # #         self.name = name
# # # # #
# # # # #     def set_ref_world(self):
# # # # #         self.__class__.ref_world = self
# # # # #
# # # # # # Create instances of MyClass
# # # # # instance1 = MyClass("Instance 1")
# # # # # instance2 = MyClass("Instance 2")
# # # # #
# # # # # # Call set_ref_world on instance1
# # # # # instance1.set_ref_world()
# # # # #
# # # # # # Now the class attribute ref_world refers to instance1
# # # # # print(MyClass.ref_world.name)  # Output: Instance 1
# # # # # print(instance2.ref_world.name)
# # # # # # Call set_ref_world on instance2
# # # # # instance2.set_ref_world()
# # # # #
# # # # # # Now the class attribute ref_world refers to instance2
# # # # # print(MyClass.ref_world.name)
# # # #
# # # # # TODO testing the message manager class
# # # # # import copy
# # # # #
# # # # #
# # # # # class MessagesManager:
# # # # #     """
# # # # #     This class manages the messages exchanged between devices and aggregators through contracts.
# # # # #     """
# # # # #
# # # # #     # the minimum information needed everywhere
# # # # #     information_message = {"type": "", "aggregator": "", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": 0}
# # # # #     decision_message = {"aggregator": "", "quantity": 0, "price": 0}
# # # # #     # the information added to all messages
# # # # #     added_information = {}
# # # # #
# # # # #     def __init__(self):
# # # # #         self._specific_information_message = {}
# # # # #         self._specific_decision_message = {}
# # # # #
# # # # #     # ##########################################################################################
# # # # #     # Initialization
# # # # #     # ##########################################################################################
# # # # #
# # # # #     def complete_information_message(self, additional_element: str, default_value):
# # # # #         """
# # # # #         When complementary information is added in the messages exchanged between devices and aggregators,
# # # # #         this method updates the self._message attribute.
# # # # #
# # # # #         Parameters
# # # # #         ----------
# # # # #         additional_element: any parsable type of object
# # # # #         """
# # # # #         self._specific_information_message = {**self._specific_information_message, **{additional_element: default_value}}
# # # # #
# # # # #     def complete_decision_message(self, additional_element: str, default_value):
# # # # #         """
# # # # #         When complementary information is added in the messages exchanged between devices and aggregators,
# # # # #         this method updates the self._message attribute.
# # # # #
# # # # #         Parameters
# # # # #         ----------
# # # # #         additional_element: any parsable type of object
# # # # #         """
# # # # #         self._specific_decision_message = {**self._specific_decision_message, **{additional_element: default_value}}
# # # # #
# # # # #     def set_type(self, device_type: str):
# # # # #         self._specific_information_message["type"] = device_type
# # # # #
# # # # #     @classmethod
# # # # #     def complete_all_messages(cls, additional_element: str, default_value):
# # # # #         cls.information_message = {**cls.information_message, **{additional_element: default_value}}
# # # # #         cls.decision_message = {**cls.decision_message, **{additional_element: default_value}}
# # # # #         cls.added_information[additional_element] = default_value
# # # # #
# # # # #     # ##########################################################################################
# # # # #     # Dynamic behavior
# # # # #     # ##########################################################################################
# # # # #
# # # # #     def create_information_message(self):
# # # # #         general_message = copy.deepcopy(self.__class__.information_message)
# # # # #         specific_message = copy.deepcopy(self._specific_information_message)
# # # # #         information_message = {**general_message, **specific_message}
# # # # #
# # # # #         return information_message
# # # # #
# # # # #     def create_decision_message(self):
# # # # #         general_message = copy.deepcopy(self.__class__.decision_message)
# # # # #         specific_message = copy.deepcopy(self._specific_decision_message)
# # # # #         decision_message = {**general_message, **specific_message}
# # # # #
# # # # #         return decision_message
# # # #
# # # #
# # # # # TODO here we test how to send the information message to my code
# # # # # import sys
# # # # #
# # # # #
# # # # # formalism_message = {"t": "toto"}
# # # # # prediction_message = {"s": "sousou"}
# # # # # prices = {"b": "bousou"}
# # # # #
# # # # # # Sending the information message to the method
# # # # # path_to_interface = "C:/Users/y23hallo/PycharmProjects/Management_Strategy/Peacefulness_cases/Utilities/strategy_interface.py"
# # # # # pass_state = open(path_to_interface).read()
# # # # # sys.argv = ["pass_state", formalism_message, prediction_message, prices]
# # # # # exec(pass_state)
# # # #
# # # # # TODO here we test functions from DRL_Strategy_Utilities - from_tensor_to_dict
# # # # # import numpy as np
# # # # # import pandas as pd
# # # # # from collections import Counter
# # # # #
# # # # #
# # # # # # def from_tensor_to_dict(actions: np.ndarray, aggregators: list, agent: "Agent") -> dict:
# # # # # #     """
# # # # # #     This method is used to translate the actions taken by the A-C method into results understood by Peacefulness.
# # # # # #     The decision is to be stored.
# # # # # #     The return dict is under the format: {'Aggregator_1': {'Energy_Consumption': , 'Energy_Production': ...}, ...}
# # # # # #     """
# # # # # #     list_of_columns = []
# # # # # #     number_of_aggregators, number_of_actions = actions.shape
# # # # # #
# # # # # #     if number_of_aggregators != len(aggregators):
# # # # # #         raise Exception("The number of actions taken by the RL does not correspond to the number of aggregators in the MEG")
# # # # # #
# # # # # #     # Getting relevant info from the peacefulness_grid class considered for the RL agent
# # # # # #     agent_grid_topology = agent.grid.get_topology  # the return of the get_topology method
# # # # # #     agent_standard_devices = agent.grid.get_standard  # the return of the get_standard method
# # # # # #     agent_storage_devices = agent.grid.get_storage  # the return of the get_storage method
# # # # # #
# # # # # #     # Finding the columns related to energy exchanges
# # # # # #     exchange_options = Counter(item for tup in agent_grid_topology for item in tup[:2])
# # # # # #     exchange_list = []
# # # # # #     for index in range(exchange_options.most_common(1)[0][1]):
# # # # # #         name = "Energy_Exchange_{}".format(index + 1)
# # # # # #         exchange_list.append(name)
# # # # # #
# # # # # #     # Finding the other columns
# # # # # #     condition = number_of_actions - exchange_options.most_common(1)[0][1]
# # # # # #     if condition == 3:  # presence of energy consumers, production and storage
# # # # # #         list_of_columns.extend(["Energy_Consumption", "Energy_Production", "Energy_Storage"])
# # # # # #     elif condition == 2:  # presence of either energy consumers/production, consumers/storage or production/storage
# # # # # #         if max(agent_storage_devices.values()) == 0:  # presence of only energy consumers & production
# # # # # #             list_of_columns.extend(["Energy_Consumption", "Energy_Production"])
# # # # # #         else:
# # # # # #             if actions[0][0] < 0:  # presence of only energy production & storage
# # # # # #                 list_of_columns.extend(["Energy_Production", "Energy_Storage"])
# # # # # #             else:  # presence of only energy consumers & storage
# # # # # #                 list_of_columns.extend(["Energy_Consumption", "Energy_Storage"])
# # # # # #     elif condition == 1:  # presence of either energy consumers or energy production or energy storage
# # # # # #         if max(agent_storage_devices.values()) != 0:  # presence of only energy storage
# # # # # #             list_of_columns.extend(["Energy_Storage"])
# # # # # #         else:
# # # # # #             if actions[0][0] < 0:  # presence of only energy production
# # # # # #                 list_of_columns.extend(["Energy_Production"])
# # # # # #             else:  # presence of only energy consumers
# # # # # #                 list_of_columns.extend(["Energy_Consumption"])
# # # # # #     elif condition == 0:  # we only manage the energy exchanges between aggregators
# # # # # #         print("Attention, the MEG in question consists of only energy exchangers aggregators !")
# # # # # #
# # # # # #     list_of_columns.extend(exchange_list)
# # # # # #
# # # # # #     # First we get a dataframe from the actions tensor or vector
# # # # # #     actions_to_dataframe = pd.DataFrame(
# # # # # #                                         data=actions,
# # # # # #                                         index=aggregators,
# # # # # #                                         columns=list_of_columns
# # # # # #                                         )
# # # # # #     # We then get a dict from the dataframe
# # # # # #     actions_dict = actions_to_dataframe.to_dict()
# # # # # #
# # # # # #     # Inverting the dict - to get the aggregators.names as keys.
# # # # # #     resulting_dict = {
# # # # # #         key: {k: v[key] for k, v in actions_dict.items()}
# # # # # #         for key in actions_dict[next(iter(actions_dict))].keys()
# # # # # #     }
# # # # # #
# # # # # #     return resulting_dict
# # # # #
# # # # # #
# # # # # dummy_actions = np.array([[500, -100, 0, 150, 250], [0, -300, 100, -150, 0], [600, -700, -150, 0, -250]])
# # # # # aggregator_list = ["A1", "A2", "A3"]
# # # # # #
# # # # # # # print(exchange_options)
# # # # # # # print(exchange_options.most_common(1)[0][1])
# # # # # # # print(from_tensor_to_dict(dummy_actions, aggregator_list))
# # # # # # # print(dummy_actions[0][0])
# # # # # list_of_columns = []
# # # # # number_of_aggregators, number_of_actions = dummy_actions.shape
# # # # # #
# # # # # # if number_of_aggregators != len(aggregator_list):
# # # # # #     raise Exception("The number of actions taken by the RL does not correspond to the number of aggregators in the MEG")
# # # # # #
# # # # # # Getting relevant info from the peacefulness_grid class considered for the agent
# # # # # agent_grid_topology = []  # the return of the get_topology method
# # # # # agent_standard_devices = {"A1": 10, "A2": 5, "A3": 10}  # the return of the get_standard method
# # # # # agent_storage_devices = {"A1": 0, "A2": 6, "A3": 6}  # the return of the get_storage method
# # # # # #
# # # # # # Finding the columns related to energy exchanges
# # # # # if len(agent_grid_topology) != 0:
# # # # #     exchange_options = Counter(item for tup in agent_grid_topology for item in tup[:2])
# # # # #     exchange_list = []
# # # # #     for index in range(exchange_options.most_common(1)[0][1]):
# # # # #         name = "Energy_Exchange_{}".format(index + 1)
# # # # #         exchange_list.append(name)
# # # # #     number_of_exchanges = exchange_options.most_common(1)[0][1]
# # # # # else:
# # # # #     number_of_exchanges = 0
# # # # # #
# # # # # # Finding the other columns
# # # # # condition = number_of_actions - number_of_exchanges
# # # # # if condition == 3:  # presence of energy consumers, production and storage
# # # # #     list_of_columns.extend(["Energy_Consumption", "Energy_Production", "Energy_Storage"])
# # # # # elif condition == 2:  # presence of either energy consumers/production, consumers/storage or production/storage
# # # # #     if max(agent_storage_devices.values()) == 0:  # presence of only energy consumers & production
# # # # #         list_of_columns.extend(["Energy_Consumption", "Energy_Production"])
# # # # #     else:
# # # # #         if dummy_actions[0][0] < 0:  # presence of only energy production & storage
# # # # #             list_of_columns.extend(["Energy_Production", "Energy_Storage"])
# # # # #         else:  # presence of only energy consumers & storage
# # # # #             list_of_columns.extend(["Energy_Consumption", "Energy_Storage"])
# # # # # elif condition == 1:  # presence of either energy consumers or energy production or energy storage
# # # # #     if max(agent_storage_devices.values()) != 0:  # presence of only energy storage
# # # # #         list_of_columns.extend(["Energy_Storage"])
# # # # #     else:
# # # # #         if dummy_actions[0][0] < 0:  # presence of only energy production
# # # # #             list_of_columns.extend(["Energy_Production"])
# # # # #         else:  # presence of only energy consumers
# # # # #             list_of_columns.extend(["Energy_Consumption"])
# # # # # #
# # # # # list_of_columns.extend(exchange_list)
# # # # # # # print(list_of_columns)
# # # # # #
# # # # # # Transforming the tensor to a dataframe
# # # # # actions_to_dataframe = pd.DataFrame(
# # # # #                                         data=dummy_actions,
# # # # #                                         index=aggregator_list,
# # # # #                                         columns=list_of_columns
# # # # #                                         )
# # # # # # # # print(actions_to_dataframe)
# # # # # # #
# # # # # # Getting a dict from the dataframe
# # # # # actions_dict = actions_to_dataframe.to_dict()
# # # # # # print(actions_dict)
# # # # # #
# # # # # # Inverting the dict
# # # # # resulting_dict = {
# # # # #     key: {k: v[key] for k, v in actions_dict.items()}
# # # # #     for key in actions_dict[next(iter(actions_dict))].keys()
# # # # # }
# # # # # print(resulting_dict)
# # # # # # resulting_dict = {}
# # # # # # inter_dict = {}
# # # # # # for key in actions_dict.keys():
# # # # #     for subkey in actions_dict[key]:
# # # # #         resulting_dict[subkey] = {}
# # # # #         inter_dict[key] = actions_dict[key][subkey]
# # # # #         resulting_dict[subkey] = {**inter_dict}
# # # # #         # print(actions_dict[key][subkey])
# # # # #         if subkey in resulting_dict:
# # # # #             resulting_dict[subkey][key] = actions_dict[key][subkey]
# # # # #         resulting_dict[subkey] = {key: actions_dict[key][subkey]}
# # # # # print(resulting_dict)
# # # # # print(actions_dict.items())
# # # # # print(resulting_dict)
# # # #
# # # # # TODO here we test functions from DRL_Strategy_Utilities - extract_decision
# # # # # def extract_decision(decision_message: dict, aggregator: "Aggregator") -> list:
# # # # #     """
# # # # #     From the decisions taken by the RL agent concerning the whole multi-energy grid, we extract the decision related to the current aggregator.
# # # # #     """
# # # # #     consumption = {}
# # # # #     production = {}
# # # # #     storage = {}
# # # # #     exchange = {}
# # # # #
# # # # #     for element in decision_message.keys():  # TODO prices ?
# # # # #         if element == aggregator.name:
# # # # #             cold_startup = decision_message[element]
# # # # #             if "Energy_Consumption" in cold_startup:
# # # # #                 consumption = decision_message[element]["Energy_Consumption"]
# # # # #                 cold_startup.pop("Energy_Consumption")
# # # # #             if "Energy_Production" in cold_startup:
# # # # #                 production = decision_message[element]["Energy_Production"]
# # # # #                 cold_startup.pop("Energy_Production")
# # # # #             if "Energy_Storage" in cold_startup:
# # # # #                 storage = decision_message[element]["Energy_Storage"]
# # # # #                 cold_startup.pop("Energy_Storage")
# # # # #             exchange = cold_startup
# # # # #
# # # # #     return [consumption, production, storage, exchange]
# # # # #
# # # # #
# # # # # class Aggregator():
# # # # #     def __init__(self, name: str):
# # # # #         self.name = name
# # # # #
# # # # # aggregateur_1 = Aggregator("A1")
# # # # # aggregateur_2 = Aggregator("A2")
# # # # # aggregateur_3 = Aggregator("A3")
# # # # #
# # # # # print(extract_decision(resulting_dict, aggregateur_1))
# # # # # print(extract_decision(resulting_dict, aggregateur_2))
# # # # # print(extract_decision(resulting_dict, aggregateur_3))
# # # #
# # # # # TODO here we are testing the bottom-up phase of the strategy
# # # # # TODO - Proposition 1 - on publie tout le besoin en énergie des agrégateurs a.k.a AlwaysSatisfied
# # # # # # The information to be communicated to the DRL method in order to define the state of the grid
# # # # # prediction = self.call_to_forecast(aggregator)
# # # # # [min_price, max_price] = self._limit_prices(aggregator)
# # # # # formalism = [{}]
# # # # # # Getting the formalism message from the devices
# # # # # for device in aggregator.devices:
# # # # #     formalism.append(device._create_message())
# # # # #
# # # # # self.interface[0](min_price, max_price, prediction, formalism)  # communicating the formalism message, forecasting message and prices to the method
# # # # #
# # # # # from src.common.Messages import *
# # # # #
# # # # #
# # # # # class dummy_class():
# # # # #     messages_manager = MessagesManager()
# # # # #     messages_manager.complete_information_message("flexibility",[])  # -, indicates the level of flexibility on the latent concumption or production
# # # # #     messages_manager.complete_information_message("interruptibility", 0)  # -, indicates if the device is interruptible
# # # # #     messages_manager.complete_information_message("coming_volume",0)  # kWh, gives an indication on the latent consumption or production
# # # # #     messages_manager.set_type("standard")
# # # # #     information_message = messages_manager.create_information_message
# # # # #     decision_message = messages_manager.create_decision_message
# # # # #     information_keys = messages_manager.information_keys
# # # # #     decision_keys = messages_manager.decision_keys
# # # # #
# # # # #     def get_information(self):
# # # # #         return self.messages_manager.decision_message
# # # # #
# # # # #     def get_volume(self):
# # # # #         return self.messages_manager._specific_information_message
# # # #
# # # # #
# # # # # test = dummy_class()
# # # # # print(test.decision_keys)
# # # # # print(test.get_information())
# # # # #
# # # # # general_message = copy.deepcopy(test.messages_manager.__class__.information_message)
# # # # # print(general_message)
# # # # # specific_message = copy.deepcopy(test.messages_manager._specific_information_message)
# # # # # print(specific_message)
# # # # # information_message = {**general_message, **specific_message}
# # # # # print(information_message)
# # # # # from src.tools.DRL_Strategy_utilities import *
# # # # #
# # # # #
# # # # # cold_startup = {"A1": {"Energy_Consumption": {"D1": {"energy_minimum": 20, "energy_maximum": 150, "flexibility": [0], "interruptibility": 0, "coming_volume": 500},
# # # # #                                             "D2": {"energy_minimum": 20, "energy_maximum": 150, "flexibility": [], "interruptibility": 0, "coming_volume": 500},
# # # # #                                             "D3": {"energy_minimum": 20, "energy_maximum": 150, "flexibility": [], "interruptibility": 0, "coming_volume": 500}},
# # # # #                      "Energy_Production": {"D4": {"energy_minimum": -20, "energy_maximum": -150, "flexibility": [], "interruptibility": 0, "coming_volume": 0},
# # # # #                                            "D5": {"energy_minimum": -20, "energy_maximum": -150, "flexibility": [1], "interruptibility": 0, "coming_volume": -500},
# # # # #                                            "D6": {"energy_minimum": -20, "energy_maximum": -150, "flexibility": [], "interruptibility": 0, "coming_volume": -500}},
# # # # #                      "Energy_Storage": {"D7": {"energy_minimum": 20, "energy_maximum": 150, "state_of_charge": 0.45, "capacity": 20, "self_discharge_rate": 0.3, "efficiency": 0.95},
# # # # #                                         "D8": {"energy_minimum": -20, "energy_maximum": -150, "state_of_charge": 0.45, "capacity": 20, "self_discharge_rate": 0.3, "efficiency": 0.95},
# # # # #                                         "D9": {"energy_minimum": 20, "energy_maximum": 150, "state_of_charge": 0.45, "capacity": 20, "self_discharge_rate": 0.3, "efficiency": 0.95}},
# # # # #                      "Energy_Conversion": {"D10": {"energy_minimum": 20, "energy_maximum": 150, "efficiency": 0.65},
# # # # #                                            "D11": {"energy_minimum": -20, "energy_maximum": -150, "efficiency": 0.5},
# # # # #                                            "D12": {"energy_minimum": 20, "energy_maximum": 150, "efficiency": 0.8}}
# # # # #                      }
# # # # #               }
# # # # #
# # # # # cold_startup = mutualize_formalism_message(cold_startup)
# # # # # print(cold_startup)
# # # #
# # # # # # Preparing the dict
# # # # # return_dict = {}
# # # # # inter_dict = {}
# # # # # consumption_dict = {}
# # # # # production_dict = {}
# # # # # storage_dict = {}
# # # # # conversion_dict = {}
# # # # # for aggregator_name in cold_startup.keys():
# # # # #     inter_dict = {**cold_startup[aggregator_name]}
# # # # #     for key in inter_dict.keys():
# # # # #         consumption_dict = {**consumption_dict, **inter_dict["Energy_Consumption"]}
# # # # #         production_dict = {**production_dict, **inter_dict["Energy_Production"]}
# # # # #         storage_dict = {**storage_dict, **inter_dict["Energy_Storage"]}
# # # # #         conversion_dict = {**conversion_dict, **inter_dict["Energy_Conversion"]}
# # # #
# # # # # # Energy consumption and production associated dict of values
# # # # # energy_min = []
# # # # # energy_max = []
# # # # # flexibility = []
# # # # # interruptibility = []
# # # # # coming_volume = []
# # # # #
# # # # # for element in [consumption_dict, production_dict]:
# # # # #     for key in element:
# # # # #         for subkey in element[key]:
# # # # #             if subkey == 'energy_minimum':
# # # # #                 energy_min.append(element[key][subkey])
# # # # #             elif subkey == 'energy_maximum':
# # # # #                 energy_max.append(element[key][subkey])
# # # # #             elif subkey == 'flexibility':
# # # # #                 flexibility.extend(element[key][subkey])
# # # # #             elif subkey == 'interruptibility':
# # # # #                 interruptibility.append(element[key][subkey])
# # # # #             else:
# # # # #                 coming_volume.append(element[key][subkey])
# # # # #     if element == consumption_dict:
# # # # #         return_dict = {
# # # # #             "Energy_Consumption": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
# # # # #                                    'flexibility': min(flexibility), 'interruptibility': min(interruptibility),
# # # # #                                    'coming_volume': sum(coming_volume)}}
# # # # #         energy_min.clear()
# # # # #         energy_max.clear()
# # # # #         flexibility.clear()
# # # # #         interruptibility.clear()
# # # # #         coming_volume.clear()
# # # # #     else:
# # # # #         return_dict = {**return_dict, **{
# # # # #             "Energy_Production": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
# # # # #                                   'flexibility': min(flexibility), 'interruptibility': min(interruptibility),
# # # # #                                   'coming_volume': sum(coming_volume)}}
# # # # #                                            }
# # # # # # Energy storage associated dict of values
# # # # # energy_min = []
# # # # # energy_max = []
# # # # # state_of_charge = []
# # # # # capacity = []
# # # # # self_discharge_rate = []
# # # # # efficiency = []
# # # # #
# # # # # for key in storage_dict:
# # # # #     for subkey in storage_dict[key]:
# # # # #         if subkey == 'energy_minimum':
# # # # #             energy_min.append(storage_dict[key][subkey])
# # # # #         elif subkey == 'energy_maximum':
# # # # #             energy_max.append(storage_dict[key][subkey])
# # # # #         elif subkey == 'state_of_charge':
# # # # #             state_of_charge.append(storage_dict[key][subkey])
# # # # #         elif subkey == 'capacity':
# # # # #             capacity.append(storage_dict[key][subkey])
# # # # #         elif subkey == 'self_discharge_rate':
# # # # #             self_discharge_rate.append(storage_dict[key][subkey])
# # # # #         else:
# # # # #             efficiency.append(storage_dict[key][subkey])
# # # # #
# # # # # return_dict = {**return_dict, **{
# # # # #             "Energy_Storage": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
# # # # #                                'state_of_charge': sum(state_of_charge)/len(state_of_charge), 'capacity': sum(capacity)/len(capacity),
# # # # #                                'self_discharge_rate': sum(self_discharge_rate)/len(self_discharge_rate), 'efficiency': sum(efficiency)/len(efficiency)}}
# # # # #                                            }
# # # # # # Energy conversion associated dict of values
# # # # # energy_min = []
# # # # # energy_max = []
# # # # # efficiency = []
# # # # #
# # # # # for key in conversion_dict:
# # # # #     for subkey in conversion_dict[key]:
# # # # #         if subkey == 'energy_minimum':
# # # # #             energy_min.append(conversion_dict[key][subkey])
# # # # #         elif subkey == 'energy_maximum':
# # # # #             energy_max.append(conversion_dict[key][subkey])
# # # # #         else:
# # # # #             efficiency.append(conversion_dict[key][subkey])
# # # # #
# # # # # return_dict = {**return_dict, **{
# # # # #             "Energy_Conversion": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max), 'efficiency': sum(efficiency)/len(efficiency)}}}
# # # # #
# # # # # print(return_dict)
# # # #
# # # # # TODO here we test some functionalities in the top-down-phase of the DRL strategy
# # # # # import numpy as np
# # # # # # my_aggregator = "A1"
# # # # # # my_list = []
# # # # # # dumb_grid_topology = [("A1", "A2", 0.45), ("A1", "A4", 1), ("A3", "A2", 1), ("A4", "A2", 0.85)]
# # # # # # for element in dumb_grid_topology:
# # # # # #     if my_aggregator in element:
# # # # # #         print(element[2])
# # # # # #         my_list.append(dumb_grid_topology.index(element))
# # # # # # print(my_list)
# # # # # a = 5
# # # # # b = 5
# # # # # if np.sign(a) == np.sign(b):
# # # # #     print(True)
# # # # # else:
# # # # #     print(False)
# # # # #
# # # # # a = abs(-9)
# # # # # print(a)
# # # # # class aggregator:
# # # # #     def __init__(self, name: str):
# # # # #         self.name = name
# # # # #
# # # # # my_aggregator = aggregator('Aggregator_1')
# # # # #
# # # # #
# # # # # decision_message = {'Aggregator_1': {'Energy_Consumption': 400, 'Energy_Production': -320, 'Energy_Storage': 0,
# # # # # 'Energy_Exchange_1': 120, 'Energy_Exchange_2': -60, 'Energy_Exchange_3': 20},
# # # # # 'Aggregator_2': {'Energy_Consumption': 0, 'Energy_Production': 0, 'Energy_Storage': 110, 'Energy_Exchange_1': -120,
# # # # # 'Energy_Exchange_2': 0, 'Energy_Exchange_3': 10}, 'Aggregator_3': {'Energy_Consumption': 350,
# # # # # 'Energy_Production': -630, 'Energy_Storage': 250, 'Energy_Exchange_1': 0, 'Energy_Exchange_2': 60,
# # # # # 'Energy_Exchange_3': -30}}
# # # # #
# # # # # if my_aggregator.name in decision_message:
# # # # #     cold_startup = decision_message[my_aggregator.name]
# # # # #     if "Energy_Consumption" in cold_startup:
# # # # #         consumption = decision_message[my_aggregator.name]["Energy_Consumption"]
# # # # #         cold_startup.pop("Energy_Consumption")
# # # # #     if "Energy_Production" in cold_startup:
# # # # #         production = decision_message[my_aggregator.name]["Energy_Production"]
# # # # #         cold_startup.pop("Energy_Production")
# # # # #     if "Energy_Storage" in cold_startup:
# # # # #         storage = decision_message[my_aggregator.name]["Energy_Storage"]
# # # # #         cold_startup.pop("Energy_Storage")
# # # # #     exchange = cold_startup
# # # # # print(consumption)
# # # # # print(production)
# # # # # print(storage)
# # # # # print(exchange)
# # # #
# # # # # TODO here we test top-down phase functionalities
# # # # # def distribute_to_standard_devices(device_list: list, energy_accorded: float, energy_price: float, world: "World", aggregator: "Aggregator", message: dict) -> float:
# # # # #     """
# # # # #     This function is used for energy distribution and billing for standard devices managed by the aggregator.
# # # # #     It concerns the energy producers and consumers.
# # # # #     The minimum energy demands/offers are served first, the rest is then distributed equally over non-urgent devices.
# # # # #     """
# # # # #     distribution_decision = {}
# # # # #     energy_difference = energy_accorded
# # # # #     urgent_devices = []
# # # # #     non_urgent_devices = []
# # # # #     for device in device_list:
# # # # #         Emin = world.catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
# # # # #         Emax = world.catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
# # # # #
# # # # #         # the minimum energy demand/offer is served first
# # # # #         if abs(energy_accorded) > abs(Emin):  # to take into account both negative and positive signs
# # # # #             distribution_decision[device.name] = Emin
# # # # #             energy_accorded -= Emin
# # # # #         elif 0 < abs(energy_accorded) < abs(Emin):  # to take into account both negative and positive signs
# # # # #             distribution_decision[device.name] = energy_accorded
# # # # #             energy_accorded = 0
# # # # #
# # # # #         # the urgency of the demand/offer is determined
# # # # #         if Emin == Emax:  # the energy demand/offer is urgent
# # # # #             urgent_devices.append(device)
# # # # #         else:  # the energy demand/offer is not a priority
# # # # #             non_urgent_devices.append(device)
# # # # #
# # # # #     for device in urgent_devices:  # the urgent energy demands/offers are served
# # # # #         message['quantity'] = distribution_decision[device.name]
# # # # #         message["price"] = energy_price
# # # # #         world.catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #
# # # # #     for device in non_urgent_devices:  # the remaining energy is equally distributed over the rest of the devices
# # # # #         message['quantity'] = distribution_decision[device.name] + energy_accorded / len(non_urgent_devices)
# # # # #         message["price"] = energy_price
# # # # #         world.catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #
# # # # #     maximum_energy_difference = energy_difference - energy_accorded
# # # # #
# # # # #     return maximum_energy_difference
# # # # # from src.tools.DRL_Strategy_utilities import return_sign
# # # #
# # # #
# # # # # def distribute_to_storage_devices(storage_list: list, energy_accorded_to_storage: float, buying_price: float, selling_price: float, world: "World", aggregator: "Aggregator", message: dict):
# # # # #     """
# # # # #     This function is used for energy distribution and billing for energy storage systems managed by the aggregator.
# # # # #     The devices who have needs that encounter the average needs are to stay idle.
# # # # #     The minimum energy demands/offers are served first, the rest is then distributed equally over non-urgent devices.
# # # # #     """
# # # # #     distribution_decision = {}
# # # # #     non_urgent_storage = []
# # # # #     for storage in storage_list:
# # # # #         Emax = world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
# # # # #         Emin = world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
# # # # #         sign_min = return_sign(Emin, energy_accorded_to_storage)
# # # # #         if not sign_min:  # the device wants the opposite of the average want of the energy storage systems managed by the aggregator, thus it will be idle
# # # # #             message["quantity"] = 0
# # # # #             message["price"] = 0
# # # # #             world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #         else:  # the device wants the same as the average want of the energy storage systems managed by the aggregator
# # # # #             if abs(energy_accorded_to_storage) > abs(Emin):  # to take into account both negative and positive signs
# # # # #                 distribution_decision[storage.name] = Emin
# # # # #                 energy_accorded_to_storage -= Emin
# # # # #             elif 0 < abs(energy_accorded_to_storage) < abs(Emin):  # to take into account both negative and positive signs
# # # # #                 distribution_decision[storage.name] = energy_accorded_to_storage
# # # # #                 energy_accorded_to_storage = 0
# # # # #             # the urgency is determined
# # # # #             if Emin == Emax:  # the energy storage system has urgency
# # # # #                 message["quantity"] = distribution_decision[storage.name]
# # # # #                 if Emin < 0:  # the energy storage system wants to sell its energy
# # # # #                     message["price"] = selling_price
# # # # #                 else:  # the energy storage system wants to buy energy
# # # # #                     message["price"] = buying_price
# # # # #                 world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #             else:
# # # # #                 sign_max = return_sign(Emax, energy_accorded_to_storage)
# # # # #                 if not sign_max:
# # # # #                     message["quantity"] = distribution_decision[storage.name]
# # # # #                     if Emin < 0:  # the energy storage system wants to sell its energy
# # # # #                         message["price"] = selling_price
# # # # #                     else:  # the energy storage system wants to buy energy
# # # # #                         message["price"] = buying_price
# # # # #                     world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #                 else:
# # # # #                     non_urgent_storage.append(storage)
# # # # #
# # # # #     for storage in non_urgent_storage:  # the remaining energy is equally distributed over the rest of the devices
# # # # #         Emin = world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
# # # # #         message["quantity"] = distribution_decision[storage.name] + energy_accorded_to_storage / len(non_urgent_storage)
# # # # #         if Emin < 0:  # the energy storage system wants to sell its energy
# # # # #             message["price"] = selling_price
# # # # #         else:  # the energy storage system wants to buy energy
# # # # #             message["price"] = buying_price
# # # # #         world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # # aggregator_name = "A1"
# # # # #
# # # # # dummy_grid_topology = [('A1', 'A2', -35, 25, 1), ('A1', 'A3', 25, 45, 0.85), ('A2', 'A3', 'A4', -12, 87, 0.6, 0.45), ('A3', 'A1', 'A2', 'A4', -59, 64, 0.5, 0.45, 0.65)]
# # # # # energy_accorded_to_exchanges = {"Energy_Exchange_1": 0, "Energy_Exchange_2": 30, "Energy_Exchange_3": 12}  # for A4
# # # # # converters_list = {'device_1': {"energy_minimum": -12, "energy_nominal": 25, "energy_maximum": 87}, 'device_2': {"energy_minimum": -59, "energy_nominal": 7, "energy_maximum": 64}}  # for A1, and it is the device objects not only their names
# # # #
# # # # # def distribute_energy_exchanges(world: "World", catalog: "Catalog", aggregator: "Aggregator", energy_accorded_to_exchange: dict, grid_topology: list, converter_list: dict, buying_price: float, selling_price: float, message: dict):
# # # # #     """
# # # # #     This function computes the energy exchanges (direct ones and with conversion systems).
# # # # #     Since we don't know how are which decision corresponds to which energy exchange, we first verify if the decision is bound by the min and max.
# # # # #     Then we look for the one closest to the nominal.
# # # # #     May be subject to change if finally we output the matrix of the grid's topology as in the input to the model.
# # # # #     """
# # # # #     aggregator_energy_exchanges_from_grid_topology = []
# # # # #     for tup in grid_topology:
# # # # #         if aggregator.name in tup:
# # # # #             aggregator_energy_exchanges_from_grid_topology.append(tup)
# # # # #
# # # # #     aggregator_energy_exchanges_from_RL_decision = []
# # # # #     cold_startup = {**energy_accorded_to_exchange}
# # # # #     for key, value in energy_accorded_to_exchange.items():
# # # # #         if value != 0:
# # # # #             aggregator_energy_exchanges_from_RL_decision.append(value)
# # # # #             cold_startup.pop(key)
# # # # #     if len(cold_startup) == len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision):
# # # # #         for key, value in cold_startup.items():
# # # # #             aggregator_energy_exchanges_from_RL_decision.append(value)
# # # # #     else:
# # # # #         for i in range(len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision)):
# # # # #             aggregator_energy_exchanges_from_RL_decision.append(0)
# # # # #
# # # # #     if len(aggregator_energy_exchanges_from_grid_topology) != len(aggregator_energy_exchanges_from_RL_decision):
# # # # #         raise Exception(
# # # # #             f"The {aggregator.name}'s occurrences in energy exchanges don't match the corresponding number of decisions taken by the RL !")
# # # # #
# # # # #     # Quantities concerning energy conversion systems
# # # # #     decision_message = {}
# # # # #     print("The aggregator does not exchange with its subaggregators nor with its superior aggregator !")
# # # # #     for device in converter_list:
# # # # #         decision_message[device] = []
# # # # #         for element in aggregator_energy_exchanges_from_RL_decision[:]:
# # # # #             if converter_list[device]["energy_minimum"] < element < converter_list[device]["energy_maximum"]:
# # # # #                 decision_message[device].append(element)
# # # # #         if len(decision_message[device]) > 1:
# # # # #             distance = {}
# # # # #             for element in decision_message[device]:
# # # # #                 distance[element] = abs(element - converter_list[device]["energy_nominal"])
# # # # #             decision_message[device] = min(distance, key=distance.get)
# # # # #             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
# # # # #         else:
# # # # #             decision_message[device] = decision_message[device][0]
# # # # #             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
# # # # #
# # # # #         message["quantity"] = decision_message[device]
# # # # #         if decision_message[device] < 0:  # energy selling
# # # # #             message["price"] = selling_price
# # # # #         else:  # energy buying
# # # # #             message["price"] = buying_price
# # # # #         world.catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #
# # # # #     # Quantities concerning sub-aggregators
# # # # #     if aggregator_energy_exchanges_from_RL_decision:
# # # # #         for subaggregator in aggregator.subaggregators:
# # # # #             decision_message[subaggregator.name] = []
# # # # #             quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
# # # # #             for element in aggregator_energy_exchanges_from_RL_decision[:]:
# # # # #                 if quantities_and_prices["energy_minimum"] < element < quantities_and_prices["energy_maximum"]:
# # # # #                     decision_message[subaggregator.name].append(element)
# # # # #                 if len(decision_message[subaggregator.name]) > 1:
# # # # #                     distance = {}
# # # # #                     for element in decision_message[subaggregator.name]:
# # # # #                         distance[element] = abs(element - quantities_and_prices["energy_nominal"])
# # # # #                     decision_message[subaggregator.name] = min(distance, key=distance.get)
# # # # #                     aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
# # # # #                 else:
# # # # #                     decision_message[subaggregator.name] = decision_message[subaggregator.name][0]
# # # # #                     aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
# # # # #
# # # # #             message["quantity"] = decision_message[subaggregator.name]
# # # # #             if decision_message[subaggregator.name] < 0:  # energy selling
# # # # #                 message["price"] = selling_price
# # # # #             else:  # energy buying
# # # # #                 message["price"] = buying_price
# # # # #             catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)
# # # #
# # # # # message = {"aggregator": "", "quantity": 0, "price": 0}
# # # # #
# # # # # buying_price = 0.45
# # # # # selling_price = 0.35
# # # # #
# # # # # grid_topology = [('A1', 'A2', -500, 500, 1), ('A3', 'A4', -350, 350, 1), ('A2', 'A3', -110, 75, 0.8),
# # # # #                  ('A1', 'A3', 'A4', -65, 50, 0.45, 0.55), ('A1', 'A4', 'A5', 'A6', -25, 35, 0.6, 0.5, 0.7)]
# # # # #
# # # # # energy_accorded_to_exchange = {"Energy_Exchange_1": -100, "Energy_Exchange_2": 15, "Energy_Exchange_3": 25}  # pour A1
# # # # #
# # # # # converter_list = {"device_1": {"energy_minimum": -65, "energy_nominal": 12, "energy_maximum": 50},
# # # # #                   "device_2": {"energy_minimum": -25, "energy_nominal": 20, "energy_maximum": 35}}  # pour A1
# # # # #
# # # # # aggregator_name = 'A1'
# # # # # aggregator_subaggregators = ['A2']
# # # # #
# # # # # # initializing
# # # # # energy_bought_inside = 0.0
# # # # # money_spent_inside = 0.0
# # # # # energy_sold_inside = 0.0
# # # # # money_earned_inside = 0.0
# # # # # energy_bought_outside = 0.0
# # # # # money_spent_outside = 0.0
# # # # # energy_sold_outside = 0.0
# # # # # money_earned_outside = 0.0
# # # # #
# # # # # aggregator_energy_exchanges_from_grid_topology = []
# # # # # for tup in grid_topology:
# # # # #     if aggregator_name in tup:
# # # # #         aggregator_energy_exchanges_from_grid_topology.append(tup)
# # # # #
# # # # # aggregator_energy_exchanges_from_RL_decision = []
# # # # # cold_startup = {**energy_accorded_to_exchange}
# # # # # for key, value in energy_accorded_to_exchange.items():
# # # # #     if value != 0:
# # # # #         aggregator_energy_exchanges_from_RL_decision.append(value)
# # # # #         cold_startup.pop(key)
# # # # # if len(cold_startup) == len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision):
# # # # #     for key, value in cold_startup.items():
# # # # #         aggregator_energy_exchanges_from_RL_decision.append(value)
# # # # # else:
# # # # #     for i in range(len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision)):
# # # # #         aggregator_energy_exchanges_from_RL_decision.append(0)
# # # # #
# # # # # if len(aggregator_energy_exchanges_from_grid_topology) != len(aggregator_energy_exchanges_from_RL_decision):
# # # # #     raise Exception(
# # # # #         f"The {aggregator_name}'s occurrences in energy exchanges don't match the corresponding number of decisions taken by the RL !")
# # # # #
# # # # # # Quantities concerning energy conversion systems
# # # # # decision_message = {}
# # # # # print("The aggregator does not exchange with its subaggregators nor with its superior aggregator !")
# # # # # for device in converter_list:
# # # # #     decision_message[device] = []
# # # # #     for element in aggregator_energy_exchanges_from_RL_decision[:]:
# # # # #         if converter_list[device]["energy_minimum"] < element < converter_list[device]["energy_maximum"]:
# # # # #             decision_message[device].append(element)
# # # # #     if len(decision_message[device]) > 1:
# # # # #         distance = {}
# # # # #         for element in decision_message[device]:
# # # # #             distance[element] = abs(element - converter_list[device]["energy_nominal"])
# # # # #         decision_message[device] = min(distance, key=distance.get)
# # # # #         aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
# # # # #     else:
# # # # #         decision_message[device] = decision_message[device][0]
# # # # #         aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
# # # # #
# # # # #     message["quantity"] = decision_message[device]
# # # # #     if decision_message[device] < 0:  # energy selling
# # # # #         message["price"] = selling_price
# # # # #         energy_sold_outside += abs(message["quantity"])
# # # # #         money_earned_outside += abs(message['quantity'] * message["price"])
# # # # #     else:  # energy buying
# # # # #         message["price"] = buying_price
# # # # #         energy_bought_outside += abs(message["quantity"])
# # # # #         money_spent_outside += abs(message['quantity'] * message["price"])
# # # # #     # world.catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #     print(message)
# # # # # # Quantities concerning sub-aggregators
# # # # # quantities_and_prices = {"energy_minimum": -500, "energy_nominal": -150, "energy_maximum": 500}
# # # # # if aggregator_energy_exchanges_from_RL_decision:
# # # # #     for subaggregator in aggregator_subaggregators:
# # # # #         decision_message[subaggregator] = []
# # # # #         # quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
# # # # #         for element in aggregator_energy_exchanges_from_RL_decision[:]:
# # # # #             if quantities_and_prices["energy_minimum"] < element < quantities_and_prices["energy_maximum"]:
# # # # #                 decision_message[subaggregator].append(element)
# # # # #             if len(decision_message[subaggregator]) > 1:
# # # # #                 distance = {}
# # # # #                 for element in decision_message[subaggregator]:
# # # # #                     distance[element] = abs(element - quantities_and_prices["energy_nominal"])
# # # # #                 decision_message[subaggregator] = min(distance, key=distance.get)
# # # # #                 aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator])
# # # # #             else:
# # # # #                 decision_message[subaggregator] = decision_message[subaggregator][0]
# # # # #                 aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator])
# # # # #
# # # # #         message["quantity"] = decision_message[subaggregator]
# # # # #         if decision_message[subaggregator] < 0:  # energy selling
# # # # #             message["price"] = selling_price
# # # # #             energy_bought_inside += abs(message["quantity"])
# # # # #             money_spent_inside += abs(message['quantity'] * message["price"])
# # # # #         else:  # energy buying
# # # # #             message["price"] = buying_price
# # # # #             energy_sold_inside += abs(message["quantity"])
# # # # #             money_earned_inside += abs(message['quantity'] * message["price"])
# # # # #         # catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #         print(message)
# # # #
# # # # # todo here we test functionalities of dataloggers in order to send the iteration results to the agent for reward calculation
# # # # # def distribute_energy_exchanges(catalog: "Catalog", aggregator: "Aggregator", energy_accorded_to_exchange: dict, grid_topology: list, converter_list: dict, buying_price: float, selling_price: float, message: dict) -> Tuple[float, float, float, float, float, float, float, float]:
# # # # #     """
# # # # #     This function computes the energy exchanges (direct ones and with conversion systems).
# # # # #     Since we don't know how do decisions correspond to energy exchanges, we first verify if they are bound by the min and max.
# # # # #     Then we look for the one closest to the nominal.
# # # # #     May be subject to change if finally we output the matrix of the grid's topology as in the input to the model.
# # # # #     """
# # # # #     # initializing
# # # # #     energy_bought_inside = 0.0
# # # # #     money_spent_inside = 0.0
# # # # #     energy_sold_inside = 0.0
# # # # #     money_earned_inside = 0.0
# # # # #     energy_bought_outside = 0.0
# # # # #     money_spent_outside = 0.0
# # # # #     energy_sold_outside = 0.0
# # # # #     money_earned_outside = 0.0
# # # # #
# # # # #     aggregator_energy_exchanges_from_grid_topology = []
# # # # #     for tup in grid_topology:
# # # # #         if aggregator.name in tup:
# # # # #             aggregator_energy_exchanges_from_grid_topology.append(tup)
# # # # #
# # # # #     aggregator_energy_exchanges_from_RL_decision = []
# # # # #     cold_startup = {**energy_accorded_to_exchange}
# # # # #     for key, value in energy_accorded_to_exchange.items():
# # # # #         if value != 0:
# # # # #             aggregator_energy_exchanges_from_RL_decision.append(value)
# # # # #             cold_startup.pop(key)
# # # # #     if len(cold_startup) == len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision):
# # # # #         for key, value in cold_startup.items():
# # # # #             aggregator_energy_exchanges_from_RL_decision.append(value)
# # # # #     else:
# # # # #         for i in range(len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision)):
# # # # #             aggregator_energy_exchanges_from_RL_decision.append(0)
# # # # #
# # # # #     if len(aggregator_energy_exchanges_from_grid_topology) != len(aggregator_energy_exchanges_from_RL_decision):
# # # # #         raise Exception(
# # # # #             f"The {aggregator.name}'s occurrences in energy exchanges don't match the corresponding number of decisions taken by the RL !")
# # # # #
# # # # #     # Quantities concerning energy conversion systems
# # # # #     decision_message = {}
# # # # #     print("The aggregator does not exchange with its subaggregators nor with its superior aggregator !")
# # # # #     for device in converter_list:
# # # # #         decision_message[device] = []
# # # # #         for element in aggregator_energy_exchanges_from_RL_decision[:]:
# # # # #             if converter_list[device]["energy_minimum"] <= element <= converter_list[device]["energy_maximum"]:
# # # # #                 decision_message[device].append(element)
# # # # #         if len(decision_message[device]) > 1:
# # # # #             distance = {}
# # # # #             for element in decision_message[device]:
# # # # #                 distance[element] = abs(element - converter_list[device]["energy_nominal"])
# # # # #             decision_message[device] = min(distance, key=distance.get)
# # # # #             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
# # # # #         else:
# # # # #             decision_message[device] = decision_message[device][0]
# # # # #             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
# # # # #
# # # # #         message["quantity"] = decision_message[device]
# # # # #         if decision_message[device] < 0:  # energy selling
# # # # #             message["price"] = selling_price
# # # # #             energy_sold_outside += abs(message["quantity"])
# # # # #             money_earned_outside += abs(message['quantity'] * message["price"])
# # # # #         else:  # energy buying
# # # # #             message["price"] = buying_price
# # # # #             energy_bought_outside += abs(message["quantity"])
# # # # #             money_spent_outside += abs(message['quantity'] * message["price"])
# # # # #         catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #
# # # # #     # Quantities concerning sub-aggregators
# # # # #     if aggregator_energy_exchanges_from_RL_decision:
# # # # #         for subaggregator in aggregator.subaggregators:
# # # # #             decision_message[subaggregator.name] = []
# # # # #             quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
# # # # #             print(f"top-down phase, quantities_and_prices: {quantities_and_prices}")
# # # # #             for element in aggregator_energy_exchanges_from_RL_decision[:]:
# # # # #                 print(element)
# # # # #                 if quantities_and_prices[0]["energy_minimum"] <= element <= quantities_and_prices[0]["energy_maximum"]:
# # # # #                     decision_message[subaggregator.name].append(element)
# # # # #                 if len(decision_message[subaggregator.name]) > 1:
# # # # #                     distance = {}
# # # # #                     for element in decision_message[subaggregator.name]:
# # # # #                         distance[element] = abs(element - quantities_and_prices["energy_nominal"])
# # # # #                     decision_message[subaggregator.name] = min(distance, key=distance.get)
# # # # #                     aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
# # # # #                 else:
# # # # #                     print(decision_message[subaggregator.name])
# # # # #                     decision_message[subaggregator.name] = decision_message[subaggregator.name][0]
# # # # #                     aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
# # # # #
# # # # #             message["quantity"] = decision_message[subaggregator.name]
# # # # #             if decision_message[subaggregator.name] < 0:  # energy selling
# # # # #                 message["price"] = selling_price
# # # # #                 energy_bought_inside += abs(message["quantity"])
# # # # #                 money_spent_inside += abs(message['quantity'] * message["price"])
# # # # #             else:  # energy buying
# # # # #                 message["price"] = buying_price
# # # # #                 energy_sold_inside += abs(message["quantity"])
# # # # #                 money_earned_inside += abs(message['quantity'] * message["price"])
# # # # #             catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #
# # # # #     return energy_bought_inside, money_spent_inside, energy_sold_inside, money_earned_inside, energy_bought_outside, money_spent_outside, energy_sold_outside, money_earned_outside
# # # # #
# # # #
# # # # # Emin = - 15.0
# # # # # energy_accorded_to_storage = 0.0
# # # # # distribution_decision = {}
# # # # # failed_to_satisfy = 0.0
# # # # # storage_name = "S1"
# # # # #
# # # # # if abs(energy_accorded_to_storage) > abs(Emin):  # to take into account both negative and positive signs
# # # # #     distribution_decision[storage_name] = Emin
# # # # #     energy_accorded_to_storage -= Emin
# # # # # elif 0 < abs(energy_accorded_to_storage) < abs(Emin):  # to take into account both negative and positive signs
# # # # #     distribution_decision[storage_name] = energy_accorded_to_storage
# # # # #     failed_to_satisfy += abs(abs(Emin) - abs(energy_accorded_to_storage))
# # # # #     energy_accorded_to_storage = 0
# # # # # else:
# # # # #     distribution_decision[storage_name] = 0.0
# # # # #     failed_to_satisfy += abs(Emin)
# # # # #
# # # # # print(energy_accorded_to_storage)
# # # # # print(distribution_decision)
# # # # # print(failed_to_satisfy)
# # # # # import numpy as np
# # # # # import pandas as pd
# # # # # from collections import Counter
# # # #
# # # #
# # # # # def from_tensor_to_dict(actions: np.ndarray, aggregators: list, agent: "Agent") -> List[dict, dict]:
# # # # #     """
# # # # #     This method is used to translate the actions taken by the A-C method into results understood by Peacefulness.
# # # # #     The decision is to be stored.
# # # # #     The return dict is under the format: {'Aggregator_1': {'Energy_Consumption': , 'Energy_Production': ...}, ...}
# # # # #     The dict concerning energy exchanges is also returned.
# # # # #     """
# # # # #     list_of_columns = []
# # # # #
# # # # #     # Getting relevant info from the peacefulness_grid class considered for the RL agent
# # # # #     agent_grid_topology = agent.grid.get_topology  # the return of the get_topology method
# # # # #     agent_storage_devices = agent.grid.get_storage  # the return of the get_storage method
# # # # #
# # # # #     # Grouping actions into ones related to energy exchanges and ones related to management of energy consumption, production and storage inside the aggregators
# # # # #     actions_related_to_aggregators = actions[:-len(agent_grid_topology)]
# # # # #     actions_related_to_exchange = actions[-len(agent_grid_topology):]
# # # # #
# # # # #     # Getting the dimensions of the dataframe
# # # # #     number_of_aggregators = len(aggregators)  # index of the dataframe
# # # # #     number_of_actions = int(len(actions_related_to_aggregators) / number_of_aggregators)  # number of columns
# # # # #     if number_of_actions == 3:  # presence of energy consumers, production and storage
# # # # #         list_of_columns.extend(["Energy_Consumption", "Energy_Production", "Energy_Storage"])
# # # # #     elif number_of_actions == 2:  # presence of either energy consumers/production, consumers/storage or production/storage
# # # # #         if max(agent_storage_devices.values()) == 0:  # presence of only energy consumers & production
# # # # #             list_of_columns.extend(["Energy_Consumption", "Energy_Production"])
# # # # #         else:
# # # # #             if np.all(actions_related_to_aggregators < 0):  # presence of only energy production & storage
# # # # #                 list_of_columns.extend(["Energy_Production", "Energy_Storage"])
# # # # #             else:  # presence of only energy consumers & storage
# # # # #                 list_of_columns.extend(["Energy_Consumption", "Energy_Storage"])
# # # # #     elif number_of_actions == 1:  # presence of either energy consumers or energy production or energy storage
# # # # #         if max(agent_storage_devices.values()) != 0:  # presence of only energy storage
# # # # #             list_of_columns.extend(["Energy_Storage"])
# # # # #         else:
# # # # #             if np.all(actions_related_to_aggregators < 0):  # presence of only energy production
# # # # #                 list_of_columns.extend(["Energy_Production"])
# # # # #             else:  # presence of only energy consumers
# # # # #                 list_of_columns.extend(["Energy_Consumption"])
# # # # #     elif number_of_actions == 0:  # we only manage the energy exchanges between aggregators
# # # # #         print("Attention, the Multi-Energy Grid in question consists of only energy exchangers aggregators !")
# # # # #
# # # # #     # First we get a dataframe from the actions tensor or vector
# # # # #     actions_related_to_aggregators.reshape(number_of_aggregators, number_of_actions)
# # # # #     actions_to_dataframe = pd.DataFrame(
# # # # #                                         data=actions_related_to_aggregators,
# # # # #                                         index=aggregators,
# # # # #                                         columns=list_of_columns
# # # # #                                         )
# # # # #     # We then get a dict from the dataframe
# # # # #     actions_dict = actions_to_dataframe.to_dict()
# # # # #
# # # # #     # Inverting the dict - to get the aggregators.names as keys.
# # # # #     resulting_dict = {
# # # # #         key: {k: v[key] for k, v in actions_dict.items()}
# # # # #         for key in actions_dict[next(iter(actions_dict))].keys()
# # # # #     }  # this is the dict of the actions related to management of device typologies inside the concerned aggregators
# # # # #
# # # # #     # For energy exchanges
# # # # #     exchange_dict = {}  # keys -> (('A1', 'A2'), ...) and values -> corresponding decision (energy exchange value)
# # # # #     for index in range(len(agent_grid_topology)):
# # # # #         exchange = agent_grid_topology[index]
# # # # #         exchange_value = actions_related_to_exchange[index]
# # # # #         number_of_concerned_aggregators = int((len(exchange) - 1) / 2)
# # # # #         concerned_aggregators = exchange[:number_of_concerned_aggregators]
# # # # #         exchange_dict[concerned_aggregators] = exchange_value
# # # # #
# # # # #     return resulting_dict, exchange_dict
# # # #
# # # # # def distribute_energy_exchanges(catalog: "Catalog", aggregator: "Aggregator", energy_accorded_to_exchange: dict, grid_topology: list, converter_list: dict, buying_price: float, selling_price: float, message: dict, scope: list):
# # # # #     """
# # # # #     This function computes the energy exchanges (direct ones and with conversion systems).
# # # # #     May be subject to change.
# # # # #     """
# # # # #     # Initializing
# # # # #     if f"{aggregator.name}.DRL_Strategy.failed_to_deliver" not in catalog.keys:
# # # # #         failed_to_satisfy = 0.0
# # # # #     else:
# # # # #         failed_to_satisfy = catalog.get(f"{aggregator.name}.DRL_Strategy.failed_to_deliver")
# # # # #     energy_bought_inside = 0.0
# # # # #     money_spent_inside = 0.0
# # # # #     energy_sold_inside = 0.0
# # # # #     money_earned_inside = 0.0
# # # # #     energy_bought_outside = 0.0
# # # # #     money_spent_outside = 0.0
# # # # #     energy_sold_outside = 0.0
# # # # #     money_earned_outside = 0.0
# # # # #
# # # # #     # Solving hierarchical energy exchanges; those concerning superior aggregator and subaggregators, be it direct or through a device connecting just both of them
# # # # #     # todo il y a aussi l'aspect du signe de l'echange + et - pour quel agregateur ?
# # # # #     decision_message = {}
# # # # #     fixed_prices_by_superior = {}
# # # # #     energy_exchanges_left = {**energy_accorded_to_exchange}
# # # # #     for exchange in grid_topology:
# # # # #         if aggregator.name in exchange:
# # # # #             # First, we check for superior aggregators, since they distribute first
# # # # #             if aggregator.superior.name in exchange:
# # # # #                 if aggregator.superior in scope:  # if the superior aggregator is also managed by the DRL strategy
# # # # #                     if exchange[:2] in energy_accorded_to_exchange:
# # # # #                         decision_message[aggregator.name] = energy_accorded_to_exchange[exchange[:2]]
# # # # #                         if decision_message[aggregator.name] < 0:  # selling of energy
# # # # #                             energy_sold_outside -= decision_message[aggregator.name]
# # # # #                             money_earned_outside -= decision_message[aggregator.name] * selling_price
# # # # #                         else:  # buying of energy
# # # # #                             energy_bought_outside += decision_message[aggregator.name]
# # # # #                             money_spent_outside += decision_message[aggregator.name] * buying_price
# # # # #                         energy_exchanges_left.pop(exchange[:2])
# # # # #                 else:  # if the superior aggregator is managed by another strategy
# # # # #                     quantities_and_prices = catalog.get(f"{aggregator.name}.{aggregator.superior.nature.name}.energy_accorded")
# # # # #                     if not isinstance(quantities_and_prices, list):  # todo check with Timothé why it is a list in the first place
# # # # #                         decision_message[aggregator.name] = quantities_and_prices["quantity"]
# # # # #                         fixed_prices_by_superior[aggregator.name] = quantities_and_prices["price"]
# # # # #                     if decision_message[aggregator.name] < 0:  # selling of energy
# # # # #                         energy_sold_outside -= decision_message[aggregator.name]
# # # # #                         money_earned_outside -= decision_message[aggregator.name] * fixed_prices_by_superior[aggregator.name]
# # # # #                     else:  # buying of energy
# # # # #                         energy_bought_outside += decision_message[aggregator.name]
# # # # #                         money_spent_outside += decision_message[aggregator.name] * fixed_prices_by_superior[aggregator.name]
# # # # #                     if exchange[:2] in energy_accorded_to_exchange:
# # # # #                         failed_to_satisfy += abs(abs(energy_accorded_to_exchange[exchange[:2]]) - abs(decision_message[aggregator.name]))  # Penalty
# # # # #                         energy_exchanges_left.pop(exchange[:2])
# # # # #
# # # # #             # Then, we check for subaggregators after that
# # # # #             else:
# # # # #                 for subaggregator in aggregator.subaggregators:
# # # # #                     if subaggregator.name in exchange:
# # # # #                         if exchange[:2] in energy_accorded_to_exchange:
# # # # #                             decision_message[subaggregator.name] = energy_accorded_to_exchange[exchange[:2]]
# # # # #                             message["quantity"] = decision_message[subaggregator.name]
# # # # #                             if decision_message[subaggregator.name] < 0:  # selling of energy
# # # # #                                 message["price"] = selling_price
# # # # #                                 energy_bought_inside -= decision_message[aggregator.name]
# # # # #                                 money_spent_inside -= decision_message[aggregator.name] * message["price"]
# # # # #                             else:  # buying of energy
# # # # #                                 message["price"] = buying_price
# # # # #                                 energy_sold_inside += decision_message[aggregator.name]
# # # # #                                 money_earned_inside += decision_message[aggregator.name] * message["price"]
# # # # #                             energy_exchanges_left.pop(exchange[:2])
# # # # #                             if not subaggregator in scope:
# # # # #                                 quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
# # # # #                                 if not isinstance(quantities_and_prices, list):  # todo check with Timothé why it is a list in the first place
# # # # #                                     wanted_energy = quantities_and_prices["energy_maximum"]
# # # # #                                     failed_to_satisfy += abs(abs(message["quantity"]) - abs(wanted_energy))  # Penalty
# # # # #                             catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #
# # # # #     # The rest of energy exchanges
# # # # #     copy_of_left_exchanges = {**energy_exchanges_left}
# # # # #     for device in converter_list:
# # # # #         for exchange in copy_of_left_exchanges:
# # # # #             my_flag = False
# # # # #             for my_aggregator in converter_list[device]:
# # # # #                 if my_aggregator.name in exchange:
# # # # #                     my_flag = True
# # # # #                 else:
# # # # #                     my_flag = False
# # # # #                     break
# # # # #             if my_flag:
# # # # #                 decision_message[device.name] = energy_exchanges_left[exchange]
# # # # #                 if decision_message[device.name] < 0:  # the aggregator sells energy through this energy conversion system
# # # # #                     message["price"] = selling_price
# # # # #                     energy_sold_outside -= decision_message[device.name]
# # # # #                     money_earned_outside -= decision_message[device.name] * message["price"]
# # # # #                 else:  # the aggregator buys energy through this energy conversion system
# # # # #                     message["price"] = buying_price
# # # # #                     energy_bought_outside += decision_message[device.name]
# # # # #                     money_spent_outside += decision_message[device.name] * message["price"]
# # # # #                 message["quantity"] = decision_message[device.name]
# # # # #                 catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
# # # # #                 energy_exchanges_left.pop(exchange)
# # # # #                 break
# # # # #
# # # # #     return energy_bought_inside, money_spent_inside, energy_sold_inside, money_earned_inside, energy_bought_outside, money_spent_outside, energy_sold_outside, money_earned_outside
# # # #
# # # # # my_test ={"b": 1}
# # # # # if my_test:
# # # # #     print(True)
# # # # # ep = 10
# # # # # a = "my  is {}episode".format(ep)
# # # # # print(a)
# # # #
# # # # # #####################################################################################################################
# # # # # TODO creating thermal consumption profiles for the ramp-up management study case (ECOS)
# # # # #######################################################################################################################
# # # # #
# Imports
# from fileinput import filename
# # # # #
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# from copy import deepcopy
# # # # # #
# # # # # # #
# my_year = np.arange(1, 8761)
# # # # # # #
# # Reading data from excel file
# my_df1 = pd.read_excel('D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/heatConsumptionData.xlsx', sheet_name="Sheet1", engine='openpyxl')
# my_df2 = pd.read_excel('D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/heatConsumptionData.xlsx', sheet_name="Sheet2", engine='openpyxl')
# my_data = my_df1.to_dict(orient='list')
# # # plt.rcParams["font.family"] = "Times New Roman"
# # # plt.rcParams['font.size'] = 10
# # # plt.plot(my_data["Hour"], my_data["OutdoorTemperature"])
# # # plt.xlabel('Time in [Hours]')
# # # plt.ylabel('Outdoor Temperature in [°C]')
# # # plt.title("Evolution of outdoor temperature during heating season")
# # # plt.grid(True)
# # # plt.savefig('D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/OutdoorTemp.pdf', format="pdf", bbox_inches="tight")
# # # plt.show()
# setpoints = my_df2.to_dict(orient='list')
# # # # # #
# # Constructing my setpoints evolution over the year - starts in sunday
# house_setpoints = []
# office_setpoints = []
# for week in range(len(my_year) // (24 * 7)):
#     for weekday in range(5):  # temperature setpoints during the week-days
#         office_setpoints.extend(setpoints["setpoint_office_week"])
#         house_setpoints.extend(setpoints["setpoint_house_week"])
#     for weekday in range(2):  # temperature setpoints during the week-days
#         office_setpoints.extend(setpoints["setpoint_office_weekend"])
#         house_setpoints.extend(setpoints["setpoint_house_weekend"])
# # # # #
# remaining_time = len(my_year) % (24 * 7)
# # # # # #
# if remaining_time != 0 and remaining_time % 24 == 0:
#     for day in range(remaining_time // 24):
#         office_setpoints.extend(setpoints["setpoint_office_week"])
#         house_setpoints.extend(setpoints["setpoint_house_week"])
# elif remaining_time % 24 != 0:
#     number_of_hours = remaining_time % 24
#     office_hours = []
#     house_hours = []
#     for hour in range(number_of_hours):
#         office_hours.append(setpoints["setpoint_office_week"][hour])
#         house_hours.append(setpoints["setpoint_house_week"][hour])
#     office_setpoints.extend(office_hours)
#     house_setpoints.extend(house_hours)
# # # # # #
# # # # # # Delta Temperature values through the year
# office_deltas = []
# house_deltas = []
# first_set_of_data = deepcopy(my_data['OutdoorTemperature'][2616:])
# second_set_of_data = deepcopy(my_data['OutdoorTemperature'][:2616])
# yearly_exterior_temperature = deepcopy(first_set_of_data)
# yearly_exterior_temperature.extend(np.zeros(3432))
# yearly_exterior_temperature.extend(second_set_of_data)
# # # # # #
# # # # # #
# for index in range(len(first_set_of_data)):
#      if office_setpoints[index] > yearly_exterior_temperature[index]:
#          office_deltas.append(office_setpoints[index] - yearly_exterior_temperature[index])
#      else:
#          office_deltas.append(0.0)
# for index in range(len(first_set_of_data)):
#      if house_setpoints[index] > yearly_exterior_temperature[index]:
#          house_deltas.append(house_setpoints[index] - yearly_exterior_temperature[index])
#      else:
#          house_deltas.append(0.0)
# # # # # #
# office_deltas.extend(np.zeros(3432))
# house_deltas.extend(np.zeros(3432))
# # # # # #
# for index in range(len(second_set_of_data)):
#     if office_setpoints[index] > yearly_exterior_temperature[index]:
#         office_deltas.append(office_setpoints[index] - yearly_exterior_temperature[index])
#     else:
#         office_deltas.append(0.0)
# for index in range(len(second_set_of_data)):
#      if house_setpoints[index] > yearly_exterior_temperature[index]:
#          house_deltas.append(house_setpoints[index] - yearly_exterior_temperature[index])
#      else:
#          house_deltas.append(0.0)
# # # # # #
# # minTemp = min(yearly_exterior_temperature)
# # minIndex = yearly_exterior_temperature.index(minTemp)
# # start_min_day = my_year[minIndex] - my_year[minIndex] % 24
# # end_min_day = start_min_day + 24
# # # # #
# # maxTemp = max(yearly_exterior_temperature)
# # maxIndex = yearly_exterior_temperature.index(maxTemp)
# # start_max_day = my_year[maxIndex] - my_year[maxIndex] % 24
# # end_max_day = start_max_day + 24
# # # #
# # print(len(first_set_of_data))
# # plt.plot(my_year[0: len(first_set_of_data)], first_set_of_data)
# # plt.show()
# # print(len(second_set_of_data))
# # plt.plot(my_year[0: len(second_set_of_data)], second_set_of_data)
# # plt.show()
# # # #
# # plt.plot(my_year, yearly_exterior_temperature)  # Plotting the Exterior Temperature values through the year
# # plt.plot(my_year, yearly_exterior_temperature)
# # plt.show()
# # # # # # # #
# # plt.plot(my_year, office_deltas)  # Plotting the T° difference between exterior and offices setpoints
# # plt.plot(my_year, house_deltas)  # Plotting the T° difference between exterior and houses setpoints
# # plt.show()
# # # # # # #
# # Total consumption data (kWh)
# old_house_total_space_heating_consumption = 1232500
# new_house_total_space_heating_consumption = 673030
# office_total_space_heating_consumption = 2730948
# # # # # #
# # # Retrieving Cp values for each building type
# old_house_Cp = old_house_total_space_heating_consumption / sum(house_deltas)
# new_house_Cp = new_house_total_space_heating_consumption / sum(house_deltas)
# office_Cp = office_total_space_heating_consumption / sum(office_deltas)
# # # # # #
# # Consumption profiles
# old_house_profile = []
# new_house_profile = []
# office_profile = []
# for index in range(len(house_deltas)):
#     old_house_profile.append(old_house_Cp * house_deltas[index])
#     new_house_profile.append(new_house_Cp * house_deltas[index])
# for index in range(len(office_deltas)):
#     office_profile.append(office_Cp * office_deltas[index])
# # # # #
# # heat_sink = np.empty(len(my_year))
# # heat_sink.fill(1300.0)
# # # # #
# total_consumption = []
# for index in range(len(office_profile)):
#     total_consumption.append(float(old_house_profile[index] + new_house_profile[index] + office_profile[index]))
# # # # #
# # print(total_consumption.index(max(total_consumption)))
# # Plotting the consumption profiles
# my_fig = plt.figure()
# # # plt.plot(my_year, old_house_profile, label="Old house consumption profile")
# # # plt.plot(my_year, new_house_profile, label="New house consumption profile")
# # # plt.plot(my_year, office_profile, label="Office consumption profile")
# print(max(total_consumption))
# plt.plot(my_year, total_consumption, label="Total consumption profile")
# plt.show()
# # # plt.plot(my_year[:2712], total_consumption[:2712], label="Total consumption profile")
# # # plt.plot(my_year[6144:], total_consumption[6144:], label="Total consumption profile")
# # # # # #
# # # # plt.plot(my_year, heat_sink, label="Dissipation profile")
# # # plt.legend()
# plt.show()
# # # # # #
# first_season = deepcopy(total_consumption[:2712])
# days = [first_season[i:i + 24] for i in range(0, len(first_season), 24)]
# weekdays = []
# weekends = []
# # Iterate over the days list in chunks of 7 (5 weekdays + 2 weekends)
# for i in range(0, len(days), 7):
#     weekdays.extend(days[i:i+5])  # First 5 days go to weekdays
#     weekends.extend(days[i+5:i+7])  # Next 2 days go to weekends (if they exist)
#
# num_groups = len(weekends) // 8  # Number of groups of 4 weekends
# weekend_averages = []
#
# for i in range(0, num_groups * 8, 8):  # Process weekends in chunks of 4
#     chunk = weekends[i:i+8]  # Extract 4 consecutive weekend lists
#     avg_24h = np.mean(chunk, axis=0)  # Compute element-wise average (hourly)
#     weekend_averages.append(avg_24h.tolist())  # Convert back to list and store
#
# num_groups = len(weekdays) // 20  # Number of groups of 4 weekends
# weekdays_averages = []
#
# for i in range(0, num_groups * 20, 20):  # Process weekends in chunks of 4
#     chunk = weekdays[i:i+20]  # Extract 4 consecutive weekend lists
#     avg_24h = np.mean(chunk, axis=0)  # Compute element-wise average (hourly)
#     weekdays_averages.append(avg_24h.tolist())  # Convert back to list and store
#
# days_array = np.array(days)
# hourly_median = np.median(days_array, axis=0)
# hourly_median_list = hourly_median.tolist()
#
# myFirstSeason = []  # 1 janv -> 23 avril inclus
# for index in range(len(weekend_averages)):
#     myFirstSeason.extend(weekdays_averages[index])
#     myFirstSeason.extend(weekend_averages[index])
#
# timeFirstSeason = np.arange(0, len(myFirstSeason), 1)
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams['font.size'] = 10
# plt.plot(timeFirstSeason, myFirstSeason, label="Heating Consumption Profile")
# plt.xlabel("Time in [hours]")
# plt.ylabel("Heat loads in [MWh]")
# plt.legend()
# plt.title("The heat loads during winter season")
# plt.grid(True)
# plt.savefig("D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/WinterSeasonHeatingConsumptionProfiles.pdf", format="pdf", bbox_inches="tight")
# plt.show()

# #
# # firstSeasonMaxConso = max(first_season)
# # maxFirstSeasonIndexConso = total_consumption.index(firstSeasonMaxConso)
# # startFirstSeasonMaxConso = my_year[maxFirstSeasonIndexConso] - my_year[maxFirstSeasonIndexConso] % 24
# # endFirstSeasonMaxConso = startFirstSeasonMaxConso + 24
# #
# # firstSeasonMinConso = min(first_season)
# # minFirstSeasonIndexConso = total_consumption.index(firstSeasonMinConso)
# # startFirstSeasonMinConso = my_year[minFirstSeasonIndexConso] - my_year[minFirstSeasonIndexConso] % 24
# # endFirstSeasonMinConso = startFirstSeasonMinConso + 24
# #
# # firstSeasonMoyConso = sum(first_season) / len(first_season)
# # closest = min(first_season, key=lambda x: abs(x - firstSeasonMoyConso))
# # moyFirstSeasonIndexConso = total_consumption.index(closest)
# # startFirstSeasonMoyConso = my_year[moyFirstSeasonIndexConso] - my_year[moyFirstSeasonIndexConso] % 24
# # endFirstSeasonMoyConso = startFirstSeasonMoyConso + 24
# #
# firstSeasonMedConso = np.median(first_season)
# medFirstSeasonIndexConso = total_consumption.index(firstSeasonMedConso)
# startFirstSeasonMedConso = my_year[medFirstSeasonIndexConso] - my_year[medFirstSeasonIndexConso] % 24
# endFirstSeasonMedConso = startFirstSeasonMedConso + 24
# #
# # fig = plt.figure()
# plt.rcParams['font.family'] = "Times New Roman"
# plt.rcParams['font.size'] = 10
# # plt.plot(my_year[0:24], total_consumption[startFirstSeasonMaxConso:endFirstSeasonMaxConso], label="Max consumption profile")
# # plt.plot(my_year[0:24], total_consumption[startFirstSeasonMinConso:endFirstSeasonMinConso], label="Min consumption profile")
# # plt.plot(my_year[0:24], total_consumption[startFirstSeasonMoyConso:endFirstSeasonMoyConso], label="Moy consumption profile")
# plt.plot(my_year[0:24], hourly_median_list, label="Hourly median consumption profile during the first season")
# plt.plot(my_year[0:24], total_consumption[startFirstSeasonMedConso:endFirstSeasonMedConso], label="Heat Consumption Representative Day For The Winter Season")
# # plt.plot(my_year[0:24], heat_sink[0:24], label="Biomass production profile", linestyle='--')
# # plt.plot(my_year[0:24], 0.75 * heat_sink[0:24], label="Threshold", linestyle='--')
# plt.title("First season representative day")
# plt.xlabel("Time step in [hours]")
# plt.ylabel("Energy in [MWh]")
# # plt.legend()
# plt.show()
# # fig.savefig("D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/firstSeasonRepresentativeDay.png")
# # plt.close(fig)
# #
# # print(total_consumption[startFirstSeasonMedConso:endFirstSeasonMedConso])
# # # print(total_consumption[startFirstSeasonMoyConso:endFirstSeasonMoyConso])
# #
# second_season = deepcopy(total_consumption[6144:])
# days = [second_season[i:i + 24] for i in range(0, len(second_season), 24)]
# weekdays = []
# weekends = []
# # Iterate over the days list in chunks of 7 (5 weekdays + 2 weekends)
# for i in range(0, len(days), 7):
#     weekdays.extend(days[i:i+5])  # First 5 days go to weekdays
#     weekends.extend(days[i+5:i+7])  # Next 2 days go to weekends (if they exist)
# num_groups = len(weekends) // 8  # Number of groups of 4 weekends
# weekend_averages = []
#
# for i in range(0, num_groups * 8, 8):  # Process weekends in chunks of 4
#     chunk = weekends[i:i+8]  # Extract 4 consecutive weekend lists
#     avg_24h = np.mean(chunk, axis=0)  # Compute element-wise average (hourly)
#     weekend_averages.append(avg_24h.tolist())  # Convert back to list and store
#
# num_groups = len(weekdays) // 20  # Number of groups of 4 weekends
# weekdays_averages = []
#
# for i in range(0, num_groups * 20, 20):  # Process weekends in chunks of 4
#     chunk = weekdays[i:i+20]  # Extract 4 consecutive weekend lists
#     avg_24h = np.mean(chunk, axis=0)  # Compute element-wise average (hourly)
#     weekdays_averages.append(avg_24h.tolist())  # Convert back to list and store
#
# days_array = np.array(days)
# hourly_median = np.median(days_array, axis=0)
# hourly_median_list = hourly_median.tolist()
#
# mySecondSeason = []  # 14 sept -> 31 déc inclus
# for index in range(len(weekend_averages)):
#     mySecondSeason.extend(weekdays_averages[index])
#     mySecondSeason.extend(weekend_averages[index])
#
# timeSecondSeason = np.arange(0, len(mySecondSeason), 1)
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams['font.size'] = 10
# plt.plot(timeSecondSeason, mySecondSeason, label="Heating Consumption Profile")
# plt.xlabel("Time in [hours]")
# plt.ylabel("Heat loads in [MWh]")
# plt.legend()
# plt.title("The heat loads during fall season")
# plt.grid(True)
# plt.savefig("D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/FallSeasonHeatingConsumptionProfiles.pdf", format="pdf", bbox_inches="tight")
# plt.show()


# days_array = np.array(days)
# hourly_median = np.median(days_array, axis=0)
# hourly_median_list = hourly_median.tolist()
# #
# # secondSeasonMaxConso = max(second_season)
# # maxSecondSeasonIndexConso = total_consumption.index(secondSeasonMaxConso)
# # startSecondSeasonMaxConso = my_year[maxSecondSeasonIndexConso] - my_year[maxSecondSeasonIndexConso] % 24
# # endSecondSeasonMaxConso = startSecondSeasonMaxConso + 24
# #
# # secondSeasonMinConso = min(second_season)
# # minSecondSeasonIndexConso = total_consumption.index(secondSeasonMinConso)
# # startSecondSeasonMinConso = my_year[minSecondSeasonIndexConso] - my_year[minSecondSeasonIndexConso] % 24
# # endSecondSeasonMinConso = startSecondSeasonMinConso + 24
# #
# # secondSeasonMoyConso = sum(second_season) / len(second_season)
# # closest = min(first_season, key=lambda x: abs(x - secondSeasonMoyConso))
# # moySecondSeasonIndexConso = total_consumption.index(closest)
# # startSecondSeasonMoyConso = my_year[moySecondSeasonIndexConso] - my_year[moySecondSeasonIndexConso] % 24
# # endSecondSeasonMoyConso = startSecondSeasonMoyConso + 24
# #
# secondSeasonMedConso = np.median(second_season)
# medSecondSeasonIndexConso = total_consumption.index(secondSeasonMedConso)
# startSecondSeasonMedConso = my_year[medSecondSeasonIndexConso] - my_year[medSecondSeasonIndexConso] % 24
# endSecondSeasonMedConso = startSecondSeasonMedConso + 24
# #
# # fig = plt.figure()
# # plt.plot(my_year[0:24], total_consumption[startSecondSeasonMaxConso:endSecondSeasonMaxConso], label="Max consumption profile")
# # plt.plot(my_year[0:24], total_consumption[startSecondSeasonMinConso:endSecondSeasonMinConso], label="Min consumption profile")
# # plt.plot(my_year[0:24], total_consumption[startSecondSeasonMoyConso:endSecondSeasonMoyConso], label="Moy consumption profile")
# plt.plot(my_year[0:24], hourly_median_list, label="Hourly Median consumption profile during the second season")
# plt.plot(my_year[0:24], total_consumption[startSecondSeasonMedConso:endSecondSeasonMedConso], label="Heat Consumption Representative Day For The Fall Season")
# # plt.plot(my_year[0:24], heat_sink[0:24], label="Biomass production profile", linestyle='--')
# # plt.plot(my_year[0:24], 0.75 * heat_sink[0:24], label="Threshold", linestyle='--')
# # plt.title("Second season representative day")
# plt.xlabel("Time step in [hours]")
# plt.ylabel("Energy in [MWh]")
# plt.legend()
# plt.grid(True)
# plt.title("Heating Consumption Profiles for Representative Days of the two heating seasons")
# plt.savefig("D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/HeatConsumptionRepresentativeDays.pdf", format="pdf", bbox_inches="tight")
# plt.show()
# # fig.savefig("D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/secondSeasonRepresentativeDay.png")
# # plt.close(fig)
# #
# # print(total_consumption[startSecondSeasonMedConso:endSecondSeasonMedConso])
#
# # # # maxConso = max(total_consumption)
# # # # maxIndexConso = total_consumption.index(maxConso)
# # # # startMaxConso = my_year[maxIndexConso] - my_year[maxIndexConso] % 24
# # # # endMaxConso = startMaxConso + 24
# # # #
# # # #
# # # # minConso = min(total_consumption)
# # # # minIndexConso = total_consumption.index(minConso)
# # # # startMinConso = my_year[minIndexConso] - my_year[minIndexConso] % 24
# # # # endMinConso = startMinConso + 24
# # # #
# # # # real_conso = total_consumption[:2712] + total_consumption[6144:]
# # # # moyConso = sum(real_conso) / len(real_conso)
# # # # closest = min(real_conso, key=lambda x: abs(x - moyConso))
# # # # moyIndexConso = total_consumption.index(closest)
# # # # startMoyConso = my_year[moyIndexConso] - my_year[moyIndexConso] % 24
# # # # endMoyConso = startMoyConso + 24
# # # #
# # # #
# # # #
# # # # typic_day = total_consumption[startMoyConso:startMoyConso + 11]
# # # #
# # # # for element in range(13):
# # # #     typic_day.append(total_consumption[startMoyConso + 11 + element] + 0.25 * total_consumption[startMoyConso + 11 + element])
# # # # typic_day[11] -= 100
# # # # typic_day[17] -= 100
# # # #
# # # # for element in range(len(typic_day)):
# # # #     if element != 18:
# # # #         if typic_day[element] < 1300:
# # # #             typic_day[element] -= 250
# # # #
# # # # typic_day[18] -= 400
# # # #
# # # # # typicDay = {"time": my_year[0:24], "load": typic_day}
# # # # # typicDay_df = pd.DataFrame(data=typicDay)
# # # # # nameFile = "D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/typicalDay.csv"
# # # # # typicDay_df.to_csv(nameFile, index=False, sep=";")
# # # #
# # # # plt.plot(my_year[0:24], total_consumption[startMaxConso:endMaxConso], label="Max consumption profile")
# # # # plt.plot(my_year[0:24], total_consumption[startMinConso:endMinConso], label="Min consumption profile")
# # # # plt.plot(my_year[0:24], total_consumption[startMoyConso:endMoyConso], label="Moy consumption profile")
# # # # plt.plot(my_year[0:24], typic_day, label="representative consumption profile")
# # plt.plot(my_year[0:24], heat_sink[0:24], label="Biomass production profile", linestyle='--')
# # plt.plot(my_year[0:24], 0.75 * heat_sink[0:24], label="Threshold", linestyle='--')
# # # # plt.plot(my_year[0:24], np.zeros_like(my_year[0:24]), linestyle='--')
# # # # plt.xlabel("Time in hours")
# # # # plt.ylabel("Energy in kWh")
# # # # plt.title("Representative days for heat management")
# # # # plt.legend()
# # # # plt.show()
# # # #
# # # # # # Writing data on a file for the new background subclass
# my_total_consumption = []
# for index in range(len(old_house_profile)):
#     old_house_profile[index] = float(old_house_profile[index])
#     new_house_profile[index] = float(new_house_profile[index])
#     office_profile[index] = float(office_profile[index])
#     # heat_sink[index] = float(heat_sink[index])
#     my_total_consumption.append(old_house_profile[index] + new_house_profile[index] + office_profile[index])
# # # # #
# # # # # with open('new_background.txt', "w") as my_file:
# # # #     my_file.write(f"Thermal consumption of old houses : {old_house_profile}")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"Thermal consumption of new houses : {new_house_profile}")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"Thermal consumption of offices : {office_profile}")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"\n")
# # # #     my_file.write(f"Thermal consumption of offices : {heat_sink.tolist()}")
# # # # my_file.close()
# # # #
# # # # #
# # # # # old_house_profile = list(filter((0.0).__ne__, old_house_profile))  # removing the zero values
# # # # # print(len(old_house_profile))
# # # # # x1_axis = np.arange(1, len(old_house_profile) + 1)
# # # # # old_house_profile.sort(reverse=True)
# # # # # my_fig = plt.figure()
# # # # # plt.plot(x1_axis, old_house_profile, label="Old house consumption profile")
# # # # # plt.show()
# # # # #
# # # # # new_house_profile = list(filter((0.0).__ne__, new_house_profile))  # removing the zero values
# # # # # print(len(new_house_profile))
# # # # # x2_axis = np.arange(1, len(new_house_profile) + 1)
# # # # # new_house_profile.sort(reverse=True)
# # # # # plt.plot(x2_axis, new_house_profile, label="New house consumption profile")
# # # # # plt.show()
# # # # #
# # # # # office_profile = list(filter((0.0).__ne__, office_profile))  # removing the zero values
# # # # # print(len(office_profile))
# # # # # x3_axis = np.arange(1, len(office_profile) + 1)
# # # # # office_profile.sort(reverse=True)
# # # # # plt.plot(x3_axis, office_profile, label="Office consumption profile")
# # # # # plt.show()
# # # #
# total_consumption = list(filter((0.0).__ne__, total_consumption))  # removing the zero values
# # # # # print(len(my_total_consumption))
# # # # # print(max(my_total_consumption))
# x4_axis = np.arange(1, len(total_consumption) + 1)
# threshold = np.empty(len(x4_axis))
# threshold.fill(1300)
# total_consumption.sort(reverse=True)
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 10
# plt.plot(x4_axis, total_consumption, label="Heat loads monotone")
# plt.plot(x4_axis, threshold, label="Baseload heat generation", linestyle='--')
# plt.xlabel("Duration in [hours]")
# plt.ylabel("Energy in [MWh]")
# plt.title("Sizing of the biomass plant")
# plt.legend()
# plt.savefig("D:/dossier_y23hallo/PycharmProjects/peacefulness/cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/biomassPlantSizing.pdf", format="pdf", bbox_inches="tight")
# plt.show()
# # # #
# # #
# # # # #####################################################################################################################
# # # # # # TODO creating biomass power profiles for the ramp-up management study case (ECOS)
# # # # # ###################################################################################################################
# the figures of evolution that we have correspond to a steam generator/turbine group of a 600MW generation capacity
# hyp.1 -> the efficiency considered is 35% thus, the nominal thermal power is 600 / 0.35 = 1714.28571428571 MWth
# hyp.2 -> the inlet temperature is around 60°C
# hyp.3 -> the evolution figures don't depend on the thermal power

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from CoolProp.CoolProp import PropsSI
#
#
#
# def get_data_at_timestep(df, timestep):
#     # Check if the timestep exists in the DataFrame
#     if timestep in df['Time'].values:
#         return df.loc[df['Time'] == timestep, 'ThermalPower'].values[0]
#     else:
#         # If timestep does not exist, interpolate between the nearest timesteps
#         lower_timestep = df[df['Time'] < timestep]['Time'].max()
#         upper_timestep = df[df['Time'] > timestep]['Time'].min()
#
#         # Check if lower and upper timesteps exist
#         if pd.isna(lower_timestep) or pd.isna(upper_timestep):
#             raise ValueError(f"Timestep {timestep} is out of bounds for interpolation.")
#
#         # Get corresponding data for lower and upper timesteps
#         lower_data = df.loc[df['Time'] == lower_timestep, 'ThermalPower'].values[0]
#         upper_data = df.loc[df['Time'] == upper_timestep, 'ThermalPower'].values[0]
#
#         # Perform linear interpolation
#         interpolated_value = lower_data + (upper_data - lower_data) * (timestep - lower_timestep) / (upper_timestep - lower_timestep)
#         return interpolated_value
#
#
#
# # Reading data
# filepath = "cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData"
# cold_temperature_file = filepath + "/" + "coldStartUpTemp.csv"
# cold_steamflow_file = filepath + "/" + "coldStartUpFlow.csv"
# cold_pressure_file = filepath + "/" + "coldStartUpPressure.csv"
# warm_pressure_file = filepath + "/" + "warmStartUpPressure.csv"
# warm_temperature_file = filepath + "/" + "warmStartUpTemp.csv"
# warm_steamflow_file = filepath + "/" + "warmStartUpFlow.csv"
#
# cold_temperatures = pd.read_csv(cold_temperature_file, names=['Time', 'Temperature'], sep=';', decimal=',',header=None)
# cold_steam_flow = pd.read_csv(cold_steamflow_file, names=['Time', 'Flow'], sep=';', decimal=',',header=None)
# cold_pressure = pd.read_csv(cold_pressure_file, names=['Time', 'Pressure'], sep=';', decimal=',',header=None)
# warm_pressure = pd.read_csv(warm_pressure_file, names=['Time', 'Pressure'], sep=';', decimal=',',header=None)
# warm_temperatures = pd.read_csv(warm_temperature_file, names=['Time', 'Temperature'], sep=';', decimal=',',header=None)
# warm_steam_flow = pd.read_csv(warm_steamflow_file, names=['Time', 'Flow'], sep=';', decimal=',',header=None)
#
# common_length = max([len(cold_temperatures), len(cold_steam_flow), len(cold_pressure)])
#
# new_time_points_cold_Temp = np.linspace(cold_temperatures["Time"].min(), cold_temperatures["Time"].max(), common_length)
# new_time_points_warm_Temp = np.linspace(warm_temperatures["Time"].min(), warm_temperatures["Time"].max(), common_length)
# new_time_points_cold_Flow = np.linspace(cold_steam_flow["Time"].min(), cold_steam_flow["Time"].max(), common_length)
# new_time_points_warm_Flow = np.linspace(warm_steam_flow["Time"].min(), warm_steam_flow["Time"].max(), common_length)
# new_time_points_cold_Pressure = np.linspace(cold_pressure["Time"].min(), cold_pressure["Time"].max(), common_length)
# new_time_points_warm_Pressure = np.linspace(warm_pressure["Time"].min(), warm_pressure["Time"].max(), common_length)
#
# cold_temperatures_new = pd.DataFrame({'Time': new_time_points_cold_Temp})
# warm_temperatures_new = pd.DataFrame({'Time': new_time_points_warm_Temp})
# cold_steam_flow_new = pd.DataFrame({'Time': new_time_points_cold_Flow})
# warm_steam_flow_new = pd.DataFrame({'Time': new_time_points_warm_Flow})
# cold_pressure_new = pd.DataFrame({'Time': new_time_points_cold_Pressure})
# warm_pressure_new = pd.DataFrame({'Time': new_time_points_warm_Pressure})
#
# # interpolating data
# cold_temperatures_new['Temperature'] = np.interp(cold_temperatures_new['Time'], cold_temperatures['Time'], cold_temperatures['Temperature'])
# warm_temperatures_new['Temperature'] = np.interp(warm_temperatures_new['Time'], warm_temperatures['Time'], warm_temperatures['Temperature'])
# # correcting error
# for index in range(81, 87):
#     warm_temperatures_new.loc[index, "Temperature"] = warm_temperatures_new.loc[index - 1, "Temperature"]
# cold_steam_flow_new['Flow'] = np.interp(cold_steam_flow_new['Time'], cold_steam_flow['Time'], cold_steam_flow['Flow'])
# warm_steam_flow_new['Flow'] = np.interp(warm_steam_flow_new['Time'], warm_steam_flow['Time'], warm_steam_flow['Flow'])
# for index in range(82, 87):
#     warm_steam_flow_new.loc[index, "Flow"] = warm_steam_flow_new.loc[index - 1, "Flow"]
# cold_pressure_new['Pressure'] = np.interp(cold_pressure_new['Time'], cold_pressure['Time'], cold_pressure['Pressure'])
# warm_pressure_new['Pressure'] = np.interp(warm_pressure_new['Time'], warm_pressure['Time'], warm_pressure['Pressure'])
#
# # plots
# # plt.plot(cold_temperatures_new['Time'], cold_temperatures_new['Temperature'], label="Temperature")
# # plt.plot(cold_pressure_new['Time'], cold_pressure_new['Pressure'], label="Pressure")
# # plt.plot(cold_steam_flow_new['Time'], cold_steam_flow_new['Flow'], label="Flow")
# # plt.xlabel('Time in [hour]')
# # plt.title('Parameters of the biomass during a cold start up')
# # plt.legend()
# # plt.show()
# # plt.plot(warm_temperatures_new['Time'], warm_temperatures_new['Temperature'])
# # plt.plot(warm_pressure_new['Time'], warm_pressure_new['Pressure'])
# # plt.plot(warm_steam_flow_new['Time'], warm_steam_flow_new['Flow'])
# # plt.show()
#
# # finding Cp corresponding to the nominal state
# fluid = 'Water'
# warm_pressure = warm_pressure_new['Pressure'].max() * 1e5  # should be in Pascals
# cold_pressure = cold_pressure_new['Pressure'].max() * 1e5  # should be in Pascals
# warm_temperature = warm_temperatures_new['Temperature'].max() + 273.15  # should be in °K
# cold_temperature = cold_temperatures_new['Temperature'].max() + 273.15  # should be in °K
# cold_Cp = PropsSI('C', 'P', cold_pressure, 'T', cold_temperature, fluid)
# warm_Cp = PropsSI('C', 'P', warm_pressure, 'T', warm_temperature, fluid)
# nominal_thermal_power = (600 / 0.35) * 1e6
# input_Temp = 60 + 273.15
# nominal_mass_flow = nominal_thermal_power / (((cold_Cp + warm_Cp) / 2) * (((cold_temperature + warm_temperature) / 2) - input_Temp))
#
#
# # finding the evolution of P per time as a percentage of nominal thermal power
# cold_steam_flow_new.loc[:, "Flow"] *= nominal_mass_flow / 100
# warm_steam_flow_new.loc[:, "Flow"] *= nominal_mass_flow / 100
# cold_temperatures_new.loc[:, "Temperature"] += 273.15
# warm_temperatures_new.loc[:, "Temperature"] += 273.15
# cold_pressure_new.loc[:, "Pressure"] *= 1e5
# warm_pressure_new.loc[:, "Pressure"] *= 1e5
#
# cold_thermal_power = []
# warm_thermal_power = []
#
# for index in range(len(cold_steam_flow_new)):
#     cold_Cp = PropsSI('C', 'P', cold_pressure_new.loc[index, "Pressure"], 'T', cold_temperatures_new.loc[index, "Temperature"], fluid)
#     cold_thermal_power.append(((cold_steam_flow_new.loc[index, "Flow"] * cold_Cp * (cold_temperatures_new.loc[index, "Temperature"] - input_Temp)) / nominal_thermal_power) * 100)
#     warm_Cp = PropsSI('C', 'P', warm_pressure_new.loc[index, "Pressure"], 'T', warm_temperatures_new.loc[index, "Temperature"], fluid)
#     warm_thermal_power.append(((warm_steam_flow_new.loc[index, "Flow"] * warm_Cp * (warm_temperatures_new.loc[index, "Temperature"] - input_Temp)) / nominal_thermal_power) * 100)
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 10
# plt.figure(figsize=(6, 4))
# plt.plot(cold_steam_flow_new['Time'], cold_thermal_power)
# plt.xlabel('Time in [hour]')
# plt.ylabel("Percent of nominal Power in [%]")
# # plt.title('Evolution of generated heat during cold start up')
# # plt.legend()
# # plt.grid(True)
# plt.savefig(filepath + "/" + "Cold_StartUp.pdf", format="pdf", bbox_inches="tight")
# plt.show()

# plt.plot(warm_steam_flow_new['Time'], warm_thermal_power)
# plt.show()
#
# cold_thermal_power = pd.DataFrame({'Time': cold_steam_flow_new['Time'], 'ThermalPower': cold_thermal_power})
# warm_thermal_power = pd.DataFrame({'Time': warm_steam_flow_new['Time'], 'ThermalPower': warm_thermal_power})
# coldStartUpThermalPowerEvolution_filepath = filepath + "/" + "coldStartUpThermalPowerEvolution.csv"
# cold_thermal_power.to_csv(coldStartUpThermalPowerEvolution_filepath, sep=';', decimal=',', index=False, header=False)
# warmStartUpThermalPowerEvolution_filepath = filepath + "/" + "warmStartUpThermalPowerEvolution.csv"
# warm_thermal_power.to_csv(warmStartUpThermalPowerEvolution_filepath, sep=';', decimal=',', index=False, header=False)
# # #
# # #
# # # # #####################################################################################################################
# # # # TODO saving biomass power profiles in the corresponding json file for the ramp-up management study case (ECOS)
# # # #######################################################################################################################
# # # # import pandas as pd
# # # # import json
# # # #
# # # #
# # # # # reading dataframes from csv file
# # # # filepath = "cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData"
# # # # coldStartUpThermalPowerEvolution_file = filepath + "/" + "coldStartUpThermalPowerEvolution.csv"
# # # # cold_power = pd.read_csv(coldStartUpThermalPowerEvolution_file, names=['Time', 'ThermalPower'], sep=';', decimal=',',header=None)
# # # # warmStartUpThermalPowerEvolution_file = filepath + "/" + "warmStartUpThermalPowerEvolution.csv"
# # # # warm_power = pd.read_csv(warmStartUpThermalPowerEvolution_file, names=['Time', 'ThermalPower'], sep=';', decimal=',',header=None)
# # # #
# # # # # reading the json file of BiomassGasPlantAlternative
# # # # json_filepath = "lib/Subclasses/Device/BiomassGasPlantAlternative"
# # # # jsonFile = json_filepath + "/" + "BiomassGasPlantAlternative.json"
# # # # with open(jsonFile, 'r') as my_file:
# # # #     systemData = json.load(my_file)
# # # #
# # # # # appending thermal power evolution profiles
# # # # for technology in systemData['technical_data']:
# # # #     systemData['technical_data'][technology]["cold_startup"] = {"time": [], "power": []}
# # # #     systemData['technical_data'][technology]["cold_startup"]["time"].extend(cold_power["Time"].tolist())
# # # #     systemData['technical_data'][technology]["cold_startup"]["power"].extend(cold_power["ThermalPower"].tolist())
# # # #     systemData['technical_data'][technology]["warm_startup"] = {"time": [], "power": []}
# # # #     systemData['technical_data'][technology]["warm_startup"]["time"].extend(warm_power["Time"].tolist())
# # # #     systemData['technical_data'][technology]["warm_startup"]["power"].extend(warm_power["ThermalPower"].tolist())
# # # #
# # # # # writing the data in the json file
# # # # with open(jsonFile, 'w') as my_file:
# # # #     json.dump(systemData, my_file, indent=4)
# # #
# # # # #####################################################################################################################
# # # # TODO testing the biomass alternative plant
# # # # #######################################################################################################################
# from os import chdir, path
# import sys
# chdir("D:/dossier_y23hallo/PycharmProjects/peacefulness")
# sys.path.append(path.abspath("D:/dossier_y23hallo/PycharmProjects/peacefulness"))
# from typing import Dict, List, Optional
# from ijson import items
# import numpy as np
# from math import ceil
# from lib.Subclasses.Device.BiomassGasPlantAlternative.BiomassGasPlantAlternative import get_data_at_timestep, get_timestep_of_data, check_distance
#
# # # # #
# # # # #
# class DummyClass:
#     def __init__(self, profile: Dict, device_parameters: Dict, filepath: str, timestep: int):
#         self._filename = filepath
#         self._max_power = device_parameters["max_power"] * timestep  # max power (kWh)
#         self._recharge_quantity = device_parameters["recharge_quantity"]  # fuel quantity recharged at each period (kg)
#         self._autonomy = device_parameters["autonomy"] / timestep
#         self._initial_conditions = {"initial_energy": device_parameters["initial_energy"], "initial_state": self._determine_initial_state(device_parameters["initial_energy"])}
#         self._read_data_profiles(profile)
#         self.cold_startup_signal_time = None
#         self.cold_startup = {"time_step": [0, 1, 2, 3, 4, 5, 6, 7, 8], "energy": [0.01, 0.015119328903383002, 0.1195973380807878, 0.2164839934098297, 0.31337064873887166, 0.5154843893926306, 0.7175981300463896, 0.9197118707001486, 1]}
#         # self.warm_startup_flag = False
#         # self.warm_startup = {"time_step": [0, 1, 2], "energy": [0.01, 0.7473570931988995, 1]}
#         self._log = {"time_step": [], "energy": [], "state": []}
#         for index in range(len(self.cold_startup["energy"])):
#             self.cold_startup["energy"][index] *= self._max_power
#         # for index in range(len(self.warm_startup["energy"])):
#         #     self.warm_startup["energy"][index] *= self._max_power
# # #
# # #
#     def _read_data_profiles(self, profiles):
#         data_device = self._read_technical_data(profiles["device"])  # parsing the data
#
#         self._technical_profile = dict()
#
#         # usage profile
#         self._technical_profile[data_device["usage_profile"]["nature"]] = None
#         self._efficiency = data_device["efficiency"]  # the efficiency of the waste/biomass plant (%)
#         self._min_PCI = data_device["min_PCI"]  # the min PCI of the waste/biomass plant (kWh/kg)
#         self._max_PCI = data_device["max_PCI"]  # the max PCI of the waste/biomass plant (kWh/kg)
#         self._coldStartUp = data_device["cold_startup"]  # thermal power evolution during a cold startup
#         self._warmStartUp = data_device["warm_startup"]  # thermal power evolution during a warm startup
#
#     def _determine_initial_state(self, initial_power):
#         if initial_power == self._max_power:
#             return "nominal_state"
#         elif initial_power == 0:
#             return "idle"
#         elif self._max_power > initial_power > 0:
#             return "cold_startup"
#         else:
#             raise Exception("The initial energy specified for the biomass plant is not valid !")
#
#     def _read_technical_data(self, technical_profile):
#         # parsing the data
#         with open(self._filename, "r") as file:
#             temp = items(file, "technical_data", use_float=True)
#             data = {}
#             for truc in temp:
#                 data = truc
#
#         # getting the technical profile
#         try:
#             technical_data = data[technical_profile]
#         except:
#             raise Exception(f"{technical_profile} does not belong to the list of predefined device profiles for the class {type(self).__name__}: {data['device_consumption'].keys()}")
#
#         return technical_data
# # # # # # #
# # # # # # #     # ##########################################################################################
# # # # # # #     # Dynamic behavior
# # # # # # #     # ##########################################################################################
# # # # # #     def print_my_data(self, timestep):
# # # # # #         print(get_data_at_timestep(self._coldStartUp, timestep))
# # # # # #         # print(get_data_at_timestep(self._warmStartUp, timestep))
# # # # # #
#     def update(self, current_timestep):
#         min_production = 0.0
#
#         if current_timestep == 0:  # initial conditions
#             self._log["state"].append(self._initial_conditions["initial_state"])
#             if self._log["state"][-1] == "cold_startup":
#                 self._log["energy"].append(- self._initial_conditions["initial_energy"])
#                 self.cold_startup_signal_time = current_timestep
#
#         if self._log["state"][-1] == "idle":
#             max_production = - 0.01 * self._max_power
#             coming_volume = - 0.01 * self._max_power
#
#         elif self._log["state"][-1] == "nominal_state":
#             max_production = - self._max_power
#             coming_volume = - 5 * self._max_power
#
#         elif self._log["state"][-1] == "cold_startup":  # a cold startup is triggered
#             coming_volume = 0.0
#             delta_time = current_timestep - self.cold_startup_signal_time
#             if delta_time > 0 and delta_time in self.cold_startup["time_step"]:
#                 corresponding_max_energy = self.cold_startup["energy"][self.cold_startup["time_step"].index(delta_time - 1)]
#                 if - self._log["energy"][-1] == corresponding_max_energy:  # a standard cold start-up (E_accorded == corresponding max_production at timestep 'i')
#                     max_production = - self.cold_startup["energy"][self.cold_startup["time_step"].index(delta_time)]
#                     for index in range(self.cold_startup["time_step"].index(delta_time), 5 + self.cold_startup["time_step"].index(delta_time)):
#                         if index <= len(self.cold_startup["energy"]) - 1:
#                             coming_volume -= self.cold_startup["energy"][index]
#                         else:
#                             coming_volume -= self._max_power
#                 else:  # in the previous time step the energy accorded was less than the one corresponding to the standard curve
#                     corresponding_time, corresponding_power = get_timestep_of_data(self.cold_startup, - self._log["energy"][-1], self._max_power)
#                     next_timestep = corresponding_time + 1
#                     if not next_timestep > max(self.cold_startup["time_step"]):
#                         max_production = - get_data_at_timestep(self.cold_startup, next_timestep)
#                         coldStartUpIndex = find_nearest_point(self.cold_startup["time_step"], ceil(next_timestep))
#                         for index in range(coldStartUpIndex, 5 + coldStartUpIndex):
#                             if index <= len(self.cold_startup["energy"]) - 1:
#                                 coming_volume -= self.cold_startup["energy"][index]
#                             else:
#                                 coming_volume -= self._max_power
#                     else:
#                         max_production = - self._max_power
#                         coming_volume = - 5 * self._max_power
#             else:
#                 if self._log['energy'][-1] == - self._max_power:
#                     max_production = - self._max_power
#                     coming_volume = - 5 * self._max_power
#                 else:
#                     corresponding_time, corresponding_power = get_timestep_of_data(self.cold_startup, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
#                     next_timestep = corresponding_time + 1
#                     if not next_timestep > max(self.cold_startup["time_step"]):
#                         max_production = - get_data_at_timestep(self.cold_startup, next_timestep)
#                         coldStartUpIndex = find_nearest_point(self.cold_startup["time_step"], ceil(next_timestep))
#                         for index in range(coldStartUpIndex, 5 + coldStartUpIndex):
#                             if index <= len(self.cold_startup["energy"]) - 1:
#                                 coming_volume -= self.cold_startup["energy"][index]
#                             else:
#                                 coming_volume -= self._max_power
#                     else:
#                         max_production = - self._max_power
#                         coming_volume = - 5 * self._max_power
                



            # inside_flag, nearest_value = check_distance(self.cold_startup["energy"], - self._log["energy"][-1])
            # if inside_flag:  # a standard cold start-up (E_accorded == corresponding max_production at timestep 'i')
            #     coldStartUpIndex = self.cold_startup["energy"].index(nearest_value)
            #     if coldStartUpIndex < len(self.cold_startup["energy"]) - 1:
            #         max_production = - self.cold_startup["energy"][coldStartUpIndex + 1]
            #         for index in range(coldStartUpIndex + 1, len(self.cold_startup["energy"])):
            #             coming_volume -= self.cold_startup["energy"][index]
            #         remaining_steps = 5 - (len(self.cold_startup["energy"]) - 1 - coldStartUpIndex)
            #         if remaining_steps > 0:
            #             for index in range(remaining_steps):
            #                 coming_volume -= self._max_power
            #     else:
            #         max_production = - self._max_power
            #         coming_volume = - 5 * self._max_power
            # else:  # Energy accorded doesn't correspond to the cold start-up curve
            #     corresponding_time, corresponding_power = get_timestep_of_data(self.cold_startup, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
            #     next_timestep = corresponding_time + 1
            #     if not next_timestep > max(self.cold_startup["time_step"]):
            #         max_production = - get_data_at_timestep(self.cold_startup, next_timestep)
            #         coldStartUpIndex = find_nearest_point(self.cold_startup["time_step"], ceil(next_timestep))
            #         # coldStartUpIndex = self.cold_startup["time_step"].index(ceil(next_timestep))
            #         for index in range(coldStartUpIndex, len(self.cold_startup["energy"])):
            #             coming_volume -= self.cold_startup["energy"][index]
            #         remaining_steps = 5 - (len(self.cold_startup["energy"]) - coldStartUpIndex)
            #         if remaining_steps > 0:
            #             for index in range(remaining_steps):
            #                 coming_volume -= self._max_power
            #     else:
            #         max_production = - self._max_power
            #         coming_volume = - 5 * self._max_power

        # else:
#             raise Exception("State assignment to the log dict attribute is not correct !")
#
#         print(f"i am min energy : {min_production}")
#         print(f"i am max energy : {max_production}")
#         print(f"i am coming volume : {coming_volume}")
#
#
#     def react(self, current_time, current_energy):
#         self._log["time_step"].append(int(current_time))
#
#         if self._log["time_step"][-1] == 0:  # initial conditions
#             self._log["state"] = []
#             self._log["energy"] = []
#             self.cold_startup_signal_time = None
#
#         self._log["energy"].append(float(current_energy))
#         if self._log["energy"][-1] == 0:  # if no energy was accorded (no production)
#             self._log["state"].append("idle")
#             self.cold_startup_signal_time = None
#
#         elif self._log["energy"][-1] == - self._max_power:  # the biomass plant generates nominal energy
#             self._log["state"].append("nominal_state")
#             self.cold_startup_signal_time = None
#
#         else:  # the biomass plant generates energy during the dynamic phase
#             self._log["state"].append("cold_startup")
#             if self.cold_startup_signal_time is None:
#                 self.cold_startup_signal_time = current_time
#
#         print(f"i am what happened : {self._log}")
#
# def find_nearest_point(time_list: List, time_point: int) -> Optional[int]:
#     if time_point in time_list:
#         return time_list.index(time_point)
#     else:
#         while time_point <= max(time_list):
#             time_point += 1
#             if time_point in time_list:
#                 return time_list.index(time_point)
#     return None

#     def update(self, current_timestep):
#         min_production = 0.0
#
#         if current_timestep == 0:  # initial conditions
#             self._log["state"].append(self._initial_conditions["initial_state"])
#             if self._log["state"][-1] == "cold_startup":
#                 self.cold_startup_flag = True
#                 self.warm_startup_flag = False
#                 self._log["energy"].append(- self._initial_conditions["initial_energy"])
#             elif self._log["state"][-1] == "warm_startup":
#                 self.cold_startup_flag = False
#                 self.warm_startup_flag = True
#                 self._log["energy"].append(- self._initial_conditions["initial_energy"])
#
#         if self._log["state"][-1] == "idle" or self._log["state"][-1] == "shut_down":
#             max_production = - 0.01 * self._max_power
#             coming_volume = - 0.01 * self._max_power
#
#         elif self._log["state"][-1] == "nominal_state":
#             max_production = - self._max_power
#             coming_volume = - 5 * self._max_power
#
#         if self.cold_startup_flag:  # a cold startup is triggered
#             coming_volume = 0.0
#             inside_flag, nearest_value = check_distance(self.cold_startup["energy"], - self._log["energy"][-1])
#             if inside_flag:  # a standard cold start-up (E_accorded == max_production)
#                 coldStartUpIndex = self.cold_startup["energy"].index(nearest_value)
#                 if coldStartUpIndex < len(self.cold_startup["energy"]) - 1:
#                     max_production = - self.cold_startup["energy"][coldStartUpIndex + 1]
#                     for index in range(coldStartUpIndex + 1, len(self.cold_startup["energy"])):
#                         coming_volume -= self.cold_startup["energy"][index]
#                     remaining_steps = 5 - (len(self.cold_startup["energy"]) - 1 - coldStartUpIndex)
#                     if remaining_steps > 0:
#                         for index in range(remaining_steps):
#                             coming_volume -= self._max_power
#                 else:
#                     max_production = - self._max_power
#                     coming_volume = - 5 * self._max_power
#             else:  # Energy accorded doesn't correspond to the cold start-up curve
#                 corresponding_time, corresponding_power = get_timestep_of_data(self._coldStartUp, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
#                 next_timestep = corresponding_time + 1
#                 if not next_timestep > max(self._coldStartUp["time"]):
#                     # trapezoidal intergation
#                     # max_production = - ((get_data_at_timestep(self._coldStartUp, next_timestep) + corresponding_power) / 2) * self._max_power
#                     # calcul normal
#                     max_production = - get_data_at_timestep(self._coldStartUp, next_timestep) * self._max_power
#                     coldStartUpIndex = self.cold_startup["time_step"].index(ceil(next_timestep))
#                     for index in range(coldStartUpIndex, len(self.cold_startup["energy"])):
#                         coming_volume -= self.cold_startup["energy"][index]
#                     remaining_steps = 5 - (len(self.cold_startup["energy"]) - coldStartUpIndex)
#                     if remaining_steps > 0:
#                         for index in range(remaining_steps):
#                             coming_volume -= self._max_power
#                 else:
#                     max_production = - self._max_power
#                     coming_volume = - 5 * self._max_power
#
#         elif self.warm_startup_flag:  # a warm startup is triggered
#             coming_volume = 0.0
#             inside_flag, nearest_value = check_distance(self.warm_startup["energy"], - self._log["energy"][-1])
#             if inside_flag:  # a standard warm start-up (E_accorded == max_production)
#                 warmStartUpIndex = self.warm_startup["energy"].index(nearest_value)
#                 if warmStartUpIndex < len(self.warm_startup["energy"]) - 1:
#                     max_production = - self.warm_startup["energy"][warmStartUpIndex + 1]
#                     for index in range(warmStartUpIndex + 1, len(self.warm_startup["energy"])):
#                         coming_volume -= self.warm_startup["energy"][index]
#                     remaining_steps = 5 - (len(self.warm_startup["energy"]) - 1 - warmStartUpIndex)
#                     if remaining_steps > 0:
#                         for index in range(remaining_steps):
#                             coming_volume -= self._max_power
#                 else:
#                     max_production = - self._max_power
#                     coming_volume = - 5 * self._max_power
#             else:  # Energy accorded doesn't correspond to the warm start-up curve
#                 corresponding_time, corresponding_power = get_timestep_of_data(self._warmStartUp, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
#                 next_timestep = corresponding_time + 1
#                 if not next_timestep > max(self._warmStartUp["time"]):
#                     #  trapezoidal integration
#                     # max_production = - ((get_data_at_timestep(self._warmStartUp, next_timestep) + corresponding_power) / 2) * self._max_power
#                     # calcul normal
#                     max_production = - get_data_at_timestep(self._warmStartUp, next_timestep) * self._max_power
#                     warmStartUpIndex = self.warm_startup["time_step"].index(ceil(next_timestep))
#                     for index in range(warmStartUpIndex, len(self.warm_startup["energy"])):
#                         coming_volume -= self.warm_startup["energy"][index]
#                     remaining_steps = 5 - (len(self.warm_startup["energy"]) - warmStartUpIndex)
#                     if remaining_steps > 0:
#                         for index in range(remaining_steps):
#                             coming_volume -= self._max_power
#                 else:
#                     max_production = - self._max_power
#                     coming_volume = - 5 * self._max_power
#
#         print(f"i am the upper bound of biomass production : {max_production}")
#         print(f"i am the coming volume : {coming_volume}")
#
#     def react(self, current_timestep, energy_accorded):
#         self._log["time_step"].append(int(current_timestep))
#         if self._log["time_step"][-1] == 0:  # initial conditions
#             self._log["state"] = []
#             self._log["energy"] = []
#             self.cold_startup_flag = False
#             self.warm_startup_flag = False
#         self._log["energy"].append(float(energy_accorded))
#         if self._log["energy"][-1] == 0:  # if no energy was accorded (no production)
#             self.cold_startup_flag = False
#             self.warm_startup_flag = False
#             if len(self._log["energy"]) < 2:  # first start up
#                 self._log["state"].append("idle")
#             else:
#                 if self._log["energy"][-2] == 0:  # at least 2 time steps since shut-down
#                     self._log["state"].append("idle")
#                 else:  # the biomass plant was just shut-down for one time step
#                     if "nominal_state" in self._log['state']:
#                         self._log["state"].append("shut_down")
#                     else:
#                         self._log["state"].append("idle")
#
#         elif self._log["energy"][-1] == - self._max_power:  # the biomass plant generates nominal energy
#             self._log["state"].append("nominal_state")
#             self.cold_startup_flag = False
#             self.warm_startup_flag = False
#
#         else:  # the biomass plant generates energy during the dynamic phase
#             if len(self._log['state']) > 0:
#                 if self._log['state'][-1] == "nominal_state":  # adjusting the generated power from the nominal state
#                     if abs(self._log["energy"][-1]) <= 0.3 * self._max_power:  # a cold startup is needed
#                         self._log["state"].append("cold_startup")
#                         self.cold_startup_flag = True
#                         self.warm_startup_flag = False
#                     else:  # a warm startup is needed
#                         self._log["state"].append("warm_startup")
#                         self.cold_startup_flag = False
#                         self.warm_startup_flag = True
#
#                 elif self._log['state'][-1] == "cold_startup" or self._log['state'][-1] == "idle":  # conditions to perform a cold startup
#                     self._log["state"].append("cold_startup")
#                     self.cold_startup_flag = True
#                     self.warm_startup_flag = False
#
#                 elif self._log['state'][-1] == "warm_startup" or self._log['state'][-1] == "shut_down":  # conditions to perform a warm startup
#                     self._log["state"].append("warm_startup")
#                     self.cold_startup_flag = False
#                     self.warm_startup_flag = True
#             else:  # Only for the first iteration
#                 if abs(self._log["energy"][-1]) <= 0.3 * self._max_power:  # a cold startup is needed
#                     self._log["state"].append("cold_startup")
#                     self.cold_startup_flag = True
#                     self.warm_startup_flag = False
#                 else:  # a warm startup is needed
#                     self._log["state"].append("warm_startup")
#                     self.cold_startup_flag = False
#                     self.warm_startup_flag = True
#         print(f"i am what happened : {self._log}")




# #     def update(self):
# #         min_production = 0.0
# #         if len(self._log["state"]) > 0:
# #             if self._log["state"][-1] == "idle" or self._log["state"][-1] == "shut_down":
# #                 max_production = - 0.01 * self._max_power
# #                 coming_volume = - 0.01 * self._max_power
# #
# #             elif self._log["state"][-1] == "nominal_state":
# #                 max_production = - self._max_power
# #                 coming_volume = - 5 * self._max_power
# #         else:
# #             max_production = - 0.01 * self._max_power
# #             coming_volume = - 0.01 * self._max_power
# #
# #         if self.cold_startup_flag:  # a cold startup is triggered
# #             coming_volume = 0.0
# #             inside_flag, nearest_value = check_distance(self.cold_startup["energy"], - self._log["energy"][-1])
# #             if inside_flag:  # a standard cold start-up
# #                 coldStartUpIndex = self.cold_startup["energy"].index(nearest_value)
# #                 if coldStartUpIndex < len(self.cold_startup["energy"]) - 1:
# #                     max_production = - self.cold_startup["energy"][coldStartUpIndex + 1]
# #                     for index in range(coldStartUpIndex + 1, len(self.cold_startup["energy"])):
# #                         coming_volume -= self.cold_startup["energy"][index]
# #                     remaining_steps = 5 - (len(self.cold_startup["energy"]) - 1 - coldStartUpIndex)
# #                     if remaining_steps > 0:
# #                         for index in range(remaining_steps):
# #                             coming_volume -= self._max_power
# #                 else:
# #                     max_production = - self._max_power
# #                     coming_volume = - 5 * self._max_power
# #             else:  # Energy accorded doesn't correspond to the cold start-up curve
# #                 corresponding_time = get_timestep_of_data(self._coldStartUp, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
# #                 upper_timestep = ceil(corresponding_time)
# #                 if not upper_timestep > max(self._coldStartUp["time"]):
# #                     max_production = - get_data_at_timestep(self._coldStartUp, upper_timestep) * self._max_power
# #                     coldStartUpIndex = self.cold_startup["time_step"].index(upper_timestep)
# #                     for index in range(coldStartUpIndex, len(self.cold_startup["energy"])):
# #                         coming_volume -= self.cold_startup["energy"][index]
# #                     remaining_steps = 5 - (len(self.cold_startup["energy"]) - coldStartUpIndex)
# #                     if remaining_steps > 0:
# #                         for index in range(remaining_steps):
# #                             coming_volume -= self._max_power
# #                 else:
# #                     max_production = - self._max_power
# #                     coming_volume = - 5 * self._max_power
# #
# #         elif self.warm_startup_flag:  # a warm startup is triggered
# #             coming_volume = 0.0
# #             inside_flag, nearest_value = check_distance(self.warm_startup["energy"], - self._log["energy"][-1])
# #             if inside_flag:  # a standard warm start-up
# #                 warmStartUpIndex = self.warm_startup["energy"].index(nearest_value)
# #                 if warmStartUpIndex < len(self.warm_startup["energy"]) - 1:
# #                     max_production = - self.warm_startup["energy"][warmStartUpIndex + 1]
# #                     for index in range(warmStartUpIndex + 1, len(self.warm_startup["energy"])):
# #                         coming_volume -= self.warm_startup["energy"][index]
# #                     remaining_steps = 5 - (len(self.warm_startup["energy"]) - 1 - warmStartUpIndex)
# #                     if remaining_steps > 0:
# #                         for index in range(remaining_steps):
# #                             coming_volume -= self._max_power
# #                 else:
# #                     max_production = - self._max_power
# #                     coming_volume = - 5 * self._max_power
# #             else:  # Energy accorded doesn't correspond to the warm start-up curve
# #                 corresponding_time = get_timestep_of_data(self._warmStartUp, - self._log["energy"][-1], self._max_power)  # the time step corresponding to the energy accorded in ti-1
# #                 upper_timestep = ceil(corresponding_time)
# #                 if not upper_timestep > max(self._warmStartUp["time"]):
# #                     max_production = - get_data_at_timestep(self._warmStartUp, upper_timestep) * self._max_power
# #                     warmStartUpIndex = self.warm_startup["time_step"].index(upper_timestep)
# #                     for index in range(warmStartUpIndex, len(self.warm_startup["energy"])):
# #                         coming_volume -= self.warm_startup["energy"][index]
# #                     remaining_steps = 5 - (len(self.warm_startup["energy"]) - warmStartUpIndex)
# #                     if remaining_steps > 0:
# #                         for index in range(remaining_steps):
# #                             coming_volume -= self._max_power
# #                 else:
# #                     max_production = - self._max_power
# #                     coming_volume = - 5 * self._max_power
# #
# #         print(f"i am the min energy : {min_production}")
# #         print(f"i am the max energy : {max_production}")
# #         print(f"i am the coming volume : {coming_volume}")
# # #
# # # # #         if self.cold_startup_flag:
# # # # #             startup_time = self._buffer["cold_startup"]
# # # # #             if current_time == startup_time + 1:
# # # # #                 max_production = - get_data_at_timestep(self._coldStartUp, 1) * self._max_power
# # # # #                 coming_volume = - (get_data_at_timestep(self._coldStartUp, 1) + get_data_at_timestep(self._coldStartUp, 2) + get_data_at_timestep(self._coldStartUp, 3) + get_data_at_timestep(self._coldStartUp, 4) + 1) * self._max_power
# # # # #             elif current_time == startup_time + 2:
# # # # #                 max_production = - get_data_at_timestep(self._coldStartUp, 2) * self._max_power
# # # # #                 coming_volume = - (get_data_at_timestep(self._coldStartUp, 2) + get_data_at_timestep(self._coldStartUp, 3) + get_data_at_timestep(self._coldStartUp, 4) + 2) * self._max_power
# # # # #             elif current_time == startup_time + 3:
# # # # #                 max_production = - get_data_at_timestep(self._coldStartUp, 3) * self._max_power
# # # # #                 coming_volume = - (get_data_at_timestep(self._coldStartUp, 3) + get_data_at_timestep(self._coldStartUp, 4) + 3) * self._max_power
# # # # #             elif current_time == startup_time + 4:
# # # # #                 max_production = - get_data_at_timestep(self._coldStartUp, 4) * self._max_power
# # # # #                 coming_volume = - (get_data_at_timestep(self._coldStartUp, 4) + 4) * self._max_power
# # # # #             else:
# # # # #                 max_production = - self._max_power
# # # # #                 coming_volume = - 5 * self._max_power
# # # # #
# # # # #         elif self.warm_startup_flag:
# # # # #             startup_time = self._buffer["warm_startup"]
# # # # #             if current_time == startup_time + 1:
# # # # #                 max_production = - get_data_at_timestep(self._warmStartUp, 1) * self._max_power
# # # # #                 coming_volume = - (get_data_at_timestep(self._warmStartUp, 1) + 4) * self._max_power
# # # # #             else:
# # # # #                 max_production = - self._max_power
# # # # #                 coming_volume = - 5 * self._max_power
# # # # #
# # # # #         else:  # idle
# # # # #             max_production = - 0.01 * self._max_power
# # # # #             coming_volume = - 0.01 * self._max_power
# # # # #
# # # # #         print(f"The minimum energy wanted by the biomass plant is : {min_production}")
# # # # #         print(f"The maximum energy wanted by the biomass plant is : {max_production}")
# # # # #         print(f"The expected coming volume of the biomass plant is : {coming_volume}")
# # # # #
# #     def react(self, current_time, energy_accorded):
# #         self._log["time_step"].append(current_time)
# #         self._log["energy"].append(energy_accorded)
# #
# #         if self._log["energy"][-1] == 0:  # if no energy was accorded (no production)
# #             self.cold_startup_flag = False
# #             self.warm_startup_flag = False
# #             if len(self._log["energy"]) < 2:  # first start up
# #                 self._log["state"].append("idle")
# #             else:
# #                 if self._log["energy"][-2] == 0:  # at least 2 time steps since shut-down
# #                     self._log["state"].append("idle")
# #                 else:  # the biomass plant was just shut-down for one time step
# #                     self._log["state"].append("shut_down")
# #
# #         elif self._log["energy"][-1] == - self._max_power:  # the biomass plant generates nominal energy
# #             self._log["state"].append("nominal_state")
# #             self.cold_startup_flag = False
# #             self.warm_startup_flag = False
# #
# #         else:  # the biomass plant generates energy during the dynamic phase
# #             if len(self._log['state']) > 0:
# #                 if self._log['state'][-1] == "nominal_state":  # adjusting the generated power from the nominal state
# #                     if abs(self._log["energy"][-1]) <= 0.3 * self._max_power:  # a cold startup is needed
# #                         self._log["state"].append("cold_startup")
# #                         self.cold_startup_flag = True
# #                         self.warm_startup_flag = False
# #                     else:  # a warm startup is needed
# #                         self._log["state"].append("warm_startup")
# #                         self.cold_startup_flag = False
# #                         self.warm_startup_flag = True
# #                 elif self._log['state'][-1] == "cold_startup" or self._log['state'][-1] == "idle":  # conditions to perform a cold startup
# #                     self._log["state"].append("cold_startup")
# #                     self.cold_startup_flag = True
# #                     self.warm_startup_flag = False
# #                 elif self._log['state'][-1] == "warm_startup" or self._log['state'][-1] == "shut_down":  # conditions to perform a warm startup
# #                     self._log["state"].append("warm_startup")
# #                     self.cold_startup_flag = False
# #                     self.warm_startup_flag = True
# #             else:
# #                 self._log["state"].append("cold_startup")
# #                 self.cold_startup_flag = True
# #                 self.warm_startup_flag = False
# #
# #         print(f"i am the log of everything that happened {self._log}")
# # #
# # # # #         print(f"What was accorded is {energy_accorded}")
# # # # #         if energy_accorded != 0.0:
# # # # #             if current_time - self._buffer["last_stopped"] <= 1 or self.warm_startup_flag:
# # # # #                 self.warm_startup_flag = True
# # # # #                 if not "warm_startup" in self._buffer:
# # # # #                     self._buffer["warm_startup"] = current_time
# # # # #                 print(f"The energy accorded is {energy_accorded} and a warm startup is triggered at the {self._buffer["warm_startup"]} !")
# # # # #             else:
# # # # #                 self.cold_startup_flag = True
# # # # #                 if not "cold_startup" in self._buffer:
# # # # #                     self._buffer["cold_startup"] = current_time
# # # # #                 self._buffer["last_stopped"] = 0
# # # # #                 print(f"The energy accorded is {energy_accorded} and a cold startup is triggered at the {self._buffer["cold_startup"]} !")
# # # # #         else:
# # # # #             if "cold_startup" in self._buffer:
# # # # #                 print(f"The energy accorded is {energy_accorded} and a shut-down is triggered at the {current_time - self._buffer["cold_startup"]} after cold start-up !")
# # # # #                 self.cold_startup_flag = False
# # # # #                 self._buffer.pop("cold_startup")
# # # # #                 self._buffer["last_stopped"] = current_time
# # # # #             elif "warm_startup" in self._buffer:
# # # # #                 print(f"The energy accorded is {energy_accorded} and a shut-down is triggered at the {current_time - self._buffer["warm_startup"]} after warm start-up !")
# # # # #                 self.warm_startup_flag = False
# # # # #                 self._buffer.pop("warm_startup")
# # # # #                 self._buffer["last_stopped"] = current_time
# # # # #
# # # # #
# # #
# # def check_distance(myList: List, myElement, precision: float=1e-6):
# #     myFlag = False
# #     my_element = None
# #     if myElement in myList:
# #         myFlag = True
# #         my_element = myElement
# #     else:
# #         for element in myList:
# #             if abs(element - myElement) < precision:
# #                 myFlag = True
# #                 my_element = element
# #                 break
# #     return myFlag, my_element
# #
# # def get_data_at_timestep(df: dict, timestep: int):
# #     """
# #     Give back the value of %Pth as a function of the timestep using interpolation (if it doesn't already exist in the data).
# #     """
# #     # Check if the timestep exists in the DataFrame
# #     if timestep in df['time']:
# #         return df['power'][df['time'].index(timestep)]
# #     else:
# #         # If timestep does not exist, interpolate between the nearest timesteps
# #         lower_timestep = max((t for t in df["time"] if t < timestep), default=None)
# #         upper_timestep = min((t for t in df["time"] if t > timestep), default=None)
# #
# #         # Check if lower and upper timesteps exist
# #         if not lower_timestep or not upper_timestep:
# #             raise ValueError(f"Timestep {timestep} is out of bounds for interpolation.")
# #
# #         # Get corresponding data for lower and upper timesteps
# #         lower_data = df['power'][df['time'].index(lower_timestep)]
# #         upper_data = df['power'][df['time'].index(upper_timestep)]
# #
# #         # Perform linear interpolation
# #         interpolated_value = lower_data + (upper_data - lower_data) * (timestep - lower_timestep) / (upper_timestep - lower_timestep)
# #         interpolated_value /= 100
# #         return interpolated_value
# #
# #
# # def get_timestep_of_data(df: dict, out_power: float, max_power: float):
# #     """
# #     Give back the time step corresponding to the value of %Pth using interpolation (if it doesn't already exist in the data).
# #     """
# #     out_power /= max_power
# #     out_power *= 100
# #     # Check if the timestep exists in the DataFrame
# #     if out_power in df['power']:
# #         return df['time'][df['power'].index(out_power)]
# #     else:
# #         # If out_power does not exist, interpolate between the nearest values
# #         lower_data = max((d for d in df["power"] if d < out_power), default=None)
# #         upper_data = min((d for d in df["power"] if d > out_power), default=None)
# #         # Check if lower and upper timesteps exist
# #         if not lower_data or not upper_data:
# #             raise ValueError(f"Power {out_power} is out of bounds for interpolation.")
# #         # Get corresponding data for lower and upper timesteps
# #         lower_timestep = df['time'][df['power'].index(lower_data)]
# #         upper_timestep = df['time'][df['power'].index(upper_data)]
# #         # Perform linear interpolation
# #         interpolated_value = lower_timestep + (upper_timestep - lower_timestep) * (out_power - lower_data) / (upper_data - lower_data)
# #         return interpolated_value
# # #
# # #
# # #
# # #
# my_incinerator = DummyClass({"device": "Biomass_2_ThP"}, {"max_power": 1300, "recharge_quantity": 1500, "autonomy": 8, "initial_energy": 400}, "D:/dossier_y23hallo/PycharmProjects/peacefulness/lib/Subclasses/Device/BiomassGasPlantAlternative/BiomassGasPlantAlternative.json", 1)
# # # # # print(my_incinerator._coldStartUp)
# # # # # # # my_incinerator.print_my_data(0)
# # # # # # my_incinerator.print_my_data(5)
# # # # #
# simulation_dict = {'time': [], 'energy_accorded': []}
# simulation_dict["energy_accorded"].extend([-400, 0, 0, -13, -19.655127574397902, -155.47653950502414, -281.429191432779, -407.38184336053314,
#                                            -670.12970621042, -932.877569060307, -1195.6254319101931,
#                                            -1300, -1300, -1300, -1300, 0, -13, -15, -27, -100, -140, -200, -250, -300,
#                                            -390, -400, -450, -520, -670, -750,-830, -950, -971.5642211585694, -1200,
#                                            -1300, -1300, -700, -250, 0])
# simulation_dict['time'].extend(np.arange(0, len(simulation_dict["energy_accorded"]), 1))
# # # #-155.47653950502414
# for i in range(len(simulation_dict["time"])):
#     print(f"\n at the iteration {i}")
#     print(f"i am energy accorded {simulation_dict["energy_accorded"][i]}")
#     my_incinerator.update(simulation_dict["time"][i])
#     my_incinerator.react(simulation_dict["time"][i], simulation_dict["energy_accorded"][i])
# # #
# # #
# # # # ma_liste = ["idle", "idle", "cold_startup", "cold_startup", "cold_startup", "cold_startup", "cold_startup", "nominal_state", "nominal_state", "shut_down", "warm_startup", "warm_startup", "warm_startup", "nominal_state"]
# # #
# # # # def find_last_occurrence(lst, label):
# # # #     relevant_index = None
# # # #     for i in range(len(lst) - 1, -1, -1):
# # # #         if lst[i] == label:
# # # #             relevant_index = i
# # # #             break
# # # #     if relevant_index is not None:
# # # #         for j in range(relevant_index - 1, -1, -1):
# # # #             if lst[j] != label:
# # # #                 return j + 1
# # # #     return None
# # #
# # # # print(find_last_occurrence(ma_liste, "nominal_state"))
# # #
# # # # from math import ceil
# # # #
# # # # print(ceil(1.3))
# # #
# # myData = {'time': [0, 0.85759257, 0.900218005627907, 0.942843441255814, 0.985468876883721, 1.028094312511628, 1.0707197481395347, 1.113345183767442, 1.1559706193953487, 1.1985960550232555, 1.2412214906511627, 1.2838469262790695, 1.3264723619069767, 1.3690977975348837, 1.4117232331627907, 1.4543486687906977, 1.496974104418605, 1.5395995400465114, 1.5822249756744189, 1.6248504113023254, 1.6674758469302324, 1.7101012825581394, 1.7527267181860464, 1.7953521538139534, 1.8379775894418604, 1.8806030250697676, 1.9232284606976744, 1.9658538963255812, 2.008479331953488, 2.051104767581396, 2.093730203209302, 2.136355638837209, 2.178981074465116, 2.221606510093024, 2.26423194572093, 2.306857381348837, 2.349482816976744, 2.3921082526046518, 2.434733688232558, 2.477359123860465, 2.519984559488372, 2.562609995116279, 2.6052354307441856, 2.647860866372093, 2.690486302, 2.733111737627907, 2.7757371732558136, 2.818362608883721, 2.860988044511628, 2.903613480139535, 2.9462389157674416, 2.988864351395349, 3.031489787023256, 3.0741152226511628, 3.116740658279069, 3.1593660939069763, 3.2019915295348835, 3.2446169651627903, 3.287242400790697, 3.3298678364186043, 3.3724932720465115, 3.4151187076744183, 3.457744143302325, 3.5003695789302323, 3.5429950145581395, 3.5856204501860462, 3.628245885813953, 3.67087132144186, 3.713496757069767, 3.756122192697674, 3.798747628325581, 3.841373063953488, 3.883998499581395, 3.926623935209302, 3.969249370837209, 4.011874806465116, 4.054500242093023, 4.09712567772093, 4.1397511133488365, 4.182376548976744, 4.225001984604651, 4.267627420232557, 4.310252855860465, 4.352878291488372, 4.395503727116279, 4.438129162744186, 4.4807545983720924, 4.523380034],
# #           'power': [0.0, 0.5891783888143938, 0.8546431553272257, 1.1272752850509922, 1.4090044093672502, 1.71093367559132, 2.056833486300276, 2.4342844802257737, 2.858809365661944, 3.327424147619423, 3.7924823279822593, 4.253835244006937, 4.753303671548963, 5.256340787344144, 5.760104866016135, 6.26732690901904, 6.750404234964405, 7.170297245899936, 7.585549374846935, 8.008852329523913, 8.446134429836908, 8.901621612534127, 9.191103633224042, 9.695543913682906, 10.187632874482649, 10.693667604358827, 11.17422178292746, 11.533438777411265, 12.065593531039216, 12.60564681946244, 13.154506105770766, 13.702589843505356, 14.182817036364815, 14.693779530295028, 15.196737083729737, 15.71373375717541, 16.2942235161964, 16.87016870655116, 17.446126740584997, 17.98951271448331, 18.588050565789803, 19.206596512366477, 19.799185064523144, 20.362554218073296, 20.979622579905968, 21.685590915742445, 22.639962876951188, 24.10166920441168, 25.69610740868173, 27.3436796078332, 29.05180330603888, 30.870171664283564, 32.65736225888914, 34.492132863773406, 36.34270338325759, 38.330873827308, 40.33389006212003, 42.58759766028464, 44.97704645555996, 47.5043851930794, 50.10039753344784, 52.45965620608399, 54.97351221998439, 57.70919563469312, 60.32611451202009, 62.98310124176141, 65.82610069156743, 68.6666786659625, 71.49027307336097, 74.47138123762693, 77.42132102831924, 80.38320410428365, 83.46818539191064, 86.60975841639996, 89.73863180733504, 92.83332102918204, 94.80575564070192, 96.01530110413512, 97.04626325230596, 97.66813376711391, 97.77185324392212, 97.77316098764844, 97.7744687478856, 97.7757765452272, 97.77708436870724, 97.7783922142016, 97.77970009132348, 100.0]}
# # # # a = (2.5911028385162354 / 1300) * 100
# # # # if a in myData["power"]:
# # # #     print(myData["power"].index(a))
# # # # else:
# # # #     lower_data = max((d for d in myData["power"] if d < a), default=None)
# # # #     upper_data = min((d for d in myData["power"] if d > a), default=None)
# # # # print(lower_data)
# # # # print(upper_data)
# # #
# # # a = - 155.47653198242188
# # # a /= -1300
# # # a *= 100
# # #
# # # lower_data = max((d for d in myData["power"] if d < a), default=None)
# # # upper_data = min((d for d in myData["power"] if d > a), default=None)
# # #
# # # print(lower_data)
# # # print(upper_data)
# #
# # from math import ceil, floor
# #
# # def check_distance(myList: list, myElement, precision: float=1e-6):
# #     myFlag = False
# #     my_element = None
# #     if myElement in myList:
# #         myFlag = True
# #         my_element = myElement
# #     else:
# #         for element in myList:
# #             if abs(element - myElement) < precision:
# #                 myFlag = True
# #                 my_element = element
# #                 break
# #     return myFlag, my_element
# #
# # def get_timestep_of_data(df: dict, out_power: float, max_power: float):
# #     """
# #     Give back the time step corresponding to the value of %Pth using interpolation (if it doesn't already exist in the data).
# #     """
# #     out_power /= max_power
# #     out_power *= 100
# #     # Check if the timestep exists in the DataFrame
# #     if out_power in df['power']:
# #         return df['time'][df['power'].index(out_power)]
# #     else:
# #         # If out_power does not exist, interpolate between the nearest values
# #         lower_data = max((d for d in df["power"] if d < out_power), default=None)
# #         upper_data = min((d for d in df["power"] if d > out_power), default=None)
# #         # Check if lower and upper timesteps exist
# #         if lower_data is None or upper_data is None:
# #             raise ValueError(f"Power {out_power} is out of bounds for interpolation.")
# #         # Get corresponding data for lower and upper timesteps
# #         lower_timestep = df['time'][df['power'].index(lower_data)]
# #         upper_timestep = df['time'][df['power'].index(upper_data)]
# #         # Perform linear interpolation
# #         interpolated_value = lower_timestep + (upper_timestep - lower_timestep) * (out_power - lower_data) / (upper_data - lower_data)
# #         return interpolated_value
# #
# # def get_data_at_timestep(df: dict, timestep: int):
# #     """
# #     Give back the value of %Pth as a function of the timestep using interpolation (if it doesn't already exist in the data).
# #     """
# #     # Check if the timestep exists in the DataFrame
# #     if timestep in df['time']:
# #         return df['power'][df['time'].index(timestep)]
# #     else:
# #         # If timestep does not exist, interpolate between the nearest timesteps
# #         lower_timestep = max((t for t in df["time"] if t < timestep), default=None)
# #         upper_timestep = min((t for t in df["time"] if t > timestep), default=None)
# #
# #         # Check if lower and upper timesteps exist
# #         if lower_timestep is None or upper_timestep is None:
# #             raise ValueError(f"Timestep {timestep} is out of bounds for interpolation.")
# #
# #         # Get corresponding data for lower and upper timesteps
# #         lower_data = df['power'][df['time'].index(lower_timestep)]
# #         upper_data = df['power'][df['time'].index(upper_timestep)]
# #
# #         # Perform linear interpolation
# #         interpolated_value = lower_data + (upper_data - lower_data) * (timestep - lower_timestep) / (upper_timestep - lower_timestep)
# #         interpolated_value /= 100
# #         return interpolated_value
# #
# #
# # max_power = 1300
# # cold_startup = {"time_step": [0, 1, 2, 3, 4, 5], "energy": [0.01, 0.015119328903383002, 0.1195973380807878, 0.31337064873887166, 0.9197118707001486, 1]}
# # warm_startup_flag = False
# # warm_startup = {"time_step": [0, 1, 2], "energy": [0.01, 0.7473570931988995, 1]}
# # log = {"time_step": [], "energy": [], "state": []}
# # for index in range(len(cold_startup["energy"])):
# #     cold_startup["energy"][index] *= max_power
# #
# # for index in range(len(warm_startup["energy"])):
# #     warm_startup["energy"][index] *= max_power
# #
# # a = -155.47653198
# #
# # print(check_distance(cold_startup["energy"], -a))
# # print(get_timestep_of_data(myData, 19.65512848, max_power))
# # print(get_data_at_timestep(myData, ceil(get_timestep_of_data(myData, 19.65512848, max_power))) * max_power)
#
# a = {("A1", "A2"): [-120, 100, 0.85]}
# for tup in a:
#     print(tup)
#

# Max consumption of heat is in February 8th

# #####################################################################################################################
# todo Running the ramping-up management case study with the rule-based strategy
#######################################################################################################################
# from os import path, chdir
# import sys
# sys.path.append(path.abspath("D:/dossier_y23hallo/PycharmProjects/peacefulness"))
# chdir("D:/dossier_y23hallo/PycharmProjects/peacefulness")
# from cases.Studies.ClusteringAndStrategy.CasesStudied.RampUpManagement.Parameters import ref_priorities_consumption, ref_priorities_production
# from cases.Studies.ClusteringAndStrategy.CasesStudied.RampUpManagement.SimulationScript import create_simulation
#
#
# comparison_simulation_length = 8760
# performance_metrics = ["heat_sink.LTH.energy_bought", "old_house.LTH.energy_bought",
#                        "new_house.LTH.energy_bought", "office.LTH.energy_bought",
#                        "biomass_plant.LTH.energy_sold", "district_heating_microgrid.energy_bought"]
# coef1 = 1
# coef2 = 1
# def performance_norm(performance_vector: dict) -> float:
#     total_outside = sum(abs(element["outside"]) for element in performance_vector["district_heating_microgrid.energy_bought"])
#     return abs(sum(performance_vector["biomass_plant.LTH.energy_sold"])) - coef1 * abs(sum(performance_vector["heat_sink.LTH.energy_bought"])) - coef2 * total_outside
#
#
# ref_datalogger = create_simulation(comparison_simulation_length, ref_priorities_consumption, ref_priorities_production, f"comparison/reference", performance_metrics)
# ref_results = {key: [] for key in performance_metrics}
# for key in performance_metrics:
#     ref_results[key] = ref_datalogger._values[key]
# # print(ref_results["district_heating_microgrid.energy_bought"])
# ref_performance = performance_norm(ref_results)
# print(f"Performance of the reference strategy: {ref_performance}")



# #####################################################################################################################
# todo Running the limited resource management case study with the rule-based strategy
#######################################################################################################################
# from cases.Studies.ClusteringAndStrategy.CasesStudied.LimitedResourceManagement.Parameters import ref_priorities_consumption, ref_priorities_production
# from cases.Studies.ClusteringAndStrategy.CasesStudied.LimitedResourceManagement.SimulationScript import create_simulation
#
#
# comparison_simulation_length = 8760
# performance_metrics = ["local_network.energy_bought_outside",
#                        "unwanted_delivery_cuts",
#                        "industrial_process.LVE.energy_bought"]
# coef1 = 2
# coef2 = 0.5
# def performance_norm(performance_vector: dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
#     return - coef1 * sum(performance_vector["local_network.energy_bought_outside"]) + sum(performance_vector["industrial_process.LVE.energy_bought"]) * coef2
#
#
# ref_datalogger = create_simulation(comparison_simulation_length, ref_priorities_consumption, ref_priorities_production, f"comparison/reference", performance_metrics)
# ref_results = {key: [] for key in performance_metrics}
# for key in performance_metrics:
#     ref_results[key] = ref_datalogger._values[key]
# ref_performance = performance_norm(ref_results)
#
# print(f"Performance of the reference strategy: {ref_performance}")



# #####################################################################################################################
# todo exploitation des résultats Ramp-Up Management & Limited-Resource Management cases
#######################################################################################################################
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# # #
#
# # cold_startup = {"time_step": [0, 1, 2, 3, 4, 5, 6, 7, 8],
# #                 "energy": [0, 0.015119328903383002, 0.1195973380807878, 0.2164839934098297, 0.31337064873887166, 0.5154843893926306, 0.7175981300463896, 0.9197118707001486, 1]}
# # for index in range(len(cold_startup["energy"])):
# #     cold_startup["energy"][index] *= 100
# # def get_score_at_episode(df: dict, timestep: int):
# #     """
# #     Give back the value of %Pth as a function of the timestep using interpolation (if it doesn't already exist in the data).
# #     """
# #     # Check if the timestep exists in the DataFrame
# #     if timestep in df['episode']:
# #         return df['score'][df['episode'].index(timestep)]
# #     else:
# #         # If timestep does not exist, interpolate between the nearest timesteps
# #         lower_timestep = max((t for t in df["episode"] if t < timestep), default=None)
# #         upper_timestep = min((t for t in df["episode"] if t > timestep), default=None)
# #
# #         # Check if lower and upper timesteps exist
# #         if lower_timestep is None or upper_timestep is None:
# #             raise ValueError(f"Timestep {timestep} is out of bounds for interpolation.")
# #
# #         # Get corresponding data for lower and upper timesteps
# #         lower_data = df['score'][df['episode'].index(lower_timestep)]
# #         upper_data = df['score'][df['episode'].index(upper_timestep)]
# #
# #         # Perform linear interpolation
# #         interpolated_value = lower_data + (upper_data - lower_data) * (timestep - lower_timestep) / (upper_timestep - lower_timestep)
# #
# #         return interpolated_value
# #
# # def get_penalty_at_episode(df: dict, timestep: int):
# #     """
# #     Give back the value of %Pth as a function of the timestep using interpolation (if it doesn't already exist in the data).
# #     """
# #     # Check if the timestep exists in the DataFrame
# #     if timestep in df['episode']:
# #         return df['penalty'][df['episode'].index(timestep)]
# #     else:
# #         # If timestep does not exist, interpolate between the nearest timesteps
# #         lower_timestep = max((t for t in df["episode"] if t < timestep), default=None)
# #         upper_timestep = min((t for t in df["episode"] if t > timestep), default=None)
# #
# #         # Check if lower and upper timesteps exist
# #         if lower_timestep is None or upper_timestep is None:
# #             raise ValueError(f"Timestep {timestep} is out of bounds for interpolation.")
# #
# #         # Get corresponding data for lower and upper timesteps
# #         lower_data = df['penalty'][df['episode'].index(lower_timestep)]
# #         upper_data = df['penalty'][df['episode'].index(upper_timestep)]
# #
# #         # Perform linear interpolation
# #         interpolated_value = lower_data + (upper_data - lower_data) * (timestep - lower_timestep) / (upper_timestep - lower_timestep)
# #
# #         return interpolated_value
#
# filepath = "D:\dossier_y23hallo\Thèse\ECOS/Ramp_up_management\plots_for_ecos"
# filename = filepath + "/" + "consoXdissipXerror_fall.csv"
# curtailment_df = pd.read_csv(filename, sep=";", decimal=",", header=0)
# curtailment_dict = curtailment_df.to_dict(orient="list")
# #
# # filename = filepath + "/" + "scoreXepisode.csv"
# # reward_df = pd.read_csv(filename, sep=";", decimal=",", header=0)
# # reward_dict = reward_df.to_dict(orient="list")
# # my_episode = np.arange(1,101,1)
# # reward = []
# # penalty_term = []
# # for episode in my_episode:
# #     reward.append(get_score_at_episode(reward_dict, episode))
# #     penalty_term.append(get_penalty_at_episode(curtailment_dict, episode))
# #
# # score = []
# # for index in range(len(my_episode)):
# #     score.append(reward[index]*8760 - penalty_term[index]*8760)
# testi = []
# test2 = []
# test3 = []
# for index in range(len(curtailment_dict["total"])):
#     test3.append(abs(curtailment_dict["abs_dissip"][index]) - abs(curtailment_dict["abs_error"][index]))
#     if abs(curtailment_dict["abs_dissip"][index]) >= abs(curtailment_dict["abs_error"][index]):
#         testi.append(curtailment_dict["abs_dissip"][index])
#         test2.append(0)
#     else:
#         testi.append(0)
#         test2.append(curtailment_dict["abs_error"][index])
# fall_time = np.arange(0, len(curtailment_dict["total"]), 1)
# # print(max(score)/ref_performance*100)
# # plt.figure(figsize=(5,5))
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# # threshold = np.empty(len(score))
# # threshold.fill(ref_performance/8760)
# plt.xlabel("Time in [Hours]")
# plt.ylabel("Energy in [kWh]")
# # plt.plot(fall_time, curtailment_dict["abs_dissip"], label="Dissipation")
# # plt.plot(fall_time, zeros_like(fall_time))
# # plt.plot(fall_time, testi, label="Dissipation minus error", linestyle='--')
# # plt.plot(fall_time, test2, label="Error minus Dissipation", linestyle='--')
# plt.plot(fall_time, test3, label="Difference", linestyle='--')
# # plt.xlim([0,8])
# # plt.plot(cold_startup["time_step"], cold_startup["energy"])
# # plt.plot(my_episode,penalty_term, label="The average cumulated penalty term obtained during an episode")
# # plt.plot(my_episode,threshold, label='Score of the rule-based strategy', linestyle="--")
# # plt.plot(my_episode,zeros_like(threshold), linestyle="--")
# plt.legend()
# # plt.show()
# # plt.tight_layout()  # Adjust layout for better spacing
# # plt.show()
# # plt.savefig("D:\dossier_y23hallo\Thèse\ECOS/rampUpLR.pdf", format="pdf", bbox_inches="tight")
#
# # # # # print(curtailment_dict.keys())
# # # # winter_time = np.arange(0, len(reward_dict["total"]), 1)
# # # # curtailment_dict["heat_load"].sort(reverse=True)
# # reward_dict["biomass"].sort(reverse=True)
# # curtailment_dict["heat_load"].sort(reverse=True)
# # curtailment_dict["total"].sort(reverse=True)
# # curtailment_dict["abs_dissip"].sort(reverse=True)
# # curtailment_dict["abs_error"].sort(reverse=True)
# # # mytime = np.arange(0, 100, 1)
# # # myzeros = np.zeros_like(mytime)
# # # penalty_time = np.arange(0,len(curtailment_dict["drl"]), 1)
# # # reward_time = np.arange(0, len(reward_dict["abs_error"]), 1)
# # # filepath = "D:\dossier_y23hallo\Thèse\ECOS\Ramp_up_management\plots_for_ecos"
# # # filename = filepath + "/" + "penaltyXepisode.csv"
# # # curtailment2_df = pd.read_csv(filename, sep=";", decimal=",", header=0)
# # # curtailment2_dict = curtailment_df.to_dict(orient="list")
# #
# # # filename = filepath + "/" + "scoreXepisode.csv"
# # # reward2_df = pd.read_csv(filename, sep=";", decimal=",", header=0)
# # # reward2_dict = reward_df.to_dict(orient="list")
# #
# # # day1 = [1633.0353769963308, 1690.9817935994265, 1664.6425133252924, 1569.8211043384085, 1543.4818240642742, 1548.749680119101, 1673.786088129305, 1737.0003607872275, 1970.1781645052508, 1755.5882035629902, 1439.5168402733775, 1155.0526133127264, 1049.695492216189, 960.1419392841321, 902.1955226810364, 881.1240984617291, 881.1240984617291, 1021.9640746364134, 841.4648314666589, 830.929119357005, 836.196975411832, 825.6612633021782, 799.3219830280439, 684.8212871274936]
# # # my_time1 = np.arange(0, len(day1), 1)
# # # day2 = [1348.5711500356797, 1327.4997258163721, 1327.4997258163721, 1385.4461424194678, 1448.6604150773906, 1564.5532482835815, 1747.5360728968813, 1705.393224458266, 1864.8210434087132, 1571.2132416440495, 1297.284726793052, 1112.9097648741115, 975.9455074486127, 896.9276666262095, 849.5169621327677, 844.249106077941, 886.3919545165559, 1085.1783472943362, 1004.7683691662919, 1125.9290584273099, 1204.9468992497132, 1299.768308236597, 1389.3218611686539, 1327.4997258163721]
# # # my_time2 = np.arange(0, len(day2), 1)
# #
# #
# #
# # plt.rcParams["font.family"] = "Times New Roman"
# # plt.rcParams["font.size"] = 12
# # # # plt.plot(winter_time, reward_dict["heat_load"], label="Space heating demand")
# # # # plt.plot(winter_time, reward_dict["total"], label="Heat consumption including dissipation", linestyle="--")
# # # # plt.plot(my_time1, day1, label="Heat Consumption Representative Day For The Winter Season")
# # # # plt.plot(my_time2, day2, label="Heat Consumption Representative Day For The Fall Season")
# # # plt.plot(reward_dict["episode"], reward_dict["score"], label="The average cumulated rewards")
# # plt.plot(fall_time, curtailment_dict["heat_load"], label="Space heating demand")
# # plt.plot(fall_time, curtailment_dict["total"], label="Heat consumption including dissipation of biomass energy", linestyle="--")
# # plt.plot(fall_time, reward_dict["biomass"], label="Biomass heat production")
# # plt.plot(fall_time, curtailment_dict["abs_dissip"], label="Biomass heat dissipated")
# # plt.plot(fall_time, curtailment_dict["abs_error"], label="Absolute error w.r.t energy conservation", linestyle="--")
# # # # plt.plot(reward_dict, reward_dict["abs_error"], label="Absolute error", linestyle="--")
# # # # plt.plot(curtailment_dict["time"], curtailment_dict["energy"], label="Heating Consumption Profile - Winter Season")
# # # # plt.plot(reward_dict["time"], reward_dict["energy"], label="Heating Consumption Profile - Fall Season", linestyle="--")
# # # plt.plot(mytime, myzeros, linestyle ="--")
# # # # # plt.plot(winter_time, reward_dict["total"], label="Heat consumption including dissipation", linestyle="--")
# # # # # plt.plot(winter_time, reward_dict["dissip"], label="Heat dissipated")
# # # # # plt.plot(winter_time, reward_dict["abs_error"], label="Absolute error", linestyle="--")
# # plt.xlabel("Time in [Hours]")
# # plt.ylabel("Energy in [MWh]")
# # plt.legend()
# plt.grid(True)
# # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))  # Create two subplots side by side
# # #
# # # Plot fall data in the first subplot
# # ax1.plot(reward_dict["episode"], reward_dict["score"], label="The average cumulated rewards")
# # ax1.plot(curtailment_dict["episode"], curtailment_dict["penalty"], label="The constraint penalty term")
# # # ax1.plot(mytime, myzeros, linestyle="--")
# # ax1.set_xlabel("Training Episodes")
# # # ax1.set_ylabel("Energy in [kWh]")
# # ax1.set_title("Limited Resource Management - Case Study")
# # # ax1.grid(True)
# # ax1.legend()
# #
# # # Plot winter data in the second subplot
# # ax2.plot(reward2_dict["episode"], reward2_dict["score"], label="The average cumulated rewards")
# # ax2.plot(curtailment2_dict["episode"], curtailment2_dict["penalty"], label="The constraint penalty term")
# # ax2.plot(mytime, myzeros, linestyle="--")
# # ax2.set_xlabel("Training Episodes")
# # # ax2.set_ylabel("Energy in [kWh]")
# # ax2.set_title("Ramp Up Management - Case Study")
# # # ax2.grid(True)
# # ax2.legend()
#
# plt.tight_layout()  # Adjust layout for better spacing
# # plt.savefig("D:\dossier_y23hallo\Thèse\ECOS/Cold_StartUp.pdf", format="pdf", bbox_inches="tight")
# plt.show()


# #####################################################################################################################
# todo Running the HEMS case study for the SDEWES conference
#######################################################################################################################
from cases.Studies.SDEWES.Parameters import ref_priorities_consumption, ref_priorities_production
from cases.Studies.SDEWES.SimulationScript import create_simulation
from cases.Studies.SDEWES.export_expert_data import *

# my memory class
path_to_export = "cases/Studies/SDEWES/Results"

comparison_simulation_length = 8760
performance_metrics = ["mirror_home_aggregator.energy_bought_outside", "mirror_home_aggregator.energy_sold_outside"]
coef1 = 1
coef2 = 1
def performance_norm(performance_vector: dict) -> float:  # on peut bien évidemment prendre une norme plus complexe
    return - coef1 * sum(performance_vector["mirror_home_aggregator.energy_bought_outside"]) + sum(performance_vector["mirror_home_aggregator.energy_sold_outside"]) * coef2


ref_datalogger = create_simulation(comparison_simulation_length, ref_priorities_consumption, ref_priorities_production, f"comparison/reference", performance_metrics, exogen_instruction=other_strategies_results)
ref_results = {key: [] for key in performance_metrics}
for key in performance_metrics:
    ref_results[key] = ref_datalogger._values[key]
ref_performance = performance_norm(ref_results)

print(f"Performance of the reference strategy: {ref_performance}")
export_expert_data(path_to_export)
#
# # #####################################################################################################################
# # todo tweaking the action denormalization for action masking approach
# #######################################################################################################################
# import numpy as np
#
#
# def denormalize_my_actions(action, topology, internal_state, number_of_outside_actions=None, action_specific_index:int=None, action_reduction_flag=False) -> np.ndarray:
#     """
#     This function is used to denormalize the energy dispatch decision from the action inferred by the Actor's prediction of mean and std deviation.
#     The mean and std are used to generate a probability distribution from which action is sampled.
#     The sampled action is clipped within the normalized range of [0.0, 1.0].
#     The args represent the min/max bounds for de-normalization, it depends on the study case.
#     In case of action reduction, self.acted_action and self.action do not have the same shape !
#     """
#     # Initializing
#     used_action = np.copy(action)
#     return_list = []
#
#     # Special treatment during inference
#     if not number_of_outside_actions:
#         number_of_outside_actions = actions_related_to_energy_exchange(topology)
#
#     # Special treatment in case Action Reduction approach is used
#     if action_reduction_flag:
#         if not action_specific_index:  # we add a "shadow" action just to denormalize
#             raise Exception("If action reduction approach is to be used, you should specify during the de-normalization the index of the action which was reduced !")
#         used_action = np.insert(used_action, action_specific_index, 1)
#
#     # De-normalizing internal actions to aggregators
#     internal_actions = used_action[:- sum(number_of_outside_actions)]
#     number_of_internal_actions = int(len(internal_actions) / len(internal_state))
#     internal_actions = internal_actions.reshape(len(internal_state), number_of_internal_actions)
#     for aggregator in range(len(internal_actions)):
#         internal_actions[aggregator][0] = internal_state[aggregator][0] + (internal_state[aggregator][1] - internal_state[aggregator][0]) * internal_actions[aggregator][0]  # energy consumption
#         internal_actions[aggregator][1] = internal_state[aggregator][5] + (internal_state[aggregator][6] - internal_state[aggregator][5]) * internal_actions[aggregator][1]  # energy production
#         if number_of_internal_actions == 3:  # presence of energy storage systems
#             internal_actions[aggregator][2] = internal_state[aggregator][10] + (internal_state[aggregator][11] - internal_state[aggregator][10]) * internal_actions[aggregator][2]  # energy
#         elif number_of_internal_actions == 2:  # absence of energy storage systems
#             pass
#         else:
#             raise Exception("Attention, the number of natures of actions (consumption, production, storage) is not valid !")
#     # MLP or Dense layers need flat input
#     internal_actions = internal_actions.flatten()
#     internal_actions = internal_actions.tolist()
#     return_list.extend(internal_actions)
#
#     # De-normalizing external actions
#     external_actions = used_action[-sum(number_of_outside_actions):]
#     for exchange_index in range(len(number_of_outside_actions)):  # = length of the topology vector
#         if number_of_outside_actions[exchange_index] == 1:  # if the energy exchange involves just 2 aggregators and corresponds to just one flow
#             external_actions[exchange_index] = topology[exchange_index][2] + (topology[exchange_index][3] - topology[exchange_index][2]) * external_actions[exchange_index]
#         else:  # if it a co-generation, tri-generation ...
#             number_of_actions = number_of_outside_actions[exchange_index]
#             for i in range(number_of_actions):
#                 external_actions[exchange_index + i] = topology[exchange_index][number_of_actions + i + 1] + (topology[exchange_index][2 * number_of_actions + i + 1] - topology[exchange_index][number_of_actions + i + 1]) * external_actions[exchange_index + i]
#     # MLP or Dense layers need flat input
#     external_actions = external_actions.flatten()
#     external_actions = external_actions.tolist()
#     return_list.extend(external_actions)
#
#     # Special treatment in case Action Reduction approach is used
#     if action_reduction_flag:
#         return_list[action_specific_index] = 0.0
#         return_list[action_specific_index] = - (sum(return_list[:- sum(number_of_outside_actions)]) - sum(return_list[-sum(number_of_outside_actions):]))
#
#     # Finally we return the de-normalized actions
#     return_list = np.array([return_list])
#     return_list = return_list.flatten()
#
#     if not action_reduction_flag:
#         return_list.reshape(action.shape)
#     else:
#         return_list.reshape(action.shape[0] + 1)
#
#     return return_list
#
#
#
# def actions_related_to_energy_exchange(exchange_list: list) -> list:
#     """
#     This function is used to determine how many decisions to take per each energy exchange in the MEG.
#     """
#     aggregators_names = []
#     numerical_values = []
#     number_of_actions_per_exchange = []  # each value corresponds to an energy exchange in the topology vector
#     for exchange in exchange_list:  # each tuple in the topology
#         for element in exchange:
#             if isinstance(element, str):
#                 aggregators_names.append(element)  # aggregator names
#             else:
#                 numerical_values.append(element)  # Emin, Emax and efficiency
#         number_of_actions_per_exchange.append(int((len(numerical_values) - len(aggregators_names) + 1) / 2))
#
#     return number_of_actions_per_exchange
#
# a = np.arange(9)
# print(a)
# a = np.insert(a, 9, -100)
# print(a)
# print(a[5])
# a[5] = -9
# print(a)
# a = a.reshape(2,5)
# print(a)
# a = a.flatten()
# print(a)
# a = a.tolist()
# print(a)

# import numpy as np
#
# a = np.arange(3)
# a = np.insert(a, 2-1, 0)
# print(a)

# import numpy as np
# from scipy.stats import gamma
#
# # Define parameters
# shape = (1/0.25)**2
# scale = 0.25**2 * 1.570818982663
#
# # Calculate percentiles
# percentiles = [0.9, 0.99, 0.999, 0.9999, 0.99999, 0.999999]
# percentile_values = [gamma.ppf(p, shape, scale=scale) for p in percentiles]
#
# # Display results
# for p, value in zip(percentiles, percentile_values):
#     print(f"{p*100}% percentile: {value}")

# #####################################################################################################################
# todo defining new reward function with sigmoid for SDEWES
#######################################################################################################################
# import math
#
# x = 0.0
#
# lower = 0.0
# upper = 0.054411432
#
# steepness = 5.0
#
# scaled_x = (x - lower) / (upper - lower)
#
# # Sigmoid function, then clamped between 0 and 1
# result = max(0.0, min(1.0, 1 / (1 + math.exp(-steepness * (scaled_x - 0.5)))))
#
# print(result)
#
# def mySmoothPenalty(x: float, upper_bound: float, steepness: float):
#     """
#     This function is used to calculate the penalty related to energy conservation in a smooth way.
#     """
#     lower_bound = 0.0
#     scaled_x = (x - lower_bound) / (upper_bound - lower_bound)
#     return max(0.0, min(1.0, 1 / (1 + math.exp(-steepness * (scaled_x - 0.5)))))


# #####################################################################################################################
# todo generate electricity consumption profile for SDEWES case study
#######################################################################################################################
# import pandas as pd
#
# fileName = "D:\dossier_y23hallo\PycharmProjects\peacefulness\cases\Studies\SDEWES\AdditionalData/consumption_data.csv"
# df = pd.read_csv(fileName, sep=";", decimal=",")  # getting data
#
# start = pd.Timestamp("2018-01-01 00:00")  # or adjust if a different year
# df['datetime'] = pd.date_range(start=start, periods=8760, freq='H')
# df.set_index('datetime', inplace=True)
# df.rename(columns={df.columns[0]: 'Conso_min'}, inplace=True)
#
# # Group by day and take the mean over 24 hours
# daily_profile = df.resample('D').sum(numeric_only=True)
#
# # Optional: reset index if you want plain CSV
# daily_profile.reset_index(drop=True, inplace=True)
#
# # Save to CSV
# daily_profile.to_csv("daily_profile.csv", sep=",", decimal=".", header=True, index=False)
