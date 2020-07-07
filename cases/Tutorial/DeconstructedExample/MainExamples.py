# execute all files in the sub-directory "AgentTemplates"
from os import listdir, chdir


chdir("../../../")  # set the relative path to the project root

root_path = "cases/Tutorial/DeconstructedExample/cases/"  # the path to the cases

simulation_mains = listdir(root_path)  # the main corresponding to each case we want tot test

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations

