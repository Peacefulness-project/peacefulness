# This sheet regroups little things used to simplify the rest of the program
from os import listdir, name
import numpy as np
from math import copysign

# normalized separations
little_separation = "---------------------------------------------------------"
middle_separation = "\n---------------------------------------------------------"
big_separation = "\n========================================================="


def list_to_str(dummy_list):  # transform a data list into a string writable in a file
    dummy_list = [str(element) for element in dummy_list]  # transforms a list into a
    # string of several words...
    return "\t".join(dummy_list)  # ... separated by a tabulation


def adapt_path(blocks):  # this function allows to choose / or \ in a path accordingly to user os

    string = ''

    if name == 'nt':  # the name here is the one of the OS
        for i in range(len(blocks) - 1):
            string += blocks[i] + '\\'
        string += blocks[len(blocks) - 1]
    else:
        for i in range(len(blocks) - 1):
            string += blocks[i] + '/'
        string += blocks[len(blocks) - 1]

    return string


def check_zero_one(list_or_array):

    for element in list_or_array:
        if isinstance(element, list) or isinstance(element, np.ndarray):
            check_zero_one(element)
        elif not isinstance(element, float):
            raise Exception("the list must contain only floats")
        else:
            if element < 0 or element > 1:
                print(element)
                raise Exception("all elements must belong to [0;1]")


def into_list(object):  # if the object is not a list, this function will return a list containing only the object
    if not (isinstance(object, list) or isinstance(object, dict)):
        object = [object]

    return object


def sign(number):  # returns the sign of a number
    return copysign(1, number)


def list_files_and_folders(directory):  # this function lists all files and folders in a directory, __init__.py file and __pycache__ excepted
    files_and_folders = listdir(directory)  # a list of all subclasses of this class
    if "__init__.py" in files_and_folders:  # if a __init__.py file is present
        files_and_folders.remove("__init__.py")  # then it is deleted
    if "__pycache__" in files_and_folders:  # if a __pycache__ folder is present
        files_and_folders.remove("__pycache__")  # then it is deleted

    return files_and_folders
