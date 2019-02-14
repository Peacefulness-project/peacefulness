# Predefinite data-processing function:
# The following functions are basics function for data processing
# They can serve as examples for yours
import numpy as np

def identity(dict_content, catalog):
    result_list = []
    for i in range(len(dict_content[0])):
        result_list.append(catalog.get(dict_content[1][i]))
    return result_list


def sum_over_time(dict_content, catalog):
    if dict_content[3] == []:  # initialization: if the counter does not exist...
        dict_content[3] = [0 for element in dict_content[0]]  # ... it is set to 0
    result_list = []
    for i in range(len(dict_content[0])):
        dict_content[3][i] += catalog.get(dict_content[1][i])
        result_list.append(dict_content[3][i])
    return result_list


def mean(dict_content, catalog):
    result_list = []
    temp_counter = 0
    for i in range(len(dict_content[0])):
        for j in range(len(dict_content[1][i])):
            temp_counter += catalog.get(dict_content[1][i][j])
        result_list.append(temp_counter/(len(dict_content[0])+1))
    return result_list


def data_min(dict_content, catalog):
    result_list = []
    for i in range(len(dict_content[0])):
        temp_list = []
        for j in range(len(dict_content[1][i])):
            temp_list.append(catalog.get(dict_content[1][i][j]))
        result_list.append(min(temp_list))
    return result_list


def data_max(dict_content, catalog):
    result_list = []
    for i in range(len(dict_content[0])):
        temp_list = []
        for j in range(len(dict_content[1][i])):
            temp_list.append(catalog.get(dict_content[1][i][j]))
        result_list.append(max(temp_list))
    return result_list

# Personalized data processing functions

# example_function(dict_content=[header_list, keys_list, example_function, things_you_added],
#                  catalog= data catalog of the logger)
#   your_personalized_data_processing
#   return list_of_the_data_you_want_to_be_written


def dummy_data_function(dict_content, catalog):
    result_list = []
    for i in range(len(dict_content[0])):
        result_list.append(dict_content[3])
    return result_list
