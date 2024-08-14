# TODO get_subclasses et subclasses_dictionary
# from importlib import import_module  # this library allows to import modules defined as str
# import inspect
#
# from src.tools.Utilities import list_files_and_folders
#
#
# class SubclassesInstantiationException(Exception):
#     def __init__(self, message):
#         super().__init__(message)
#
#
#
# subclasses_dictionary = {}  # a dictionary containing all the subclasses
#
# classes_concerned = list_files_and_folders("lib/Subclasses/")  # the list of all classes concerned by subclasses
#
# for class_name in classes_concerned:
#     subclasses_dictionary[class_name] = {}  # a sub-dictionary containing all the subclasses of the concerned class
#     class_directory = "lib/Subclasses/" + class_name  # the directory containing subclasses of one class
#     subclasses_list = list_files_and_folders(class_directory)  # list of all subclasses for a given class
#
#     for subclass_folder in subclasses_list:  # for each subclass
#         subclass_file = "lib.Subclasses." + class_name + "." + subclass_folder + "." + subclass_folder  # the file where the module is defined
#         if subclass_folder + ".py" in list_files_and_folders("lib/Subclasses/" + class_name + "/" + subclass_folder):
#             # subclass_module = import_module(subclass_file)  # we import the .py file
#             try:
#                 subclass_module = import_module(subclass_file)  # we import the .py file
#             except:
#                 raise SubclassesInstantiationException(f"An error occured during the instantiation of the module {subclass_file}.\n"
#                                                            "Please check that there is a module there and that it bears the same name as the directory. If it is not the case, please add one or remove the directory from the lib/subclasses directory.")
#             for subclass_name, subclass_class in inspect.getmembers(subclass_module):
#                 # print(subclass_name)
#                 # print(subclass_class)
#                 if inspect.isclass(subclass_class) and subclass_name != class_name:  # get back only the subclasses
#                     subclasses_dictionary[class_name][subclass_name] = subclass_class  # the subclass is added to the subclass list


# TODO getting the current world instance
# class MyClass:
#     def __init__(self, name):
#         self.name = name
#
#     def set_ref_world(self):
#         self.__class__.ref_world = self
#
# # Create instances of MyClass
# instance1 = MyClass("Instance 1")
# instance2 = MyClass("Instance 2")
#
# # Call set_ref_world on instance1
# instance1.set_ref_world()
#
# # Now the class attribute ref_world refers to instance1
# print(MyClass.ref_world.name)  # Output: Instance 1
# print(instance2.ref_world.name)
# # Call set_ref_world on instance2
# instance2.set_ref_world()
#
# # Now the class attribute ref_world refers to instance2
# print(MyClass.ref_world.name)

# TODO testing the message manager class
# import copy
#
#
# class MessagesManager:
#     """
#     This class manages the messages exchanged between devices and aggregators through contracts.
#     """
#
#     # the minimum information needed everywhere
#     information_message = {"type": "", "aggregator": "", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": 0}
#     decision_message = {"aggregator": "", "quantity": 0, "price": 0}
#     # the information added to all messages
#     added_information = {}
#
#     def __init__(self):
#         self._specific_information_message = {}
#         self._specific_decision_message = {}
#
#     # ##########################################################################################
#     # Initialization
#     # ##########################################################################################
#
#     def complete_information_message(self, additional_element: str, default_value):
#         """
#         When complementary information is added in the messages exchanged between devices and aggregators,
#         this method updates the self._message attribute.
#
#         Parameters
#         ----------
#         additional_element: any parsable type of object
#         """
#         self._specific_information_message = {**self._specific_information_message, **{additional_element: default_value}}
#
#     def complete_decision_message(self, additional_element: str, default_value):
#         """
#         When complementary information is added in the messages exchanged between devices and aggregators,
#         this method updates the self._message attribute.
#
#         Parameters
#         ----------
#         additional_element: any parsable type of object
#         """
#         self._specific_decision_message = {**self._specific_decision_message, **{additional_element: default_value}}
#
#     def set_type(self, device_type: str):
#         self._specific_information_message["type"] = device_type
#
#     @classmethod
#     def complete_all_messages(cls, additional_element: str, default_value):
#         cls.information_message = {**cls.information_message, **{additional_element: default_value}}
#         cls.decision_message = {**cls.decision_message, **{additional_element: default_value}}
#         cls.added_information[additional_element] = default_value
#
#     # ##########################################################################################
#     # Dynamic behavior
#     # ##########################################################################################
#
#     def create_information_message(self):
#         general_message = copy.deepcopy(self.__class__.information_message)
#         specific_message = copy.deepcopy(self._specific_information_message)
#         information_message = {**general_message, **specific_message}
#
#         return information_message
#
#     def create_decision_message(self):
#         general_message = copy.deepcopy(self.__class__.decision_message)
#         specific_message = copy.deepcopy(self._specific_decision_message)
#         decision_message = {**general_message, **specific_message}
#
#         return decision_message


# TODO here we test how to send the information message to my code
# import sys
#
#
# formalism_message = {"t": "toto"}
# prediction_message = {"s": "sousou"}
# prices = {"b": "bousou"}
#
# # Sending the information message to the method
# path_to_interface = "C:/Users/y23hallo/PycharmProjects/Management_Strategy/Peacefulness_cases/Utilities/strategy_interface.py"
# pass_state = open(path_to_interface).read()
# sys.argv = ["pass_state", formalism_message, prediction_message, prices]
# exec(pass_state)

