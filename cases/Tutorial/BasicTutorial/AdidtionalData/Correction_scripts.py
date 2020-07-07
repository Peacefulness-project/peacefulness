# The correction_1_settings on the tutorial 1 bearing on settings
from src.tools.GlobalWorld import get_world
from datetime import datetime


def correction_1_settings():
    world = get_world()

    # creation of world
    if world == None:
        print("The world has not been created successfully.")
        exit()

    # name of world
    if world.name != "tuto_world":
        print("The world does not bear the correct name.")
        exit()

    # creation of path
    if "path" not in world.catalog.keys:
        print("The path has not been successfully defined.")
        exit()

    # path itself
    if world.catalog.get("path") != "cases/Tutorial/BasicTutorial/Results/Settings/Case_" + str(datetime.now().strftime("%Y_%m_%d-%H_%M_%S")):
        print("The path is not the good one.")
        exit()

    # creation of the seed
    if "float" not in world.catalog.keys:
        print("The random seed has not been successfully defined.")
        exit()

    # name of the seed
    if world._random_seed != "sunflower":
        print("The random seed is not the good one.")
        exit()

    # time settings
    if "physical_time" not in world.catalog.keys:
        print("The time settings have not been successfully defined.")
        exit()

    # start date
    if world._catalog.get("physical_time") != datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0):
        print("The start date is not the good one.")
        exit()

    # time step value
    if world._catalog.get("time_step") != 2:
        print("The time step value is not the good one.")
        exit()

    # length
    if world._catalog.get("time_limit") != 84:
        print("The time limit is not the good one.")
        exit()

    print("Congratulations, everything is working well.")


