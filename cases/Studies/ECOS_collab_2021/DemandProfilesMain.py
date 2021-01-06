
from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

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
pathExport = "cases/Studies/ECOS_collab_2021/Results/DemandProfiles"  # directory where results are written
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

# ##############################################################################################
# Daemons
# Price Managers
# these daemons fix a price for a given nature of energy
price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.4375, 0.3125], "selling_price": [0.245, 0.245], "hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.5125, "selling_price": 0.407})  # sets prices for the system operator

price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price": 0.407, "selling_price": 0})  # price manager for the local electrical grid
subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.407, "limit_selling_price": 0})  # sets prices for the system operator

price_managing_daemon_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_grid", {"nature": LVE.name, "buying_price": 0.2, "selling_price": 0.1})  # price manager for the local electrical grid
subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.1})  # sets prices for the system operator

# Outdoor temperature
# this daemon is responsible for the value of outdoor temperature in the catalog
subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "Pau"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# ##############################################################################################
# Strategies

# the local electrical grid strategy
supervisor_elec = subclasses_dictionary["Strategy"][f"AlwaysSatisfied"]()

# the DHN strategy
supervisor_heat = subclasses_dictionary["Strategy"][f"AlwaysSatisfied"]()

# the national grid strategy
grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

# ##############################################################################################
# Agents

national_grid = Agent("national_grid")

local_electrical_grid_manager = Agent("local_electrical_grid_manager")  # the owner of the Photovoltaics panels

old_DHN_manager = Agent("old_DHN_manager")  # the owner of the district heating network

new_DHN_manager = Agent("new_DHN_manager")  # the owner of the district heating network

# ##############################################################################################
# Contracts
contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_daemon_grid)

contract_DHN = subclasses_dictionary["Contract"]["EgoistContract"]("DHN_grid", LTH, price_managing_daemon_DHN)

contract_heat = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_managing_heat)

# ##############################################################################################
# Aggregators

# the grid
aggregator_name = "Enedis"
aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

# local electrical grid
aggregator_name = "electrical_aggregator"
aggregator_elec = Aggregator(aggregator_name, LVE, supervisor_elec, local_electrical_grid_manager, aggregator_grid, contract_grid)  # creation of a aggregator

# old aggregator dedicated to heat
aggregator_name = "Local_DHN_old"
aggregator_heat_old = Aggregator(aggregator_name, LTH, supervisor_heat, old_DHN_manager, aggregator_elec, contract_DHN, 3.6)  # creation of a aggregator

# new aggregator dedicated to heat
aggregator_name = "Local_DHN_new"
aggregator_heat_new = Aggregator(aggregator_name, LTH, supervisor_heat, new_DHN_manager, aggregator_heat_old, contract_DHN, 1)  # creation of a aggregator


# ##############################################################################################
# Devices

# old DHN
world.agent_generation(, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_demand.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat})
world.agent_generation(, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_demand.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat})
world.agent_generation(, "cases/Studies/ECOS_collab_2021/AgentTemplates/Agent_5_demand.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat})

# new DHN
world.agent_generation(, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_demand.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat})
world.agent_generation(, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_demand.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat})
world.agent_generation(, "cases/Studies/ECOS_collab_2021/AgentTemplates/Agent_5_demand.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat})

# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()


