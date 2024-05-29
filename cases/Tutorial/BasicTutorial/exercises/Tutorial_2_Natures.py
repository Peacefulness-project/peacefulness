# Tutorial 2
# Natures
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_2_natures  # a specific importation

# ##############################################################################################
# Usual importations
from datetime import datetime

from src.tools.AgentGenerator import agent_generation

from src.common.Strategy import *
from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses

from src.tools.GraphAndTex import GraphOptions

subclasses_dictionary = get_subclasses()


# ##############################################################################################
# Settings
# ##############################################################################################

# ##############################################################################################
# Creation of the world
name_world = "tuto_world"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
pathExport = "cases/Tutorial/BasicTutorial/Results"
world.set_directory(pathExport)


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("sunflower")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               168)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Natures
# TODO: load the function that creates a nature whose type is low voltage electricity

# TODO: load the function that creates a nature whose type is low temperature heat

# TODO: create a new type of nature, called PW, with the following description: "Pressurized Water"

# ##############################################################################################
# Correction
correction_2_natures()