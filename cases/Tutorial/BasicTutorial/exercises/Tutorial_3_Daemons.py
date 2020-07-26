# Tutorial 3
# Daemons
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_3_daemons  # a specific importation

# ##############################################################################################
# Usual importations
from datetime import datetime

from os import chdir

from lib.Subclasses.Daemon.PriceManagerDaemon.PriceManagerDaemon import PriceManagerDaemon
from src.common.World import World

from src.common.Nature import Nature
from lib.DefaultNatures.DefaultNatures import *

from lib.Subclasses.Daemon.PriceManagerDaemon import PriceManagerDaemon

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger


# ##############################################################################################
# Rerooting
chdir("../../../../")


# ##############################################################################################
# Importation of subclasses
from src.tools.SubclassesDictionary import get_subclasses
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
               24)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Natures

# low voltage electricity
LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()


# ##############################################################################################
# Daemon

# price managers
# TODO: create a daemon as a price manager with flat price (the standard case), called "heat_prices" and concerning the low temperature heat nature.
#       Its characteristics are:
#       1/ buying energy costs 12 c/kWh
#       2/ energy sold is paid 10 c/kWh

# TODO: create a daemon as a price manager with TOU prices, called "elec_prices" and concerning the low voltage electricity nature.
#       Its characteristics are:
#       1/ buying energy during on-peak hours costs 17 c/kWh
#       2/ buying energy during off-peak hours costs 12 c/kWh
#       3/ energy sold is always paid 15 c/kWh
#       4/ on-peak hours are from 6h to 12h and from 13h to 23h

# limit prices
# TODO: create a limit price manager for low voltage electricity. The price must be between 10 and 20 c/kWh.

# TODO: create a limit price manager for low temperature heat. The price must be between 8 and 14 c/kWh.

# Meteorological daemons
# TODO: create an indoor temperature manager.

# TODO: create the various daemons described below to handle meteorological conditions at a specific location
#       Location is "Pau"
#       The data to manage, and therefore corresponding daemons to create are:
#       1/ outdoor temperature
#       2/ cold water temperature of the water grid
#       3/ irradiation
#       4/ wind

# ##############################################################################################
# Correction
correction_3_daemons()