# execute all files in the sub-directory "LOCIE_1/Core_1"
from os import listdir, chdir

chdir("../../../../../")

# autarky
root_path = "cases/Studies/LOCIE_1/FigureRuns/MonthlyVariationSelfConsumption/Autarky/cases/"  # the path to the cases

simulation_mains = listdir(root_path)  # the main corresponding to each case we want to test

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations


# BAU
root_path = "cases/Studies/LOCIE_1/FigureRuns/MonthlyVariationSelfConsumption/BAU/cases/"  # the path to the cases

simulation_mains = listdir(root_path)  # the main corresponding to each case we want to test

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations


# Profitable
root_path = "cases/Studies/LOCIE_1/FigureRuns/MonthlyVariationSelfConsumption/Profitable/cases/"  # the path to the cases

simulation_mains = listdir(root_path)  # the main corresponding to each case we want to test

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations


