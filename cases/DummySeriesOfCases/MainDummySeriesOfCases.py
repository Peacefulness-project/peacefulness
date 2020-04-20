# execute all files in the sub-directory "cases_to_be_run"
from os import listdir, chdir


chdir("../../")  # the local environment is set at the root of the project
# it allows to import easily the different modules

path_to_cases = "cases/DummySeriesOfCases/cases_to_be_run/"  # the directories where cases can be found seen from the root of the project

simulation_mains = listdir(path_to_cases)  # the scripts corresponding to the cases we want to run

for file_path in simulation_mains:
    exec(open(path_to_cases + file_path).read(), globals())  # to execute the different simulations

