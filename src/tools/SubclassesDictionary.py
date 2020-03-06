# the following variable is a dictionary containing all the subclasses available
# Subclasses are useful for the following objects: contracts, devices, strategies, daemons and dataloggers
# as devices are folders and not files, the operation is more subtle
from os import listdir
from importlib import import_module  # this library allows to import modules defined as str
import inspect


def get_subclasses():  # this function returns all subclasses
    subclasses_dictionary = {}

    classes_concerned = ["Contract", "Daemon", "Datalogger", "Device", "Strategy"]  # a list of all classes using subclasses

    for class_name in classes_concerned:
        class_directory = "lib/Subclasses/" + class_name  # the directory containing subclasses of one class
        subclasses_list = listdir(class_directory)  # a list of all subclasses of this class
        subclasses_list.remove("__init__.py")  # we remove the file __init__.py
        subclasses_list.remove("__pycache__")  # we remove the file __pycache__

        for subclass_folder in subclasses_list:  # for each subclass
            subclass_file = "lib.Subclasses." + class_name + "." + subclass_folder + "." + subclass_folder  # the file where the module is defined
            subclass_module = import_module(subclass_file)  # we import the .py file
            for subclass_name, subclass_class in inspect.getmembers(subclass_module):
                if inspect.isclass(subclass_class) and subclass_name != class_name:  # get back only the subclasses
                    subclasses_dictionary[subclass_name] = subclass_class

    return subclasses_dictionary


