# the following variable is a dictionary containing all the subclasses available
# Subclasses are useful for the following objects: contracts, devices, strategies, daemons and dataloggers
# as devices are folders and not files, the operation is more subtle
from importlib import import_module  # this library allows to import modules defined as str
import inspect

from src.tools.Utilities import list_files_and_folders


def get_subclasses():  # this function returns all subclasses
    subclasses_dictionary = {}  # a dictionary containing all the subclasses

    classes_concerned = list_files_and_folders("lib/Subclasses/")  # the list of all classes concerned by subclasses

    for class_name in classes_concerned:
        class_directory = "lib/Subclasses/" + class_name  # the directory containing subclasses of one class
        subclasses_list = list_files_and_folders(class_directory)  # list of all subclasses for a given class

        for subclass_folder in subclasses_list:  # for each subclass
            subclass_file = "lib.Subclasses." + class_name + "." + subclass_folder + "." + subclass_folder  # the file where the module is defined
            subclass_module = import_module(subclass_file)  # we import the .py file
            for subclass_name, subclass_class in inspect.getmembers(subclass_module):
                if inspect.isclass(subclass_class) and subclass_name != class_name:  # get back only the subclasses
                    subclasses_dictionary[subclass_name] = subclass_class  # the subclass is added to the subclass list
                # todo: trouver un moyen d'esquiver les exceptions et les classes intermédiaires de devices pour pouvoir lever une erreur

    return subclasses_dictionary


