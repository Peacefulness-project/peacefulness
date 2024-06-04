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


# TODO here we tested how to send the information message to my code
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



