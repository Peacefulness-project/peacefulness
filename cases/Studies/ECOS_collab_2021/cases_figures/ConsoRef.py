
from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger
from src.tools.GraphAndTex import GraphOptions

from os import chdir
chdir("../../../../")

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


# ##############################################################################################
# Settings
# ##############################################################################################

# ##############################################################################################
# Creation of the world
# a world <=> a case, it contains all the model
# a world needs just a name
name_world = "ECOS_collab_2021"
world = World(name_world)  # creation

# ##############################################################################################
# Definition of the path to the files
pathExport = "cases/Studies/ECOS_collab_2021/Results/Figures/ConsoRef"  # directory where results are written
world.set_directory(pathExport)  # registration

# ##############################################################################################
# Definition of the random seed to be used
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("tournesol")

# ##############################################################################################
# Time Manager
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime.now()  # a start date in the datetime format
start_date = start_date.replace(year=2019, month=2, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24 * 8)  # number of time steps simulated

# ##############################################################################################
# Model creation
# ##############################################################################################

# ##############################################################################################
# Natures
# low voltage electricity
LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()

# ##############################################################################################
# Daemons
# Price Managers
# these daemons fix a price for a given nature of energy

# pricing
price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec_HP", {"nature": LVE.name, "buying_price": 0.13, "selling_price": 0})  # sets prices for TOU rate

price_managing_BAU = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("BAU_prices_heat", {"nature": LTH.name, "buying_price": 0.15, "selling_price": 1})  # sets prices for the system operator
price_managing_DLC = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("BAU_prices_DLC", {"nature": LTH.name, "buying_price": 0.14/0.9, "selling_price": 0.9})  # sets prices for the system operator
price_managing_curtailment = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("BAU_prices_curtailment", {"nature": LTH.name, "buying_price": 0.13/0.8, "selling_price": 0.8})  # sets prices for the system operator

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator
subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator

# Outdoor temperature
# this daemon is responsible for the value of outdoor temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# ##############################################################################################
# Strategies

# the DHN strategy
supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorAutarkyHeatEmergency"]()

# the national grid strategy
grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

# ##############################################################################################
# Agents
national_grid = Agent("national_grid")

DHN_manager = Agent("DHN_manager")  # the owner of the old district heating network

solar_thermal_producer = Agent("solar_thermal_producer")  # the producer of solar thermal collectors

biomass_plant_producer = Agent("biomass_plant_producer")  # the producer of the biomass plant

# ##############################################################################################
# Contracts
contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_elec)

contract_solar = subclasses_dictionary["Contract"]["EgoistContract"]("solar_contract", LTH, price_managing_BAU)

contract_biomass = subclasses_dictionary["Contract"]["CooperativeContract"]("biomass_contract", LTH, price_managing_DLC)

# ##############################################################################################
# Aggregators

# the grid
aggregator_name = "Enedis"
aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

# old aggregator dedicated to heat
aggregator_name = "Local_DHN"
aggregator_heat = Aggregator(aggregator_name, LTH, supervisor_heat, DHN_manager, aggregator_grid, contract_grid, 1.86*0.9, 2420)  # creation of a aggregator


# ##############################################################################################
# Devices

# old DHN
world.agent_generation("old_DHN_1", 500, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_demand.json", [aggregator_grid, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("old_DHN_2", 1000, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_demand.json", [aggregator_grid, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("old_DHN_5", 500, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_5_demand.json", [aggregator_grid, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# new DHN
world.agent_generation("new_DHN_1", 150, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_demand.json", [aggregator_grid, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("new_DHN_2", 300, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_demand.json", [aggregator_grid, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("new_DHN_5", 150, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_5_demand.json", [aggregator_grid, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_BAU}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})


# ##############################################################################################
# Dataloggers
# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  cluster

graph_options = GraphOptions("graph_options_1", "LaTeX", "single_series")

subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](graph_options=graph_options)


# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()


