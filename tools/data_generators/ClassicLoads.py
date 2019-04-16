# this file generates a table of 365x24 numbers

import random as rnd

file = open("../../usr/Datafiles/DummyProductionProfile.input", "w")

max = 5

for i in range(365):
    for j in range(23):
        file.write(f"{rnd.random()*max}\t")
    file.write(f"{rnd.random()*max}")
    file.write("\n")



