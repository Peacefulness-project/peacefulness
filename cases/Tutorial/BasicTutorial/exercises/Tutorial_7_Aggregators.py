# Tutorial 7
# Aggregators
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_7_aggregators  # a specific importation

# ##############################################################################################
# Usual importations
from datetime import datetime

from src.common.World import World

from src.common.Strategy import *
from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

from src.tools.GraphAndTex import GraphOptions


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
               168)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Natures

LVE = load_low_voltage_electricity()

LTH = load_low_temperature_heat()

Nature("PW", "Pressurized Water")

# ##############################################################################################
# Daemon

# price managers
price_manager_TOU_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("elec_prices", {"nature": LVE.name, "buying_price": [0.17, 0.12], "selling_price": [0.15, 0.15], "on-peak_hours": [[6, 12], [13, 23]]})

price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("heat_prices", {"nature": LTH.name, "buying_price": 0.12, "selling_price": 0.10})

# limit prices
limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.20, "limit_selling_price": 0.10})

limit_price_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.14, "limit_selling_price": 0.08})

# Meteorological daemons
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Pau"})

sun_position_daemon = subclasses_dictionary["Daemon"]["SunPositionDaemon"]({"location": "Pau"})

water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "GavedePau_Pau"})


# ##############################################################################################
# Strategy

grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

elec_strategy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

heat_strategy = subclasses_dictionary["Strategy"]["LightAutarkyFullButFew"](get_emergency)


# ##############################################################################################
# Agent

producer = Agent("producer")

aggregator_owner = Agent("aggregators_owner")

consumer = Agent("consumer")


# ##############################################################################################
# Contract

BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("elec_contract_egoist", LVE, price_manager_TOU_elec)

curtailment_elec = subclasses_dictionary["Contract"]["CurtailmentContract"]("elec_contract_curtailment", LVE, price_manager_TOU_elec)

cooperative_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("heat_contract_cooperative", LTH, price_manager_heat)


# ##############################################################################################
# Aggregator

# TODO: create a general electrical aggregator called "grid"
#       Its characteristics are:
#       1/ associated with the low voltage electricity nature (see above, LVE)
#       2/ applying the "Grid" strategy (see above, grid_strategy)
#       3/ owned by the agent "aggregators_owner"
#

# TODO: create an aggregator called "aggregator_elec"
#       Its characteristics are:
#       1/ associated with the low voltage electricity nature (see above, LVE)
#       2/ applying the strategy "AlwaysSatisfied" (see above, elec_strategy)
#       3/ owned by the agent "aggregators_owner"
#       4/ its superior is the aggregator "grid" (see above, aggregator_grid)
#       5/ its contract is business as usual for electricity (see above, BAU_elec)

# TODO: create an aggregator called "aggregator_heat"
#       Its characteristics are:
#       1/ associated with the low temperature nature (see above, LTH)
#       2/ applying the strategy "AutarkyEmergencyFullButFew" (see above, heat_strategy)
#       3/ owned by the agent "aggregators_owner"
#       4/ its superior with the general electrical aggregator (see above, aggregator_grid)
#       5/ its contract is business as usual "EgoistContract" (see above, BAU_elec)
#       6/ efficiency of 3.5
#       7/ max power of 1 MW from electricity to heat and 0 from heat to electricity


# ##############################################################################################
# Correction
correction_7_aggregators()


