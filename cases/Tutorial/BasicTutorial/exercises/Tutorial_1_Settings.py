# Tutorial 1
# Settings
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_1_settings  # a specific importation

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
# TODO: create a world called tuto_world

# ##############################################################################################
# Definition of the path to the files
# TODO: export the results in cases/Tutorial/BasicTutorial/Results/Settings


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
# TODO: set the string "sunflower" as the seed for the random generator


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
# TODO: set the start date at the 1st January of 2019, 00:00 AM, the time step at 1 hour and the duration of the simulation at 1 week (<=> 168 hours)


# ##############################################################################################
# Correction
correction_1_settings()

