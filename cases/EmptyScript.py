# This script is here to help not loose yourself when creating a case.

# ##############################################################################################
# Importations
from datetime import datetime

from os import chdir

from src.common.World import World

from src.common.Nature import Nature
from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses

# ##############################################################################################
# Minimum
# the following objects are necessary for the simulation to be performed
# you need exactly one object of each type
# ##############################################################################################

# ##############################################################################################
# Rerooting
chdir("the_path")  # here, you have to put the path to the root of project (the main directory)


# ##############################################################################################
# Importation of subclasses
# all the subclasses are imported in the following dictionary
subclasses_dictionary = get_subclasses()

# ##############################################################################################
# Creation of the world
# a world contains all the other elements of the model
# a world needs just a name
name_world = "your_name"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
world.set_directory("the_path")  # here, you have to put the path to your results directory


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("seed")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
world.set_time(start_date,  # time management: start date
               integer,  # value of a time step (in hours)
               integer)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Creation of nature


# ##############################################################################################
# Creation of daemons


# ##############################################################################################
# Creation of strategies


# ##############################################################################################
# Manual creation of agents


# ##############################################################################################
# Manual creation of contracts


# ##############################################################################################
# Creation of aggregators


# ##############################################################################################
# Manual creation of devices


# ##############################################################################################
# Automated generation of complete agents (i.e with devices and contracts)


# ##############################################################################################
# Creation of dataloggers


# ##############################################################################################
# here we have the possibility to save the world to use it later
# world.save()  # saving the world for a later use


# ##############################################################################################
# Simulation start
world.start()



