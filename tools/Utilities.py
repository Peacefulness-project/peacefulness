# This sheet regroups little things used to simplify the rest of the program
import os

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

    if os.name == 'nt':
        for i in range(len(blocks) - 1):
            string += blocks[i] + '\\'
        string += blocks[len(blocks) - 1]
    else:
        for i in range(len(blocks) - 1):
            string += blocks[i] + '/'
        string += blocks[len(blocks) - 1]

    return string
