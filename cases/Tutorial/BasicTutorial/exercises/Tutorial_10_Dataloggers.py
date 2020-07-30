# Tutorial 10
# Dataloggers
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_10_dataloggers  # a specific importation

# ##############################################################################################
# Usual importations
from datetime import datetime

from os import chdir

from src.common.World import World

from src.common.Nature import Nature
from lib.DefaultNatures.DefaultNatures import *

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

LVE = load_low_voltage_electricity()

LTH = load_low_temperature_heat()

Nature("PW", "Pressurized Water")

# ##############################################################################################
# Daemon

# price managers
price_manager_TOU_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("elec_prices", {"nature": LVE.name, "buying_price": [0.17, 0.12], "selling_price": [0.15, 0.15], "on-peak_hours": [[6, 12], [13, 22]]})

price_manager_flat_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("heat_prices", {"nature": LTH.name, "buying_price": 0.12, "selling_price": 0.10})

# limit prices
limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.20, "limit_selling_price": 0.10})

limit_price_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.14, "limit_selling_price": 0.08})

# Meteorological daemons
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterDaemon"]({"location": "Pau"})

irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

wind_daemon = subclasses_dictionary["Daemon"]["WindDaemon"]({"location": "Pau"})


# ##############################################################################################
# Strategy

grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

elec_strategy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

heat_strategy = subclasses_dictionary["Strategy"]["LightAutarkyEmergency"]()


# ##############################################################################################
# Agent

producer = Agent("producer")

aggregator_owner = Agent("aggregators_owner")

consumer = Agent("consumer")


# ##############################################################################################
# Contract

BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("elec_contract_egoist", LVE, price_manager_TOU_elec)

curtailment_elec = subclasses_dictionary["Contract"]["CurtailmentContract"]("elec_contract_curtailment", LVE, price_manager_TOU_elec)

BAU_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("heat_contract_cooperative", LTH, price_manager_flat_heat)


# ##############################################################################################
# Aggregator

aggregator_grid = Aggregator("grid", LVE, grid_strategy, aggregator_owner)

aggregator_elec = Aggregator("aggregator_elec", LVE, elec_strategy, aggregator_owner, aggregator_grid, BAU_elec)  # creation of a aggregator

aggregator_heat = Aggregator("aggregator_heat", LTH, heat_strategy, aggregator_owner, aggregator_elec, BAU_elec, efficiency=3.5, capacity=1000)  # creation of a aggregator


# ##############################################################################################
# Device

subclasses_dictionary["Device"]["PV"]("PV_field", BAU_elec, producer, aggregator_elec, "standard_field", {"surface": 1000, "location": "Pau"})

subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", curtailment_elec, producer, aggregator_elec, "standard", {"location": "Pau"})

subclasses_dictionary["Device"]["Background"]("background", BAU_elec, consumer, aggregator_elec, "family", "family")

subclasses_dictionary["Device"]["Dishwasher"]("dishwasher", BAU_elec, consumer, aggregator_elec, "family", "medium_consumption")

subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank", BAU_heat, consumer, aggregator_heat, "family", "family_heat")

subclasses_dictionary["Device"]["Heating"]("heating", BAU_heat, consumer, aggregator_heat, "residential", "house_heat", {"location": "Pau"})

# ##############################################################################################
# Automated generation of agents

world.agent_generation(500, "lib/AgentTemplates/DummyAgent.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_TOU_elec, "LTH": price_manager_flat_heat})


# ##############################################################################################
# Datalogger

# TODO: create a datalogger of the subclass "SelfSufficiencyDatalogger" with a period of 1
subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](1)

# TODO: create a datalogger of the subclass "NatureBalancesDatalogger" with a period "global"
subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]("global")

# TODO: create a datalogger called "consumer_datalogger", exporting data to the file "ConsumerData" with a period of 2 rounds
consumer_datalogger = Datalogger("consumer_datalogger", "ConsumerData", 2)

# TODO: add the key "simulation_time" as the "X" axis for "consumer_datalogger"
consumer_datalogger.add("simulation_time", graph_status="X")

# TODO: add the following keys as "Y" series to "consumer_datalogger": "consumer.LVE.energy_bought", "consumer.LTH.energy_bought", "consumer.money_spent"
consumer_datalogger.add("consumer.LVE.energy_bought")
consumer_datalogger.add("consumer.LTH.energy_bought")
consumer_datalogger.add("consumer.money_spent")


# ##############################################################################################
# Correction
correction_10_dataloggers()


