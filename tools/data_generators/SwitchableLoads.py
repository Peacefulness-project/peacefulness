# this file generates a profile adapted for adjustable loads


import random as rnd


file = open("../../usr/Datafiles/DummyShiftableLoadProfile.input", "w")

max_energy = 5
number_of_uses = rnd.randint(50, 365)
rand_time = []

for i in range(number_of_uses):
    # start date
    rand_time.append(rnd.randint(0, 8759))

rand_time.sort()  # uses are sorted in chronological order

for i in range(number_of_uses):

    # early start date
    file.write(f"{rand_time[i]}  ")

    # last start date
    rand_duration = rand_time[i] + rnd.randint(0, 10)
    file.write(f"{rand_duration}  ")

    # consumption during use
    rand_duration = rnd.randint(1, 4)
    consumption = []
    for j in range(rand_duration):
        consumption.append(rnd.random()*max_energy)
    file.write(f"{consumption}\n")