# TODO here we test functions from DRL_Strategy_Utilities - from_tensor_to_dict
# import numpy as np
# import pandas as pd
# from collections import Counter
#
#
# # def from_tensor_to_dict(actions: np.ndarray, aggregators: list, agent: "Agent") -> dict:
# #     """
# #     This method is used to translate the actions taken by the A-C method into results understood by Peacefulness.
# #     The decision is to be stored.
# #     The return dict is under the format: {'Aggregator_1': {'Energy_Consumption': , 'Energy_Production': ...}, ...}
# #     """
# #     list_of_columns = []
# #     number_of_aggregators, number_of_actions = actions.shape
# #
# #     if number_of_aggregators != len(aggregators):
# #         raise Exception("The number of actions taken by the RL does not correspond to the number of aggregators in the MEG")
# #
# #     # Getting relevant info from the peacefulness_grid class considered for the RL agent
# #     agent_grid_topology = agent.grid.get_topology  # the return of the get_topology method
# #     agent_standard_devices = agent.grid.get_standard  # the return of the get_standard method
# #     agent_storage_devices = agent.grid.get_storage  # the return of the get_storage method
# #
# #     # Finding the columns related to energy exchanges
# #     exchange_options = Counter(item for tup in agent_grid_topology for item in tup[:2])
# #     exchange_list = []
# #     for index in range(exchange_options.most_common(1)[0][1]):
# #         name = "Energy_Exchange_{}".format(index + 1)
# #         exchange_list.append(name)
# #
# #     # Finding the other columns
# #     condition = number_of_actions - exchange_options.most_common(1)[0][1]
# #     if condition == 3:  # presence of energy consumers, production and storage
# #         list_of_columns.extend(["Energy_Consumption", "Energy_Production", "Energy_Storage"])
# #     elif condition == 2:  # presence of either energy consumers/production, consumers/storage or production/storage
# #         if max(agent_storage_devices.values()) == 0:  # presence of only energy consumers & production
# #             list_of_columns.extend(["Energy_Consumption", "Energy_Production"])
# #         else:
# #             if actions[0][0] < 0:  # presence of only energy production & storage
# #                 list_of_columns.extend(["Energy_Production", "Energy_Storage"])
# #             else:  # presence of only energy consumers & storage
# #                 list_of_columns.extend(["Energy_Consumption", "Energy_Storage"])
# #     elif condition == 1:  # presence of either energy consumers or energy production or energy storage
# #         if max(agent_storage_devices.values()) != 0:  # presence of only energy storage
# #             list_of_columns.extend(["Energy_Storage"])
# #         else:
# #             if actions[0][0] < 0:  # presence of only energy production
# #                 list_of_columns.extend(["Energy_Production"])
# #             else:  # presence of only energy consumers
# #                 list_of_columns.extend(["Energy_Consumption"])
# #     elif condition == 0:  # we only manage the energy exchanges between aggregators
# #         print("Attention, the MEG in question consists of only energy exchangers aggregators !")
# #
# #     list_of_columns.extend(exchange_list)
# #
# #     # First we get a dataframe from the actions tensor or vector
# #     actions_to_dataframe = pd.DataFrame(
# #                                         data=actions,
# #                                         index=aggregators,
# #                                         columns=list_of_columns
# #                                         )
# #     # We then get a dict from the dataframe
# #     actions_dict = actions_to_dataframe.to_dict()
# #
# #     # Inverting the dict - to get the aggregators.names as keys.
# #     resulting_dict = {
# #         key: {k: v[key] for k, v in actions_dict.items()}
# #         for key in actions_dict[next(iter(actions_dict))].keys()
# #     }
# #
# #     return resulting_dict
#
# #
# dummy_actions = np.array([[500, -100, 0, 150, 250], [0, -300, 100, -150, 0], [600, -700, -150, 0, -250]])
# aggregator_list = ["A1", "A2", "A3"]
# #
# # # print(exchange_options)
# # # print(exchange_options.most_common(1)[0][1])
# # # print(from_tensor_to_dict(dummy_actions, aggregator_list))
# # # print(dummy_actions[0][0])
# list_of_columns = []
# number_of_aggregators, number_of_actions = dummy_actions.shape
# #
# # if number_of_aggregators != len(aggregator_list):
# #     raise Exception("The number of actions taken by the RL does not correspond to the number of aggregators in the MEG")
# #
# # Getting relevant info from the peacefulness_grid class considered for the agent
# agent_grid_topology = []  # the return of the get_topology method
# agent_standard_devices = {"A1": 10, "A2": 5, "A3": 10}  # the return of the get_standard method
# agent_storage_devices = {"A1": 0, "A2": 6, "A3": 6}  # the return of the get_storage method
# #
# # Finding the columns related to energy exchanges
# if len(agent_grid_topology) != 0:
#     exchange_options = Counter(item for tup in agent_grid_topology for item in tup[:2])
#     exchange_list = []
#     for index in range(exchange_options.most_common(1)[0][1]):
#         name = "Energy_Exchange_{}".format(index + 1)
#         exchange_list.append(name)
#     number_of_exchanges = exchange_options.most_common(1)[0][1]
# else:
#     number_of_exchanges = 0
# #
# # Finding the other columns
# condition = number_of_actions - number_of_exchanges
# if condition == 3:  # presence of energy consumers, production and storage
#     list_of_columns.extend(["Energy_Consumption", "Energy_Production", "Energy_Storage"])
# elif condition == 2:  # presence of either energy consumers/production, consumers/storage or production/storage
#     if max(agent_storage_devices.values()) == 0:  # presence of only energy consumers & production
#         list_of_columns.extend(["Energy_Consumption", "Energy_Production"])
#     else:
#         if dummy_actions[0][0] < 0:  # presence of only energy production & storage
#             list_of_columns.extend(["Energy_Production", "Energy_Storage"])
#         else:  # presence of only energy consumers & storage
#             list_of_columns.extend(["Energy_Consumption", "Energy_Storage"])
# elif condition == 1:  # presence of either energy consumers or energy production or energy storage
#     if max(agent_storage_devices.values()) != 0:  # presence of only energy storage
#         list_of_columns.extend(["Energy_Storage"])
#     else:
#         if dummy_actions[0][0] < 0:  # presence of only energy production
#             list_of_columns.extend(["Energy_Production"])
#         else:  # presence of only energy consumers
#             list_of_columns.extend(["Energy_Consumption"])
# #
# list_of_columns.extend(exchange_list)
# # # print(list_of_columns)
# #
# # Transforming the tensor to a dataframe
# actions_to_dataframe = pd.DataFrame(
#                                         data=dummy_actions,
#                                         index=aggregator_list,
#                                         columns=list_of_columns
#                                         )
# # # # print(actions_to_dataframe)
# # #
# # Getting a dict from the dataframe
# actions_dict = actions_to_dataframe.to_dict()
# # print(actions_dict)
# #
# # Inverting the dict
# resulting_dict = {
#     key: {k: v[key] for k, v in actions_dict.items()}
#     for key in actions_dict[next(iter(actions_dict))].keys()
# }
# print(resulting_dict)
# # resulting_dict = {}
# # inter_dict = {}
# # for key in actions_dict.keys():
#     for subkey in actions_dict[key]:
#         resulting_dict[subkey] = {}
#         inter_dict[key] = actions_dict[key][subkey]
#         resulting_dict[subkey] = {**inter_dict}
#         # print(actions_dict[key][subkey])
#         if subkey in resulting_dict:
#             resulting_dict[subkey][key] = actions_dict[key][subkey]
#         resulting_dict[subkey] = {key: actions_dict[key][subkey]}
# print(resulting_dict)
# print(actions_dict.items())
# print(resulting_dict)

