
from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat, load_low_pressure_gas
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from os import chdir

from src.tools.SubclassesDictionary import get_subclasses


# ##############################################################################################
# Settings
# ##############################################################################################

# ##############################################################################################
# Rerooting
chdir("../../../")  # set the relative path to the project root
subclasses_dictionary = get_subclasses()


# ##############################################################################################
# Creation of the world
# a world <=> a case, it contains all the model
# a world needs just a name
name_world = "ECOS_CHP_2021"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
pathExport = "cases/Studies/ECOS_CHP_2021/Results/Demand"  # directory where results are written
world.set_directory(pathExport)  # registration


# ##############################################################################################
# Definition of the random seed to be used
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("sunflower")


# ##############################################################################################
# Time Manager
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime.now()  # a start date in the datetime format
start_date = start_date.replace(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24 * 365)  # number of time steps simulated


# ##############################################################################################
# Model creation
# ##############################################################################################

# ##############################################################################################
# Natures
# low voltage electricity
LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()

# low pressure gas
LPG = load_low_pressure_gas()


# ##############################################################################################
# Daemons
# Price Managers
# these daemons fix a price for a given nature of energy

price_managing_gas = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_gas", {"nature": LPG.name, "buying_price": 0, "selling_price": 0})  # price manager for the local electrical grid
price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_heat", {"nature": LTH.name, "buying_price": 0, "selling_price": 0})  # price manager for the local electrical grid
price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_CHP_elec", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # price manager for the local electrical grid

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator
subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator
subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LPG.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator

# Outdoor temperature
# this daemon is responsible for the value of outdoor temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})


# ##############################################################################################
# Strategies

# the local electrical grid strategy
supervisor_elec = subclasses_dictionary["Strategy"][f"LightAutarkyEmergency"]()

# the DHN strategy
supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

# the national grid strategy
grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Agents

CHP_producer = Agent("CHP_producer")  # the owner of the solar thermal collectors

national_grid = Agent("national_grid")

local_electrical_grid_manager = Agent("local_electrical_grid_producer")  # the owner of the Photovoltaics panels

DHN_manager = Agent("DHN_producer")  # the owner of the district heating network


# ##############################################################################################
# Contracts

# contracts for aggregators
contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid_contract", LVE, price_managing_elec)

contract_DHN = subclasses_dictionary["Contract"]["EgoistContract"]("DHN_grid_contract", LTH, price_managing_elec)

# contracts for the CHP unit
contract_CHP_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("CHP_heat_contract", LTH, price_managing_heat)

contract_CHP_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("CHP_elec_contract", LVE, price_managing_elec)

contract_CHP_gas = subclasses_dictionary["Contract"]["EgoistContract"]("CHP_gas_contract", LPG, price_managing_gas)


# ##############################################################################################
# Aggregators
# national electrical grid
aggregator_name = "elec_grid"
aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

# gas grid
aggregator_name = "gas_grid"
aggregator_gas = Aggregator(aggregator_name, LPG, grid_supervisor, national_grid)

# local electrical aggregator
aggregator_name = "general_aggregator"
aggregator_elec = Aggregator(aggregator_name, LVE, supervisor_elec, local_electrical_grid_manager, aggregator_grid, contract_grid)  # creation of a aggregator

# DHN aggregator
aggregator_name = "Local_DHN"
aggregator_heat = Aggregator(aggregator_name, LTH, supervisor_heat, DHN_manager, aggregator_elec, contract_DHN, 3.5)  # creation of a aggregator


# ##############################################################################################
# Devices
BAU = 400
DLC = 0
curtailment = 0

subclasses_dictionary["Device"]["CombinedHeatAndPower"]("CHP_plant", [contract_CHP_elec, contract_CHP_gas, contract_CHP_heat], CHP_producer, aggregator_gas, [aggregator_heat, aggregator_elec], {"device": "standard"}, {"max_power": 6350*10/3})

# BAU contracts
world.agent_generation("", BAU * 2, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_1_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", BAU * 3, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_2_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", BAU, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_5_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# DLC contracts
world.agent_generation("", DLC * 2, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_1_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", DLC * 3, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_2_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", DLC, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_5_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# Curtailment contracts
world.agent_generation("", curtailment * 2, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_1_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", curtailment * 3, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_2_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", curtailment, "cases/Studies/ECOS_CHP_2021/AgentTemplates/AgentECOS_5_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})


# ##############################################################################################
# Dataloggers
# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  cluster
subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")
subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="global")
subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["WeightedSelfSufficiencyDatalogger"](period="global")
subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"]()

CHP_datalogger = Datalogger("CHP_datalogger", "CHP")
CHP_datalogger.add("CHP_producer.LVE.energy_sold")
CHP_datalogger.add("CHP_producer.LTH.energy_sold")
CHP_datalogger.add("CHP_producer.LPG.energy_bought")

CHP_datalogger = Datalogger("CHP_datalogger_global", "CHP_global", period="global")
CHP_datalogger.add("CHP_producer.LVE.energy_sold")
CHP_datalogger.add("CHP_producer.LTH.energy_sold")
CHP_datalogger.add("CHP_producer.LPG.energy_bought")

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()


