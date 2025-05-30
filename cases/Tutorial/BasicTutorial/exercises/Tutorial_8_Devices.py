# Tutorial 8
# Devices
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_8_devices  # a specific importation

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

# TODO: create a device of 'Photovoltaics' type, called "PV_field"
#       Its characteristics are:
#       1/ its contract is an "EgoistContract" contract for the low voltage electricity nature (see above, BAU_elec)
#       2/ owned by the agent "producer"
#       3/ supervised by the aggregator "aggregator_elec"
#       For the technical features:
#       4/ technical profile is "standard_field"
#       5/ surface is 1000 m2
#       6/ location is "Pau"

# TODO: create a device of 'WindTurbine' type, called "wind_turbine"
#       Its characteristics are:
#       1/ its contract is a "CurtailmentContract" for the low voltage electricity nature (see above, curtailment_elec)
#       2/ owned by the agent "producer"
#       3/ supervised by the aggregator "aggregator_elec"
#       For the technical features:
#       4/ technical profile is "standard"
#       5/ location is "Pau"

# TODO: create a device of 'Background' type, called "background"
#       Its characteristics are:
#       1/ its contract is an "EgoistContract" contract for the low voltage electricity nature (see above, BAU_elec)
#       2/ owned by the agent "consumer"
#       3/ supervised by the aggregator "aggregator_elec"
#       For the technical features:
#       4/ user profile is "family"
#       5/ technical profile is "family"

# TODO: create a device of 'Dishwasher' type, called "dishwasher"
#       Its characteristics are:
#       1/ its contract is an "EgoistContract" contract for the low voltage electricity nature (see above, BAU_elec)
#       2/ owned by the agent "consumer"
#       3/ supervised by the aggregator "aggregator_elec"
#       For the technical features:
#       4/ user profile is "family"
#       5/ technical profile is "medium_consumption"

# TODO: create a device of 'HotWaterTank' type, called "hot_water_tank"
#       Its characteristics are:
#       1/ its contract is a "CooperativeContract" for the low temperature heat nature (see above, cooperative_heat)
#       2/ owned by the agent "consumer"
#       3/ supervised by the aggregator "aggregator_heat"
#       For the technical features:
#       4/ user profile is "family"
#       5/ technical profile is "family_heat"

# TODO: create a device of 'Heating' type, called "heating"
#       Its characteristics are:
#       1/ its contract is a "CooperativeContract" for the low temperature heat nature (see above, cooperative_heat)
#       2/ owned by the agent "consumer"
#       3/ supervised by the aggregator "aggregator_heat"
#       For the technical features:
#       4/ user profile is "residential"
#       5/ technical profile is "house_heat"
#       6/ location is "Pau"
#       7/ its initial temperature is 15°C


# ##############################################################################################
# Correction
correction_8_devices()


