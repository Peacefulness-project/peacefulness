# This script is the one given in example in the github wiki.


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
# ##############################################################################################

# here, we reroot this script at the root of the project.
chdir("../../")  # root of the project


# ##############################################################################################
# Importation of subclasses
# all the subclasses are imported in the following dictionary
subclasses_dictionary = get_subclasses()


# ##############################################################################################
# Creation of the world
# a world contains all the other elements of the model
# a world needs just a name
name_world = "Disc World"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
pathExport = "cases/TutorialAndExamples/Results/disc_world"
world.set_directory(pathExport)  # registration


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("tournesol")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24*365)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Creation of supervisors

# the BAU strategy
strategy_elec = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# the heat strategy
strategy_heat = subclasses_dictionary["Strategy"]["SubaggregatorHeatEmergency"]()

# the strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Creation of nature

# low voltage electricity
LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()

# user-made nature
name = "orgone"
description = "The mysterious energy of life, according to the pseudo-scientific theory of Wilhelm Reich."
orgone = Nature(name, description)


# ##############################################################################################
# Creation of aggregators

# we create a first aggregator who represents the national electrical grid
aggregator_name = "Enedis"
aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy)

# here we create a second one put under the orders of the first
aggregator_name = "general_aggregator"
aggregator_elec = Aggregator(aggregator_name, LVE, strategy_elec, aggregator_grid)  # creation of a aggregator

# here we create another aggregator dedicated to heat, under the order of the local electrical grid
aggregator_name = "Local_DHN"
aggregator_heat = Aggregator(aggregator_name, LTH, strategy_heat, 3.6, 2000)  # creation of a aggregator


# ##############################################################################################
# Manual creation of contracts

# producers
TOU_prices = "TOU_prices"
BAU_elec = subclasses_dictionary["Contract"]["TOUEgoistContract"]("BAU_elec", LVE, TOU_prices)

flat_prices_elec = "flat_prices_elec"
cooperative_contract_elec = subclasses_dictionary["Contract"]["FlatCooperativeContract"]("cooperative_contract_elec", LVE, flat_prices_elec)

flat_prices_heat = "flat_prices_heat"
cooperative_contract_heat = subclasses_dictionary["Contract"]["FlatCooperativeContract"]("cooperative_contract_heat", LTH, flat_prices_heat)


# ##############################################################################################
# Manual creation of agents

PV_producer = Agent("PV_producer")  # creation of an agent

WT_producer = Agent("WT_producer")  # creation of an agent

DHN_producer = Agent("DHN_producer")  # creation of an agent


# ##############################################################################################
# Manual creation of devices

PV_field = subclasses_dictionary["Device"]["PV"]("PV_field", BAU_elec, PV_producer, aggregator_elec, "ECOS", "ECOS_field", {"surface": 2500})  # creation of a photovoltaic panel field

wind_turbine = subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", cooperative_contract_elec, WT_producer, aggregator_elec, "ECOS", "ECOS")  # creation of a wind turbine

heat_production = subclasses_dictionary["Device"]["GenericProducer"]("heat_production", cooperative_contract_heat, DHN_producer, aggregator_heat, "ECOS", "ECOS")  # creation of a heat production unit


# ##############################################################################################
# Automated generation of complete agents (i.e with devices and contracts)

# BAU contracts
world.agent_generation(165, "cases/TutorialAndExamples/agent_templates/AgentGitHub_1_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})
world.agent_generation(330, "cases/TutorialAndExamples/agent_templates/AgentGitHub_2_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})
world.agent_generation(165, "cases/TutorialAndExamples/agent_templates/AgentGitHub_5_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})

# DLC contracts
world.agent_generation(200, "cases/TutorialAndExamples/agent_templates/AgentGitHub_1_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})
world.agent_generation(400, "cases/TutorialAndExamples/agent_templates/AgentGitHub_2_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})
world.agent_generation(200, "cases/TutorialAndExamples/agent_templates/AgentGitHub_5_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})

# Curtailment contracts
world.agent_generation(135, "cases/TutorialAndExamples/agent_templates/AgentGitHub_1_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})
world.agent_generation(270, "cases/TutorialAndExamples/agent_templates/AgentGitHub_2_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})
world.agent_generation(135, "cases/TutorialAndExamples/agent_templates/AgentGitHub_5_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "LTH": flat_prices_heat})


# ##############################################################################################
# Creation of daemons

# Price Managers
# this daemons fix a price for a given nature of energy
price_manager_elec_flat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]({"nature": LVE.name, "buying_price": 0.15, "selling_price": 0.11, "identifier": flat_prices_elec})  # sets prices for TOU rate
price_manager_elec_TOU = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]({"nature": LVE.name, "buying_price": [0.17, 0.12], "selling_price": [0.11, 0.11], "hours": [[6, 12], [14, 23]], "identifier": TOU_prices})  # sets prices for TOU rate
price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]({"nature": LTH.name, "buying_price": 0.1, "selling_price": 0.08, "identifier": flat_prices_heat})  # sets prices for flat rate

price_elec_grid = subclasses_dictionary["Daemon"]["GridPricesDaemon"]({"nature": LVE.name, "grid_buying_price": 0.2, "grid_selling_price": 0.05})  # sets prices for the system operator
price_heat_grid = subclasses_dictionary["Daemon"]["GridPricesDaemon"]({"nature": LTH.name, "grid_buying_price": 0.10, "grid_selling_price": 0.08})  # sets prices for the system operator

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterDaemon"]({"location": "Pau"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["Daemon"]["WindDaemon"]({"location": "Pau"})


# ##############################################################################################
# Creation of dataloggers

# datalogger used to get back producer outputs
producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")

producer_datalogger.add(f"{PV_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{DHN_producer.name}.LTH.energy_erased")
producer_datalogger.add(f"{WT_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{PV_producer.name}.LVE.energy_sold")
producer_datalogger.add(f"{DHN_producer.name}.LTH.energy_sold")
producer_datalogger.add(f"{WT_producer.name}.LVE.energy_sold")

# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  cluster
nature_balances = subclasses_dictionary["Datalogger"]["NatureBalanceDatalogger"]()
aggregator_balances = subclasses_dictionary["Datalogger"]["AggregatorBalanceDatalogger"]()


# ##############################################################################################
# here we have the possibility to save the world to use it later
# world.save()  # saving the world for a later use


# ##############################################################################################
# Simulation start
world.start()