# TODO here we test functions from DRL_Strategy_Utilities - extract_decision
# def extract_decision(decision_message: dict, aggregator: "Aggregator") -> list:
#     """
#     From the decisions taken by the RL agent concerning the whole multi-energy grid, we extract the decision related to the current aggregator.
#     """
#     consumption = {}
#     production = {}
#     storage = {}
#     exchange = {}
#
#     for element in decision_message.keys():  # TODO prices ?
#         if element == aggregator.name:
#             dummy_dict = decision_message[element]
#             if "Energy_Consumption" in dummy_dict:
#                 consumption = decision_message[element]["Energy_Consumption"]
#                 dummy_dict.pop("Energy_Consumption")
#             if "Energy_Production" in dummy_dict:
#                 production = decision_message[element]["Energy_Production"]
#                 dummy_dict.pop("Energy_Production")
#             if "Energy_Storage" in dummy_dict:
#                 storage = decision_message[element]["Energy_Storage"]
#                 dummy_dict.pop("Energy_Storage")
#             exchange = dummy_dict
#
#     return [consumption, production, storage, exchange]
#
#
# class Aggregator():
#     def __init__(self, name: str):
#         self.name = name
#
# aggregateur_1 = Aggregator("A1")
# aggregateur_2 = Aggregator("A2")
# aggregateur_3 = Aggregator("A3")
#
# print(extract_decision(resulting_dict, aggregateur_1))
# print(extract_decision(resulting_dict, aggregateur_2))
# print(extract_decision(resulting_dict, aggregateur_3))

# TODO here we are testing the bottom-up phase of the strategy
# TODO - Proposition 1 - on publie tout le besoin en énergie des agrégateurs a.k.a AlwaysSatisfied
# # The information to be communicated to the DRL method in order to define the state of the grid
# prediction = self.call_to_forecast(aggregator)
# [min_price, max_price] = self._limit_prices(aggregator)
# formalism = [{}]
# # Getting the formalism message from the devices
# for device in aggregator.devices:
#     formalism.append(device._create_message())
#
# self.interface[0](min_price, max_price, prediction, formalism)  # communicating the formalism message, forecasting message and prices to the method
#
# from src.common.Messages import *
#
#
# class dummy_class():
#     messages_manager = MessagesManager()
#     messages_manager.complete_information_message("flexibility",[])  # -, indicates the level of flexibility on the latent concumption or production
#     messages_manager.complete_information_message("interruptibility", 0)  # -, indicates if the device is interruptible
#     messages_manager.complete_information_message("coming_volume",0)  # kWh, gives an indication on the latent consumption or production
#     messages_manager.set_type("standard")
#     information_message = messages_manager.create_information_message
#     decision_message = messages_manager.create_decision_message
#     information_keys = messages_manager.information_keys
#     decision_keys = messages_manager.decision_keys
#
#     def get_information(self):
#         return self.messages_manager.decision_message
#
#     def get_volume(self):
#         return self.messages_manager._specific_information_message

#
# test = dummy_class()
# print(test.decision_keys)
# print(test.get_information())
#
# general_message = copy.deepcopy(test.messages_manager.__class__.information_message)
# print(general_message)
# specific_message = copy.deepcopy(test.messages_manager._specific_information_message)
# print(specific_message)
# information_message = {**general_message, **specific_message}
# print(information_message)
# from src.tools.DRL_Strategy_utilities import *
#
#
# dummy_dict = {"A1": {"Energy_Consumption": {"D1": {"energy_minimum": 20, "energy_maximum": 150, "flexibility": [0], "interruptibility": 0, "coming_volume": 500},
#                                             "D2": {"energy_minimum": 20, "energy_maximum": 150, "flexibility": [], "interruptibility": 0, "coming_volume": 500},
#                                             "D3": {"energy_minimum": 20, "energy_maximum": 150, "flexibility": [], "interruptibility": 0, "coming_volume": 500}},
#                      "Energy_Production": {"D4": {"energy_minimum": -20, "energy_maximum": -150, "flexibility": [], "interruptibility": 0, "coming_volume": 0},
#                                            "D5": {"energy_minimum": -20, "energy_maximum": -150, "flexibility": [1], "interruptibility": 0, "coming_volume": -500},
#                                            "D6": {"energy_minimum": -20, "energy_maximum": -150, "flexibility": [], "interruptibility": 0, "coming_volume": -500}},
#                      "Energy_Storage": {"D7": {"energy_minimum": 20, "energy_maximum": 150, "state_of_charge": 0.45, "capacity": 20, "self_discharge_rate": 0.3, "efficiency": 0.95},
#                                         "D8": {"energy_minimum": -20, "energy_maximum": -150, "state_of_charge": 0.45, "capacity": 20, "self_discharge_rate": 0.3, "efficiency": 0.95},
#                                         "D9": {"energy_minimum": 20, "energy_maximum": 150, "state_of_charge": 0.45, "capacity": 20, "self_discharge_rate": 0.3, "efficiency": 0.95}},
#                      "Energy_Conversion": {"D10": {"energy_minimum": 20, "energy_maximum": 150, "efficiency": 0.65},
#                                            "D11": {"energy_minimum": -20, "energy_maximum": -150, "efficiency": 0.5},
#                                            "D12": {"energy_minimum": 20, "energy_maximum": 150, "efficiency": 0.8}}
#                      }
#               }
#
# dummy_dict = mutualize_formalism_message(dummy_dict)
# print(dummy_dict)

# # Preparing the dict
# return_dict = {}
# inter_dict = {}
# consumption_dict = {}
# production_dict = {}
# storage_dict = {}
# conversion_dict = {}
# for aggregator_name in dummy_dict.keys():
#     inter_dict = {**dummy_dict[aggregator_name]}
#     for key in inter_dict.keys():
#         consumption_dict = {**consumption_dict, **inter_dict["Energy_Consumption"]}
#         production_dict = {**production_dict, **inter_dict["Energy_Production"]}
#         storage_dict = {**storage_dict, **inter_dict["Energy_Storage"]}
#         conversion_dict = {**conversion_dict, **inter_dict["Energy_Conversion"]}

# # Energy consumption and production associated dict of values
# energy_min = []
# energy_max = []
# flexibility = []
# interruptibility = []
# coming_volume = []
#
# for element in [consumption_dict, production_dict]:
#     for key in element:
#         for subkey in element[key]:
#             if subkey == 'energy_minimum':
#                 energy_min.append(element[key][subkey])
#             elif subkey == 'energy_maximum':
#                 energy_max.append(element[key][subkey])
#             elif subkey == 'flexibility':
#                 flexibility.extend(element[key][subkey])
#             elif subkey == 'interruptibility':
#                 interruptibility.append(element[key][subkey])
#             else:
#                 coming_volume.append(element[key][subkey])
#     if element == consumption_dict:
#         return_dict = {
#             "Energy_Consumption": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
#                                    'flexibility': min(flexibility), 'interruptibility': min(interruptibility),
#                                    'coming_volume': sum(coming_volume)}}
#         energy_min.clear()
#         energy_max.clear()
#         flexibility.clear()
#         interruptibility.clear()
#         coming_volume.clear()
#     else:
#         return_dict = {**return_dict, **{
#             "Energy_Production": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
#                                   'flexibility': min(flexibility), 'interruptibility': min(interruptibility),
#                                   'coming_volume': sum(coming_volume)}}
#                                            }
# # Energy storage associated dict of values
# energy_min = []
# energy_max = []
# state_of_charge = []
# capacity = []
# self_discharge_rate = []
# efficiency = []
#
# for key in storage_dict:
#     for subkey in storage_dict[key]:
#         if subkey == 'energy_minimum':
#             energy_min.append(storage_dict[key][subkey])
#         elif subkey == 'energy_maximum':
#             energy_max.append(storage_dict[key][subkey])
#         elif subkey == 'state_of_charge':
#             state_of_charge.append(storage_dict[key][subkey])
#         elif subkey == 'capacity':
#             capacity.append(storage_dict[key][subkey])
#         elif subkey == 'self_discharge_rate':
#             self_discharge_rate.append(storage_dict[key][subkey])
#         else:
#             efficiency.append(storage_dict[key][subkey])
#
# return_dict = {**return_dict, **{
#             "Energy_Storage": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max),
#                                'state_of_charge': sum(state_of_charge)/len(state_of_charge), 'capacity': sum(capacity)/len(capacity),
#                                'self_discharge_rate': sum(self_discharge_rate)/len(self_discharge_rate), 'efficiency': sum(efficiency)/len(efficiency)}}
#                                            }
# # Energy conversion associated dict of values
# energy_min = []
# energy_max = []
# efficiency = []
#
# for key in conversion_dict:
#     for subkey in conversion_dict[key]:
#         if subkey == 'energy_minimum':
#             energy_min.append(conversion_dict[key][subkey])
#         elif subkey == 'energy_maximum':
#             energy_max.append(conversion_dict[key][subkey])
#         else:
#             efficiency.append(conversion_dict[key][subkey])
#
# return_dict = {**return_dict, **{
#             "Energy_Conversion": {'energy_minimum': sum(energy_min), 'energy_maximum': sum(energy_max), 'efficiency': sum(efficiency)/len(efficiency)}}}
#
# print(return_dict)

# TODO here we test some functionalities in the top-down-phase of the DRL strategy
# import numpy as np
# # my_aggregator = "A1"
# # my_list = []
# # dumb_grid_topology = [("A1", "A2", 0.45), ("A1", "A4", 1), ("A3", "A2", 1), ("A4", "A2", 0.85)]
# # for element in dumb_grid_topology:
# #     if my_aggregator in element:
# #         print(element[2])
# #         my_list.append(dumb_grid_topology.index(element))
# # print(my_list)
# a = 5
# b = 5
# if np.sign(a) == np.sign(b):
#     print(True)
# else:
#     print(False)
#
# a = abs(-9)
# print(a)
# class aggregator:
#     def __init__(self, name: str):
#         self.name = name
#
# my_aggregator = aggregator('Aggregator_1')
#
#
# decision_message = {'Aggregator_1': {'Energy_Consumption': 400, 'Energy_Production': -320, 'Energy_Storage': 0,
# 'Energy_Exchange_1': 120, 'Energy_Exchange_2': -60, 'Energy_Exchange_3': 20},
# 'Aggregator_2': {'Energy_Consumption': 0, 'Energy_Production': 0, 'Energy_Storage': 110, 'Energy_Exchange_1': -120,
# 'Energy_Exchange_2': 0, 'Energy_Exchange_3': 10}, 'Aggregator_3': {'Energy_Consumption': 350,
# 'Energy_Production': -630, 'Energy_Storage': 250, 'Energy_Exchange_1': 0, 'Energy_Exchange_2': 60,
# 'Energy_Exchange_3': -30}}
#
# if my_aggregator.name in decision_message:
#     dummy_dict = decision_message[my_aggregator.name]
#     if "Energy_Consumption" in dummy_dict:
#         consumption = decision_message[my_aggregator.name]["Energy_Consumption"]
#         dummy_dict.pop("Energy_Consumption")
#     if "Energy_Production" in dummy_dict:
#         production = decision_message[my_aggregator.name]["Energy_Production"]
#         dummy_dict.pop("Energy_Production")
#     if "Energy_Storage" in dummy_dict:
#         storage = decision_message[my_aggregator.name]["Energy_Storage"]
#         dummy_dict.pop("Energy_Storage")
#     exchange = dummy_dict
# print(consumption)
# print(production)
# print(storage)
# print(exchange)

# TODO here we test top-down phase functionalities
# def distribute_to_standard_devices(device_list: list, energy_accorded: float, energy_price: float, world: "World", aggregator: "Aggregator", message: dict) -> float:
#     """
#     This function is used for energy distribution and billing for standard devices managed by the aggregator.
#     It concerns the energy producers and consumers.
#     The minimum energy demands/offers are served first, the rest is then distributed equally over non-urgent devices.
#     """
#     distribution_decision = {}
#     energy_difference = energy_accorded
#     urgent_devices = []
#     non_urgent_devices = []
#     for device in device_list:
#         Emin = world.catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
#         Emax = world.catalog.get(f"{device.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
#
#         # the minimum energy demand/offer is served first
#         if abs(energy_accorded) > abs(Emin):  # to take into account both negative and positive signs
#             distribution_decision[device.name] = Emin
#             energy_accorded -= Emin
#         elif 0 < abs(energy_accorded) < abs(Emin):  # to take into account both negative and positive signs
#             distribution_decision[device.name] = energy_accorded
#             energy_accorded = 0
#
#         # the urgency of the demand/offer is determined
#         if Emin == Emax:  # the energy demand/offer is urgent
#             urgent_devices.append(device)
#         else:  # the energy demand/offer is not a priority
#             non_urgent_devices.append(device)
#
#     for device in urgent_devices:  # the urgent energy demands/offers are served
#         message['quantity'] = distribution_decision[device.name]
#         message["price"] = energy_price
#         world.catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
#
#     for device in non_urgent_devices:  # the remaining energy is equally distributed over the rest of the devices
#         message['quantity'] = distribution_decision[device.name] + energy_accorded / len(non_urgent_devices)
#         message["price"] = energy_price
#         world.catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
#
#     maximum_energy_difference = energy_difference - energy_accorded
#
#     return maximum_energy_difference
# from src.tools.DRL_Strategy_utilities import return_sign


