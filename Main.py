# This file executes all the simulations presented in the article
# It can be quite long...

# execute all files in the sub-directory "SEGY_2024/cases"
from os import listdir


root_path = "cases/Studies/SEGY_2024/all_cases/"  # the path to the cases

simulation_mains = listdir(root_path)  # the main corresponding to each case we want tot test

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations

