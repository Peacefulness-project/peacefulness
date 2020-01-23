# execute all files in a directory
# regarder s'il y a un truc Python pour ça
from os import listdir, chdir

# set the relative path to the project root
chdir("../../")

root_path = "published_cases/SFT2020/cases/"

simulation_mains = listdir(root_path)  # the main corresponding to each case we want tot test

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations



