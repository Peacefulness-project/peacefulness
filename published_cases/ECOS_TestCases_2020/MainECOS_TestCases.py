# execute all files in the sub-directory "SFT2020"
from os import listdir, chdir
# from tools.GraphAndTex import graph_SFT


# chdir("../../")

# set the relative path to the project root
root_path = "published_cases/ECOS_TestCases_2020/cases/"

simulation_mains = listdir(root_path)  # the main corresponding to each case we want tot test

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations

# post-processing
root_path = "published_cases/SFT2020/Results/"
path = root_path + "Autarky_emergency_high_DSM/Case_24_01_2020-09_02_59/outputs/"

# graph_SFT(path)

