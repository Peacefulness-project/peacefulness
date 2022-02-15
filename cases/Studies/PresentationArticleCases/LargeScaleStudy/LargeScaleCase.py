# This script is here to help not loose yourself when creating a case.

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
from src.tools.GraphAndTex import GraphOptions

from src.tools.SubclassesDictionary import get_subclasses

from time import process_time


# ##############################################################################################
# Minimum
# the following objects are necessary for the simulation to be performed
# you need exactly one object of each type
# ##############################################################################################

# ##############################################################################################
# Rerooting
# chdir("../../../../")  # here, you have to put the path to the root of project (the main directory)


# ##############################################################################################
# Importation of subclasses
# all the subclasses are imported in the following dictionary
subclasses_dictionary = get_subclasses()

# ##############################################################################################
# Creation of the world
# a world contains all the other elements of the model
# a world needs just a name
name_world = "your_name"
world = World(name_world)  # creation

# ##############################################################################################
# Definition of the path to the files
world.set_directory("cases/Studies/PresentationArticleCases/Results/LargeScaleCase/")  # here, you have to put the path to your results directory

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
               24 * 365)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Creation of nature
LVE = load_low_voltage_electricity()

LPG = load_low_pressure_gas()


# ##############################################################################################
# Creation of daemons

# Price Managers
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec", {"nature": LVE.name, "buying_price": 0.15, "selling_price": 0.10})  # sets prices for flat rate

price_manager_gas = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_heat", {"nature": LPG.name, "buying_price": 0.15, "selling_price": 0.10})  # sets prices for flat rate

# Limit Prices
limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.1})  # sets prices for the system operator

limit_price_gas = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LPG.name, "limit_buying_price": 0.2, "limit_selling_price": 0.1})  # sets prices for the system operator

# Indoor temperature
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Marseille_averaged"})

# Water temperature
cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

# Irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Marseille"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Marseille"})


# ##############################################################################################
# Creation of strategies
strategy_grid = subclasses_dictionary["Strategy"]["Grid"]()

strategy_light_autarky = subclasses_dictionary["Strategy"]["LightAutarkyEmergency"]()


# ##############################################################################################
# Manual creation of agents

aggregator_owner = Agent("aggregator_owner")

# producers
WT_producer = Agent("WT_producer")

PV_producer = Agent("PV_producer")

gas_producer = Agent("gas_producer")


# ##############################################################################################
# Manual creation of contracts

# aggregators
local_electrical_grid_contract = subclasses_dictionary["Contract"]["EgoistContract"]("local_electrical_grid_contract", LVE, price_manager_elec)

local_gas_grid_contract = subclasses_dictionary["Contract"]["EgoistContract"]("local_gas_grid_contract", LPG, price_manager_gas)

# producers
cooperative_elec_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_elec_contract", LVE, price_manager_elec)

egoist_elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("egoist_contract_elec", LVE, price_manager_elec)

cooperative_gas_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_gas_contract", LPG, price_manager_gas)


# ##############################################################################################
# Creation of aggregators
national_grid = Aggregator("national_grid", LVE, strategy_grid, aggregator_owner)

local_electrical_grid = Aggregator("local_electrical_grid", LVE, strategy_light_autarky, aggregator_owner, national_grid, local_electrical_grid_contract)

local_gas_grid = Aggregator("local_gas_grid", LPG, strategy_light_autarky, aggregator_owner, local_electrical_grid, local_gas_grid_contract)


# ##############################################################################################
# Manual creation of devices
wind_turbine = subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", egoist_elec_contract, WT_producer, local_electrical_grid, {"device": "standard"}, {"wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine

heat_production = subclasses_dictionary["Device"]["BiomassGasPlant"]("methanizer", cooperative_gas_contract, gas_producer, local_gas_grid, {"device": "heat"}, {"max_power": 700})  # creation of a heat production unit

subclasses_dictionary["Device"]["PhotovoltaicsAdvanced"]("PV_advanced_field", egoist_elec_contract, PV_producer, local_electrical_grid, {"device": "standard_field"}, {"panels": 2000, "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "irradiation_daemon": irradiation_daemon.name})  # creation of a photovoltaic panel field


# ##############################################################################################
# Automated generation of complete agents (i.e with devices and contracts)

# Performance measurement
CPU_time_generation_of_device = process_time()

# Egoist contracts
world.agent_generation("", 250, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_1_BAU_DHN.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_1_DLC_DHN.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 250, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_1_curtailment_DHN.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# Cooperative contracts
world.agent_generation("", 150, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_BAU_DHN.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 300, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_DLC_DHN.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 150, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_curtailment_DHN.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# Curtailment contracts
world.agent_generation("", 100, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_BAU.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 200, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_curtailment.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 100, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_DLC.json", [local_electrical_grid, local_gas_grid], {"LVE": price_manager_elec, "LPG": price_manager_gas}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# CPU time measurement
CPU_time_generation_of_device = process_time() - CPU_time_generation_of_device  # time taken by the initialization
filename = world._catalog.get("path") + "/outputs/CPU_time.txt"  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the device generation phase: {CPU_time_generation_of_device}\n")
file.close()

# ##############################################################################################
# Creation of dataloggers
graph_options = GraphOptions("graph_options_1", "LaTeX", "single_series")


subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period="month")
subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period="global")
subclasses_dictionary["Datalogger"]["WeightedSelfSufficiencyDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="month")
subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("WindTurbine", period="month")
subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("DummyProducer", period="month")
subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("PhotovoltaicsAdvanced", period="month")

subclasses_dictionary["Datalogger"]["PeakToAverageDatalogger"]()

subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="month")
subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="global")


# ##############################################################################################
# Simulation start

# Performance measurement
CPU_time = process_time()

world.start()

# CPU time measurement
CPU_time = process_time() - CPU_time  # time taken by the initialization
filename = world._catalog.get("path") + "/outputs/CPU_time.txt"  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the calculation phase: {CPU_time}\n")
file.close()


