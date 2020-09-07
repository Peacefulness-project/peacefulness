# execute all files in the sub-directory "LOCIE_1/Core_3"
from os import listdir, chdir


root_path = "cases/Studies/LOCIE_1/Iteration_2/Core_3/"  # the path to the cases

simulation_mains = listdir(root_path)  # the main corresponding to each case we want tot test

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations

