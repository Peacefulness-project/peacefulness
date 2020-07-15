# This script checks that agents hierarchy balances work well

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
# Importation of subclasses
# all the subclasses are imported in the following dictionary
subclasses_dictionary = get_subclasses()

# ##############################################################################################
# Creation of the world
# a world contains all the other elements of the model
# a world needs just a name
name_world = "validation"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
world.set_directory("cases/ValidationCases/Results/Agents")  # here, you have to put the path to your results directory


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("seed")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24)  # number of time steps simulated


# ##############################################################################################
# Definition of the type of exports
export_formats = ["csv", "LaTeX", "matplotlib"]
export_formats = ["csv"]
world.choose_exports(export_formats)

# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Creation of nature
# low voltage electricity
LVE = load_low_voltage_electricity()


# ##############################################################################################
# Creation of daemons
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # sets prices for flat rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0, "limit_selling_price": 0})  # sets prices for the system operator


# ##############################################################################################
# Creation of strategies
# BAU strategy
strategy_elec = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
sup_agent = Agent("sup_agent")

inf_agent = Agent("inf_agent", sup_agent)

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec)


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_elec = Aggregator("local_grid", LVE, strategy_elec, aggregators_manager, aggregator_grid, BAU_elec)


# ##############################################################################################
# Manual creation of devices
device_sup = subclasses_dictionary["Device"]["Background"]("device_sup", BAU_elec, sup_agent, aggregator_elec, "dummy_user", "dummy_usage", "cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

device_inf = subclasses_dictionary["Device"]["Background"]("device_inf", BAU_elec, inf_agent, aggregator_elec, "dummy_user", "dummy_usage", "cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that agents hierarchy balances work well"

filename = "agents_validation"

reference_values = {"sup_agent.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46],
                    "inf_agent.LVE.energy_bought": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
                    }

reference_values_labels = {"abscissa": "hour",
                           "sup_agent.LVE.energy_bought": "toto",
                           "inf_agent.LVE.energy_bought": "titi"
                    }

parameters = {"description": description, "filename": filename, "reference_values": reference_values, "reference_values_labels": reference_values_labels, "tolerance": 1E-6}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("agents_test", parameters)


# ##############################################################################################
# Simulation start
world.start()








