"""
Dataset creation to feed a ClusteringAndStrategy algorithm.
"""
from itertools import permutations
import pandas as pd


# #####################################################################################################################
# dataset creation
def create_points_in_range(value_range: tuple, points_number: int):
    points_list = []
    next_point = value_range[0]
    indent = (value_range[1] - value_range[0]) / (points_number - 1)
    for i in range(points_number):
        points_list.append(next_point)
        next_point += indent

    return points_list


points_per_feature = 10
situation_points_list = []


global_range = [0, 0.25, 0.5, 0.75, 1, 2, 4]


    # load
minimum_consumption_range = (0, 1)
minimum_consumption_ratio_points = create_points_in_range(minimum_consumption_ratio_range, points_per_feature)
situation_points_list.append(minimum_consumption_ratio_points)

minimum_production_range = (0, 1)
minimum_production_ratio_points = create_points_in_range(minimum_production_ratio_range, points_per_feature)
situation_points_list.append(minimum_production_ratio_points)

maximum_production_range = (0, 1)
maximum_production_ratio_points = create_points_in_range(maximum_production_ratio_range, points_per_feature)
situation_points_list.append(maximum_production_ratio_points)

energy_stored_range = (0, 1)


    # price



# generation of dataframe
def create_parametric_list(features_and_points_list):
    buffer_list = [[]]
    for i in range(len(features_and_points_list)):
        final_list = []
        for line in buffer_list:
            final_list += toto(line, features_and_points_list[i])
        buffer_list = final_list

    return final_list


def toto(list_chunk, points_to_add):
    new_list = []
    for i in range(len(points_to_add)):
        new_list.append(list_chunk + [points_to_add[i]])

    return new_list


print("situations")
situations_list = create_parametric_list(situation_points_list)
features_list = ["temperature", "irradiation", "wind_speed", "elec_price", "H2_SOC"]
situations_dataset = pd.DataFrame(situations_list, columns=features_list)
print(situations_dataset)
print()
situations_dataset.to_csv("./SituationsDataset.csv")


# ######################################################################################################################
# strategies set creation
action_set = {"store_H2": None,
              "sell_elec_grid": None,
              }

print("strategies")
strategies_set = list(permutations(action_set.keys()))  # all different orders
print(len(strategies_set))
print(strategies_set)
print()


# # ####################################################################################################################
# # dataset with situations + strategies
# print("both")
# final_list = create_parametric_list(situation_points_list + [strategies_set])
# columns_list = features_list + ["strategies"]
# final_dataset = pd.DataFrame(final_list, columns=columns_list)
# print(final_dataset)