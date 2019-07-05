# this file generates a profile adapted for adjustable loads
# import


# parameters
device_name = "DummyShiftableLoadProfile"
period = 24  # in hours
user_range = 2  # in hours, used to create some randomness in the moment, start would be "base +- offset"
usage_range = 0.1  # in %, used to create some randomness in the consumption of the device

file = open(f"../../usr/Datafiles/{device_name}.input", "w")

epsilon = 1 / 3600  # a little offset of 1 second which allows to stop an usage


# max_energy = 5
# number_of_uses = rnd.randint(50, 365)
# rand_time = []
#
# for i in range(number_of_uses):
#     # start date
#     rand_time.append(rnd.randint(0, 8759))
#
# rand_time.sort()  # uses are sorted in chronological order
#
# for i in range(number_of_uses):
#
#     # early start date
#     file.write(f"{rand_time[i]}  ")
#
#     # last start date
#     rand_duration = rand_time[i] + rnd.randint(1, 10)
#     file.write(f"{rand_duration}  ")
#
#     # consumption during use
#     rand_duration = rnd.randint(1, 4)
#     consumption = []
#     for j in range(rand_duration):
#         consumption.append(rnd.random()*max_energy)
#     file.write(f"{consumption}\n")


# construction of the profile
# user profile
user_profile = []

user_profile.append([0,  8])
user_profile.append([1, 11])
user_profile.append([0, 11+epsilon])

user_profile.append([0, 18])
user_profile.append([1, 21])
user_profile.append([0, 21+epsilon])

# usage profile
usage_profile = []

usage_profile.append([0.5, 0.5])
usage_profile.append([1, 1])
usage_profile.append([0.5, 0.5])

# ##########################################################################################
# writing in the file

file.write(f"{device_name} data\n\n")
file.write(f"duration of the period (in hour): {period}\n")

# user profile
file.write(f"\nuser profile:\n")
file.write("\tpriority\tinstant\n")

for element in user_profile:
    file.write(f"\t{element[0]}\t{element[1]}\n")

# usage profile
file.write(f"\nusage profile:\n")
file.write("\tconsumption\tduration\n")

for element in usage_profile:
    file.write(f"\t{element[0]}\t{element[1]}\n")


