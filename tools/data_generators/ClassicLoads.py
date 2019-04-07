import numpy as np
import random as rnd

file = open("../../usr/Datafiles/DummyProductionProfile.input", "w")

for i in range(365):
    for j in range(23):
        file.write(f"{rnd.random()}\t")
    file.write(f"{rnd.random()}")
    file.write("\n")



