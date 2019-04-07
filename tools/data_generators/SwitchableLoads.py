import random as rnd


file = open("../../usr/Datafiles/DummyShiftableLoadProfile.input", "w")


for i in range(rnd.randint(50, 365)):

    # early start date
    rand_time = rnd.randint(0, 8759)
    file.write(f"{rand_time}  ")

    # last start date
    rand_time += rnd.randint(0, 10)
    file.write(f"{rand_time}  ")

    # consumption during use
    rand_time = rnd.randint(1, 4)
    consumption = []
    for j in range(rand_time):
        consumption.append(rnd.random())
    file.write(f"{consumption}")


