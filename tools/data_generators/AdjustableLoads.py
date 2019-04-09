# this file generates a profile adapted for adjustable loads


import random as rnd


file = open("../../usr/Datafiles/DummyAdjustableLoadProfile.input", "w")


for i in range(rnd.randint(50, 365)):

    # start date
    rand_time = rnd.randint(0, 8759)
    file.write(f"{rand_time}  ")

    # consumption during use
    rand_time = rnd.randint(1, 4)
    consumption = []
    for j in range(rand_time):
        consumption.append(rnd.random())
    file.write(f"{consumption}\n")


