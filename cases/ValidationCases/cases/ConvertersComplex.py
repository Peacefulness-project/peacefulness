# This script checks that converters are working well.

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
world.set_directory("cases/ValidationCases/Results/ConvertersComplex")  # here, you have to put the path to your results directory


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
# Creation of nature
# low voltage electricity
LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()

# ##############################################################################################
# Creation of daemons
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # sets prices for flat rate
price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("prices_heat", {"location": "France"})  # sets prices for flat rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator
subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator


# ##############################################################################################
# Creation of strategies

# BAU strategy
BAU_strategy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# BAU strategy
autarky_strategy = subclasses_dictionary["Strategy"]["AutarkyEmergency"]()

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
background_owner = Agent("background_owner")
converter_owner = Agent("converter_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
BAU_contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_contract_elec", LVE, price_manager_elec)
curtailment_contract_heat = subclasses_dictionary["Contract"]["CurtailmentContract"]("curtailment_contract_heat", LTH, price_manager_heat)
threshold_contract_heat = subclasses_dictionary["Contract"]["ThresholdPricesContract"]("threshold_contract_heat", LTH, price_manager_heat, {"buying_threshold": 0, "selling_threshold": 0.2})


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_elec = Aggregator("aggregator_elec", LVE, BAU_strategy, aggregators_manager, aggregator_grid, BAU_contract_elec)

aggregator_heat = Aggregator("aggregator_heat", LTH, autarky_strategy, aggregators_manager)


# ##############################################################################################
# Manual creation of devices
subclasses_dictionary["Device"]["Background"]("background", curtailment_contract_heat, background_owner, aggregator_heat, "dummy_user", "dummy_usage_heat", "cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
subclasses_dictionary["Device"]["HeatPump"]("converter", [BAU_contract_elec, threshold_contract_heat], converter_owner, aggregator_elec, aggregator_heat, "dummy_heat_pump", "cases/ValidationCases/AdditionalData/DevicesProfiles/HeatPump.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that converters are working well."


reference_values = {"background_owner.LTH.energy_bought": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 19, 20, 21, 22, 22],
                    "converter_owner.LVE.energy_bought": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9.5, 10, 10.5, 11, 11],
                    "converter_owner.LTH.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 19, 20, 21, 22, 22]
                    }

filename = "converters_validation"

parameters = {"description": description, "reference_values": reference_values, "filename": filename, "tolerance": 1E-6}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("devices_test", parameters)


# ##############################################################################################
# Simulation start
world.start()






