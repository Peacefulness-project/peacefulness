# Tutorial 1
# Settings
from cases.Tutorial.BasicTutorial.AdidtionalData.Correction_scripts import correction_1_settings  # a specific importation

# ##############################################################################################
# Usual importations
from datetime import datetime

from os import chdir, listdir

from src.common.World import World

from src.common.Nature import Nature
from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

# ##############################################################################################
# Importation of subclasses
from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


# ##############################################################################################
# Settings
# ##############################################################################################

# ##############################################################################################
# Creation of the world
# TODO: create a world called tuto_world
name_world = "tuto_world"
world = World(name_world)  # creation

# ##############################################################################################
# Definition of the path to the files
# TODO: export the results in cases/Tutorial/BasicTutorial/Results/Settings
pathExport = "cases/Tutorial/BasicTutorial/Results/Settings"
world.set_directory(pathExport)

# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
# TODO: set sunflower as the seed for the random generator
world.set_random_seed("sunflower")

# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
# TODO: set the start date at the 1st January of 2019, 00:00 AM, the time step at 2 hours and the duration of the simulation at 1 week (<=> 168 hours)
start_date = datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               2,  # value of a time step (in hours)
               84)  # number of time steps simulated

# ##############################################################################################
# Correction
correction_1_settings()