# this file generates a table of 365x24 numbers between 0 and 1

import random as rnd

file = open("../../usr/Datafiles/DummyBaseloadProfile.input", "w")

for i in range(365):
    for j in range(23):
        file.write(f"{rnd.random()}\t")
    file.write(f"{rnd.random()}")
    file.write("\n")



