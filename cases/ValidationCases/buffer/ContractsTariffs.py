# This script checks that the billing works well for contracts

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
world.set_directory("cases/ValidationCases/Results/ContractsTariffs")  # here, you have to put the path to your results directory


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
# Model
# ##############################################################################################

# ##############################################################################################
# Creation of strategies
# the different distribution strategies
strategy_elec = subclasses_dictionary["Strategy"]["LightAutarkyEmergency"]()

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Creation of nature
# low voltage electricity
LVE = load_low_voltage_electricity()


# ##############################################################################################
# Creation of daemons
price_manager_elec_flat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices", {"nature": LVE.name, "buying_price": 0.1, "selling_price": 0})  # sets prices for flat rate
price_manager_elec_TOU = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices", {"nature": LVE.name, "buying_price": [0.1, 0.2], "selling_price": [0, 0], "hours": [[6, 22]]})  # sets prices for flat rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator


# ##############################################################################################
# Manual creation of agents
flat_owner = Agent("flat_owner")
TOU_owner = Agent("TOU_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
flat_elec_contract = subclasses_dictionary["Contract"]["FlatEgoistContract"]("flat_elec_contract", LVE, price_manager_elec_flat)

TOU_elec_contract = subclasses_dictionary["Contract"]["TOUEgoistContract"]("TOU_elec_contract", LVE, price_manager_elec_TOU)


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_elec = Aggregator("local_grid", LVE, strategy_elec, aggregators_manager, aggregator_grid, flat_elec_contract)


# ##############################################################################################
# Manual creation of devices

# Each device is created 3 times
# BAU contract
subclasses_dictionary["Device"]["Background"]("flat_device", flat_elec_contract, flat_owner, aggregator_elec, "dummy_user", "dummy_usage", "cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# Cooperative contract
subclasses_dictionary["Device"]["Background"]("TOU_device", TOU_elec_contract, TOU_owner, aggregator_elec, "dummy_user", "dummy_usage", "cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that the billing works well for contracts."


reference_values = {"flat_owner.money_spent": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3],
                    "TOU_owner.money_spent": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 2.2, 2.3],
                    }

filename = "contracts_tariffs_validation"

parameters = {"description": description, "reference_values": reference_values, "filename": filename, "tolerance": 1E-6}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("contracts_tariffs_test", parameters)


# ##############################################################################################
# Simulation start
world.start()



