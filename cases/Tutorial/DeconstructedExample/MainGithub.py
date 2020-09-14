# This script is the one deconstructed in the tuto to create a case on the wiki.


# ##############################################################################################
# Importations
from datetime import datetime

from os import chdir, listdir

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
chdir("../../../")


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
pathExport = "cases/Tutorial/DeconstructedExample/Results"
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
# Creation of daemons

# Price Managers
# this daemons fix a price for a given nature of energy
price_manager_elec_flat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_elec", {"nature": LVE.name, "buying_price": 0.15, "selling_price": 0.11})  # sets prices for TOU rate
price_manager_elec_TOU = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.17, 0.12], "selling_price": [0.11, 0.11], "on-peak_hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.1, "selling_price": 0.08})  # sets prices for flat rate

price_manager_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("grid_prices", {"nature": LVE.name, "buying_price": 0.2, "selling_price": 0.05})  # sets prices for TOU rate

# limit prices
# the following daemons fix the maximum and minimum price at which energy can be exchanged
limit_prices_elec_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.05})  # sets limit price accepted
limit_prices_heat_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.10, "limit_selling_price": 0.08})  # sets limit prices accepted

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Pau"})


# ##############################################################################################
# Creation of strategies

# the BAU strategy
strategy_elec = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# the heat strategy
strategy_heat = subclasses_dictionary["Strategy"]["SubaggregatorHeatEmergency"]()

# the strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents

# the first block corresponds to the producers
PV_producer = Agent("PV_producer")  # creation of an agent

WT_producer = Agent("WT_producer")  # creation of an agent

DHN_producer = Agent("DHN_producer")  # creation of an agent

# the second block corresponds to the grid managers (i.e the owners of the aggregators)
grid_manager = Agent("grid_manager")  # creation of an agent

local_electrical_grid = Agent("local_electrical_grid")  # creation of an agent

DHN_manager = Agent("DHN_manager")  # creation of an agent


# ##############################################################################################
# Manual creation of contracts

# producers
BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec_TOU)

cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_elec_flat)  # a contract

cooperative_contract_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_heat", LTH, price_manager_heat)

contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("grid_prices_manager", LVE, price_manager_grid)  # this contract is the one between the local electrical grid and the national one


# ##############################################################################################
# Creation of aggregators

# we create a first aggregator who represents the national electrical grid
aggregator_name = "Enedis"
aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, grid_manager)

# here we create a second one put under the orders of the first
aggregator_name = "general_aggregator"
aggregator_elec = Aggregator(aggregator_name, LVE, strategy_elec, local_electrical_grid, aggregator_grid, contract_grid)  # creation of a aggregator

# here we create another aggregator dedicated to heat, under the order of the local electrical grid
aggregator_name = "Local_DHN"
aggregator_heat = Aggregator(aggregator_name, LTH, strategy_heat, DHN_manager, aggregator_elec, cooperative_contract_elec, 3.6, 2000)  # creation of a aggregator


# ##############################################################################################
# Manual creation of devices

PV_field = subclasses_dictionary["Device"]["Photovoltaics"]("PV_field", BAU_elec, PV_producer, aggregator_elec, {"device": "standard_field"}, {"panels": 1250, "irradiation_daemon": irradiation_daemon})  # creation of a photovoltaic panel field

wind_turbine = subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", cooperative_contract_elec, WT_producer, aggregator_elec, {"device": "standard"}, {"wind_speed_daemon": wind_daemon})  # creation of a wind turbine

heat_production = subclasses_dictionary["Device"]["DummyProducer"]("heat_production", cooperative_contract_heat, DHN_producer, aggregator_heat, {"device": "ECOS"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon})  # creation of a heat production unit


# ##############################################################################################
# Automated generation of complete agents (i.e with devices and contracts)

# BAU contracts
world.agent_generation(165, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_1_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})
world.agent_generation(330, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_2_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})
world.agent_generation(165, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_5_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})

# DLC contracts
world.agent_generation(200, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_1_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})
world.agent_generation(400, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_2_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})
world.agent_generation(200, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_5_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})

# Curtailment contracts
world.agent_generation(135, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_1_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})
world.agent_generation(270, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_2_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})
world.agent_generation(135, "cases/Tutorial/DeconstructedExample/agent_templates/AgentGitHub_5_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_elec_TOU, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon})


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
nature_balances = subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]()
aggregator_balances = subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()


# ##############################################################################################
# here we have the possibility to save the world to use it later
# world.save()  # saving the world for a later use


# ##############################################################################################
# Simulation start
world.start()

