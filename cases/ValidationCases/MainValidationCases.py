# execute all the validation cases
from os import listdir, chdir, makedirs
from datetime import datetime

from src.tools.Utilities import little_separation
from lib.Subclasses.Daemon.ValidationDaemon.GlobalProblem import get_problem, set_problem

chdir("../../")  # set the relative path to the project root

root_path = "cases/ValidationCases/cases/"  # the path to the cases

simulation_mains = listdir(root_path)  # the main corresponding to each case we want tot test
problem_list = list()  # a list of all the tests where a problem occured

for file_path in simulation_mains:
    exec(open(root_path + file_path).read(), globals())  # to execute the different simulations
    if get_problem():  # if a problem occured
        problem_list.append(file_path)
    set_problem(False)

# summary
# creation of the file
instant_date = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
makedirs(f"cases/ValidationCases/Results/Summary/Tests_{str(instant_date)}")
file = open(f"cases/ValidationCases/Results/Summary/Tests_{str(instant_date)}/summary.txt", "a+")  # the file resuming the results of the tests

# redaction of the file
message = f"Summary of the test\n"
print(f"{little_separation}\n"+message)
file.write(f"{message}")
if bool(problem_list):  # if a problem occured
    message = f"a problem occurred in the following tests:{problem_list}"
    print(message)
    file.write(f"{message}")
else:
    message = f"The test run was checking the following elements:\n"
    for file_path in simulation_mains:
        message += f"\t=> {file_path} \n"
    message += "Finally, no problem occurred\n"
    print(message)
    file.write(f"{message}\n")

file.close()