# def distribute_to_storage_devices(storage_list: list, energy_accorded_to_storage: float, buying_price: float, selling_price: float, world: "World", aggregator: "Aggregator", message: dict):
#     """
#     This function is used for energy distribution and billing for energy storage systems managed by the aggregator.
#     The devices who have needs that encounter the average needs are to stay idle.
#     The minimum energy demands/offers are served first, the rest is then distributed equally over non-urgent devices.
#     """
#     distribution_decision = {}
#     non_urgent_storage = []
#     for storage in storage_list:
#         Emax = world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_maximum"]
#         Emin = world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
#         sign_min = return_sign(Emin, energy_accorded_to_storage)
#         if not sign_min:  # the device wants the opposite of the average want of the energy storage systems managed by the aggregator, thus it will be idle
#             message["quantity"] = 0
#             message["price"] = 0
#             world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
#         else:  # the device wants the same as the average want of the energy storage systems managed by the aggregator
#             if abs(energy_accorded_to_storage) > abs(Emin):  # to take into account both negative and positive signs
#                 distribution_decision[storage.name] = Emin
#                 energy_accorded_to_storage -= Emin
#             elif 0 < abs(energy_accorded_to_storage) < abs(Emin):  # to take into account both negative and positive signs
#                 distribution_decision[storage.name] = energy_accorded_to_storage
#                 energy_accorded_to_storage = 0
#             # the urgency is determined
#             if Emin == Emax:  # the energy storage system has urgency
#                 message["quantity"] = distribution_decision[storage.name]
#                 if Emin < 0:  # the energy storage system wants to sell its energy
#                     message["price"] = selling_price
#                 else:  # the energy storage system wants to buy energy
#                     message["price"] = buying_price
#                 world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
#             else:
#                 sign_max = return_sign(Emax, energy_accorded_to_storage)
#                 if not sign_max:
#                     message["quantity"] = distribution_decision[storage.name]
#                     if Emin < 0:  # the energy storage system wants to sell its energy
#                         message["price"] = selling_price
#                     else:  # the energy storage system wants to buy energy
#                         message["price"] = buying_price
#                     world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
#                 else:
#                     non_urgent_storage.append(storage)
#
#     for storage in non_urgent_storage:  # the remaining energy is equally distributed over the rest of the devices
#         Emin = world.catalog.get(f"{storage.name}.{aggregator.nature.name}.energy_wanted")["energy_minimum"]
#         message["quantity"] = distribution_decision[storage.name] + energy_accorded_to_storage / len(non_urgent_storage)
#         if Emin < 0:  # the energy storage system wants to sell its energy
#             message["price"] = selling_price
#         else:  # the energy storage system wants to buy energy
#             message["price"] = buying_price
#         world.catalog.set(f"{storage.name}.{aggregator.nature.name}.energy_accorded", message)
# aggregator_name = "A1"
#
# dummy_grid_topology = [('A1', 'A2', -35, 25, 1), ('A1', 'A3', 25, 45, 0.85), ('A2', 'A3', 'A4', -12, 87, 0.6, 0.45), ('A3', 'A1', 'A2', 'A4', -59, 64, 0.5, 0.45, 0.65)]
# energy_accorded_to_exchanges = {"Energy_Exchange_1": 0, "Energy_Exchange_2": 30, "Energy_Exchange_3": 12}  # for A4
# converters_list = {'device_1': {"energy_minimum": -12, "energy_nominal": 25, "energy_maximum": 87}, 'device_2': {"energy_minimum": -59, "energy_nominal": 7, "energy_maximum": 64}}  # for A1, and it is the device objects not only their names

# def distribute_energy_exchanges(world: "World", catalog: "Catalog", aggregator: "Aggregator", energy_accorded_to_exchange: dict, grid_topology: list, converter_list: dict, buying_price: float, selling_price: float, message: dict):
#     """
#     This function computes the energy exchanges (direct ones and with conversion systems).
#     Since we don't know how are which decision corresponds to which energy exchange, we first verify if the decision is bound by the min and max.
#     Then we look for the one closest to the nominal.
#     May be subject to change if finally we output the matrix of the grid's topology as in the input to the model.
#     """
#     aggregator_energy_exchanges_from_grid_topology = []
#     for tup in grid_topology:
#         if aggregator.name in tup:
#             aggregator_energy_exchanges_from_grid_topology.append(tup)
#
#     aggregator_energy_exchanges_from_RL_decision = []
#     dummy_dict = {**energy_accorded_to_exchange}
#     for key, value in energy_accorded_to_exchange.items():
#         if value != 0:
#             aggregator_energy_exchanges_from_RL_decision.append(value)
#             dummy_dict.pop(key)
#     if len(dummy_dict) == len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision):
#         for key, value in dummy_dict.items():
#             aggregator_energy_exchanges_from_RL_decision.append(value)
#     else:
#         for i in range(len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision)):
#             aggregator_energy_exchanges_from_RL_decision.append(0)
#
#     if len(aggregator_energy_exchanges_from_grid_topology) != len(aggregator_energy_exchanges_from_RL_decision):
#         raise Exception(
#             f"The {aggregator.name}'s occurrences in energy exchanges don't match the corresponding number of decisions taken by the RL !")
#
#     # Quantities concerning energy conversion systems
#     decision_message = {}
#     print("The aggregator does not exchange with its subaggregators nor with its superior aggregator !")
#     for device in converter_list:
#         decision_message[device] = []
#         for element in aggregator_energy_exchanges_from_RL_decision[:]:
#             if converter_list[device]["energy_minimum"] < element < converter_list[device]["energy_maximum"]:
#                 decision_message[device].append(element)
#         if len(decision_message[device]) > 1:
#             distance = {}
#             for element in decision_message[device]:
#                 distance[element] = abs(element - converter_list[device]["energy_nominal"])
#             decision_message[device] = min(distance, key=distance.get)
#             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#         else:
#             decision_message[device] = decision_message[device][0]
#             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#
#         message["quantity"] = decision_message[device]
#         if decision_message[device] < 0:  # energy selling
#             message["price"] = selling_price
#         else:  # energy buying
#             message["price"] = buying_price
#         world.catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
#
#     # Quantities concerning sub-aggregators
#     if aggregator_energy_exchanges_from_RL_decision:
#         for subaggregator in aggregator.subaggregators:
#             decision_message[subaggregator.name] = []
#             quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
#             for element in aggregator_energy_exchanges_from_RL_decision[:]:
#                 if quantities_and_prices["energy_minimum"] < element < quantities_and_prices["energy_maximum"]:
#                     decision_message[subaggregator.name].append(element)
#                 if len(decision_message[subaggregator.name]) > 1:
#                     distance = {}
#                     for element in decision_message[subaggregator.name]:
#                         distance[element] = abs(element - quantities_and_prices["energy_nominal"])
#                     decision_message[subaggregator.name] = min(distance, key=distance.get)
#                     aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
#                 else:
#                     decision_message[subaggregator.name] = decision_message[subaggregator.name][0]
#                     aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
#
#             message["quantity"] = decision_message[subaggregator.name]
#             if decision_message[subaggregator.name] < 0:  # energy selling
#                 message["price"] = selling_price
#             else:  # energy buying
#                 message["price"] = buying_price
#             catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)

# message = {"aggregator": "", "quantity": 0, "price": 0}
#
# buying_price = 0.45
# selling_price = 0.35
#
# grid_topology = [('A1', 'A2', -500, 500, 1), ('A3', 'A4', -350, 350, 1), ('A2', 'A3', -110, 75, 0.8),
#                  ('A1', 'A3', 'A4', -65, 50, 0.45, 0.55), ('A1', 'A4', 'A5', 'A6', -25, 35, 0.6, 0.5, 0.7)]
#
# energy_accorded_to_exchange = {"Energy_Exchange_1": -100, "Energy_Exchange_2": 15, "Energy_Exchange_3": 25}  # pour A1
#
# converter_list = {"device_1": {"energy_minimum": -65, "energy_nominal": 12, "energy_maximum": 50},
#                   "device_2": {"energy_minimum": -25, "energy_nominal": 20, "energy_maximum": 35}}  # pour A1
#
# aggregator_name = 'A1'
# aggregator_subaggregators = ['A2']
#
# # initializing
# energy_bought_inside = 0.0
# money_spent_inside = 0.0
# energy_sold_inside = 0.0
# money_earned_inside = 0.0
# energy_bought_outside = 0.0
# money_spent_outside = 0.0
# energy_sold_outside = 0.0
# money_earned_outside = 0.0
#
# aggregator_energy_exchanges_from_grid_topology = []
# for tup in grid_topology:
#     if aggregator_name in tup:
#         aggregator_energy_exchanges_from_grid_topology.append(tup)
#
# aggregator_energy_exchanges_from_RL_decision = []
# dummy_dict = {**energy_accorded_to_exchange}
# for key, value in energy_accorded_to_exchange.items():
#     if value != 0:
#         aggregator_energy_exchanges_from_RL_decision.append(value)
#         dummy_dict.pop(key)
# if len(dummy_dict) == len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision):
#     for key, value in dummy_dict.items():
#         aggregator_energy_exchanges_from_RL_decision.append(value)
# else:
#     for i in range(len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision)):
#         aggregator_energy_exchanges_from_RL_decision.append(0)
#
# if len(aggregator_energy_exchanges_from_grid_topology) != len(aggregator_energy_exchanges_from_RL_decision):
#     raise Exception(
#         f"The {aggregator_name}'s occurrences in energy exchanges don't match the corresponding number of decisions taken by the RL !")
#
# # Quantities concerning energy conversion systems
# decision_message = {}
# print("The aggregator does not exchange with its subaggregators nor with its superior aggregator !")
# for device in converter_list:
#     decision_message[device] = []
#     for element in aggregator_energy_exchanges_from_RL_decision[:]:
#         if converter_list[device]["energy_minimum"] < element < converter_list[device]["energy_maximum"]:
#             decision_message[device].append(element)
#     if len(decision_message[device]) > 1:
#         distance = {}
#         for element in decision_message[device]:
#             distance[element] = abs(element - converter_list[device]["energy_nominal"])
#         decision_message[device] = min(distance, key=distance.get)
#         aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#     else:
#         decision_message[device] = decision_message[device][0]
#         aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#
#     message["quantity"] = decision_message[device]
#     if decision_message[device] < 0:  # energy selling
#         message["price"] = selling_price
#         energy_sold_outside += abs(message["quantity"])
#         money_earned_outside += abs(message['quantity'] * message["price"])
#     else:  # energy buying
#         message["price"] = buying_price
#         energy_bought_outside += abs(message["quantity"])
#         money_spent_outside += abs(message['quantity'] * message["price"])
#     # world.catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
#     print(message)
# # Quantities concerning sub-aggregators
# quantities_and_prices = {"energy_minimum": -500, "energy_nominal": -150, "energy_maximum": 500}
# if aggregator_energy_exchanges_from_RL_decision:
#     for subaggregator in aggregator_subaggregators:
#         decision_message[subaggregator] = []
#         # quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
#         for element in aggregator_energy_exchanges_from_RL_decision[:]:
#             if quantities_and_prices["energy_minimum"] < element < quantities_and_prices["energy_maximum"]:
#                 decision_message[subaggregator].append(element)
#             if len(decision_message[subaggregator]) > 1:
#                 distance = {}
#                 for element in decision_message[subaggregator]:
#                     distance[element] = abs(element - quantities_and_prices["energy_nominal"])
#                 decision_message[subaggregator] = min(distance, key=distance.get)
#                 aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator])
#             else:
#                 decision_message[subaggregator] = decision_message[subaggregator][0]
#                 aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator])
#
#         message["quantity"] = decision_message[subaggregator]
#         if decision_message[subaggregator] < 0:  # energy selling
#             message["price"] = selling_price
#             energy_bought_inside += abs(message["quantity"])
#             money_spent_inside += abs(message['quantity'] * message["price"])
#         else:  # energy buying
#             message["price"] = buying_price
#             energy_sold_inside += abs(message["quantity"])
#             money_earned_inside += abs(message['quantity'] * message["price"])
#         # catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)
#         print(message)

# todo here we test functionalities of dataloggers in order to send the iteration results to the agent for reward calculation
# def distribute_energy_exchanges(catalog: "Catalog", aggregator: "Aggregator", energy_accorded_to_exchange: dict, grid_topology: list, converter_list: dict, buying_price: float, selling_price: float, message: dict) -> Tuple[float, float, float, float, float, float, float, float]:
#     """
#     This function computes the energy exchanges (direct ones and with conversion systems).
#     Since we don't know how do decisions correspond to energy exchanges, we first verify if they are bound by the min and max.
#     Then we look for the one closest to the nominal.
#     May be subject to change if finally we output the matrix of the grid's topology as in the input to the model.
#     """
#     # initializing
#     energy_bought_inside = 0.0
#     money_spent_inside = 0.0
#     energy_sold_inside = 0.0
#     money_earned_inside = 0.0
#     energy_bought_outside = 0.0
#     money_spent_outside = 0.0
#     energy_sold_outside = 0.0
#     money_earned_outside = 0.0
#
#     aggregator_energy_exchanges_from_grid_topology = []
#     for tup in grid_topology:
#         if aggregator.name in tup:
#             aggregator_energy_exchanges_from_grid_topology.append(tup)
#
#     aggregator_energy_exchanges_from_RL_decision = []
#     dummy_dict = {**energy_accorded_to_exchange}
#     for key, value in energy_accorded_to_exchange.items():
#         if value != 0:
#             aggregator_energy_exchanges_from_RL_decision.append(value)
#             dummy_dict.pop(key)
#     if len(dummy_dict) == len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision):
#         for key, value in dummy_dict.items():
#             aggregator_energy_exchanges_from_RL_decision.append(value)
#     else:
#         for i in range(len(aggregator_energy_exchanges_from_grid_topology) - len(aggregator_energy_exchanges_from_RL_decision)):
#             aggregator_energy_exchanges_from_RL_decision.append(0)
#
#     if len(aggregator_energy_exchanges_from_grid_topology) != len(aggregator_energy_exchanges_from_RL_decision):
#         raise Exception(
#             f"The {aggregator.name}'s occurrences in energy exchanges don't match the corresponding number of decisions taken by the RL !")
#
#     # Quantities concerning energy conversion systems
#     decision_message = {}
#     print("The aggregator does not exchange with its subaggregators nor with its superior aggregator !")
#     for device in converter_list:
#         decision_message[device] = []
#         for element in aggregator_energy_exchanges_from_RL_decision[:]:
#             if converter_list[device]["energy_minimum"] <= element <= converter_list[device]["energy_maximum"]:
#                 decision_message[device].append(element)
#         if len(decision_message[device]) > 1:
#             distance = {}
#             for element in decision_message[device]:
#                 distance[element] = abs(element - converter_list[device]["energy_nominal"])
#             decision_message[device] = min(distance, key=distance.get)
#             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#         else:
#             decision_message[device] = decision_message[device][0]
#             aggregator_energy_exchanges_from_RL_decision.remove(decision_message[device])
#
#         message["quantity"] = decision_message[device]
#         if decision_message[device] < 0:  # energy selling
#             message["price"] = selling_price
#             energy_sold_outside += abs(message["quantity"])
#             money_earned_outside += abs(message['quantity'] * message["price"])
#         else:  # energy buying
#             message["price"] = buying_price
#             energy_bought_outside += abs(message["quantity"])
#             money_spent_outside += abs(message['quantity'] * message["price"])
#         catalog.set(f"{device.name}.{aggregator.nature.name}.energy_accorded", message)
#
#     # Quantities concerning sub-aggregators
#     if aggregator_energy_exchanges_from_RL_decision:
#         for subaggregator in aggregator.subaggregators:
#             decision_message[subaggregator.name] = []
#             quantities_and_prices = catalog.get(f"{subaggregator.name}.{aggregator.nature.name}.energy_wanted")
#             print(f"top-down phase, quantities_and_prices: {quantities_and_prices}")
#             for element in aggregator_energy_exchanges_from_RL_decision[:]:
#                 print(element)
#                 if quantities_and_prices[0]["energy_minimum"] <= element <= quantities_and_prices[0]["energy_maximum"]:
#                     decision_message[subaggregator.name].append(element)
#                 if len(decision_message[subaggregator.name]) > 1:
#                     distance = {}
#                     for element in decision_message[subaggregator.name]:
#                         distance[element] = abs(element - quantities_and_prices["energy_nominal"])
#                     decision_message[subaggregator.name] = min(distance, key=distance.get)
#                     aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
#                 else:
#                     print(decision_message[subaggregator.name])
#                     decision_message[subaggregator.name] = decision_message[subaggregator.name][0]
#                     aggregator_energy_exchanges_from_RL_decision.remove(decision_message[subaggregator.name])
#
#             message["quantity"] = decision_message[subaggregator.name]
#             if decision_message[subaggregator.name] < 0:  # energy selling
#                 message["price"] = selling_price
#                 energy_bought_inside += abs(message["quantity"])
#                 money_spent_inside += abs(message['quantity'] * message["price"])
#             else:  # energy buying
#                 message["price"] = buying_price
#                 energy_sold_inside += abs(message["quantity"])
#                 money_earned_inside += abs(message['quantity'] * message["price"])
#             catalog.set(f"{subaggregator.name}.{aggregator.nature.name}.energy_accorded", message)
#
#     return energy_bought_inside, money_spent_inside, energy_sold_inside, money_earned_inside, energy_bought_outside, money_spent_outside, energy_sold_outside, money_earned_outside
#



