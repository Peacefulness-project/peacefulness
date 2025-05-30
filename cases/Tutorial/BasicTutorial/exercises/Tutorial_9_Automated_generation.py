# Tutorial 9
# Automated generation
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_9_automatic_generation  # a specific importation

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

aggregator_grid = Aggregator("grid", LVE, grid_strategy, aggregator_owner)

aggregator_elec = Aggregator("aggregator_elec", LVE, elec_strategy, aggregator_owner, aggregator_grid, BAU_elec)  # creation of a aggregator

aggregator_heat = Aggregator("aggregator_heat", LTH, heat_strategy, aggregator_owner, aggregator_elec, BAU_elec, efficiency=3.5, capacity={"buying": 10000, "selling": 0})  # creation of a aggregator


# ##############################################################################################
# Device

subclasses_dictionary["Device"]["Photovoltaics"]("PV_field", BAU_elec, producer, aggregator_elec, {"device": "standard_field"}, {"panels": 500, "irradiation_daemon": irradiation_daemon.name})

subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", curtailment_elec, producer, aggregator_elec, {"device": "standard"}, {"wind_speed_daemon": wind_daemon.name})

subclasses_dictionary["Device"]["Background"]("background", BAU_elec, consumer, aggregator_elec, {"user": "family", "device": "family"})

subclasses_dictionary["Device"]["Dishwasher"]("dishwasher", BAU_elec, consumer, aggregator_elec, {"user": "family", "device": "medium_consumption"})

subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank", cooperative_heat, consumer, aggregator_heat, {"user": "family", "device": "family_heat"}, {"cold_water_temperature_daemon": water_temperature_daemon.name})

subclasses_dictionary["Device"]["Heating"]("heating", cooperative_heat, consumer, aggregator_heat, {"user": "residential", "device": "house_heat"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name, "initial_temperature": 15})


# ##############################################################################################
# Automated generation of agents

# TODO: create automatically a group of 50 agents, called "little_district", using the template "DummyAgent.json".
#       Its characteristics are:
#       1/ supervised by the aggregators "aggregators_elec" and "aggregators_heat"
#       2/ management of prices done by the daemon "price_manager_TOU_elec" for the low voltage electricity, and by the daemon "price_manager_heat" for the low temperature heat


# ##############################################################################################
# Correction
correction_9_automatic_generation()


