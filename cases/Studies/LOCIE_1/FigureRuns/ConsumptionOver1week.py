
from datetime import datetime
from os import chdir, listdir

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.GraphAndTex import GraphOptions

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
name_world = "ECOS_collab_2020"
world = World(name_world)  # creation

# ##############################################################################################
# Definition of the path to the files
pathExport = "cases/Studies/LOCIE_1/FigureRuns/Results/ConsumptionOver1week"   # directory where results are written
world.set_directory(pathExport)  # registration

# ##############################################################################################
# Definition of the random seed to be used
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("tournesol")

# ##############################################################################################
# Time Manager
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2019, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24 * 7)  # number of time steps simulated

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

price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.5, 0.5], "selling_price": [0.5, 0.5], "on-peak_hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate

price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.5, "selling_price": 0.5})  # sets prices for the system operator

price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price": 0.5, "selling_price": 0})  # price manager for the local electrical grid regarding the devices

price_managing_daemon_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_grid", {"nature": LVE.name, "buying_price": 0.2, "selling_price": 0.1})  # price manager for the local electrical grid

# limit prices
subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator

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
supervisor_elec = subclasses_dictionary["Strategy"][f"AlwaysSatisfied"]()

# the DHN strategy
supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

# the national grid strategy
grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

# ##############################################################################################
# Agents
PV_producer = Agent("PV_producer")  # the owner of the Photovoltaics panels

solar_thermal_producer = Agent("solar_thermal_producer")  # the owner of the solar thermal collectors

national_grid = Agent("national_grid")

local_electrical_grid_manager = Agent("local_electrical_grid_producer")  # the owner of the Photovoltaics panels

DHN_manager = Agent("DHN_producer")  # the owner of the district heating network

# ##############################################################################################
# Contracts
contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_daemon_grid)

contract_DHN = subclasses_dictionary["Contract"]["CooperativeContract"]("DHN_grid", LVE, price_managing_daemon_DHN)

contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_managing_elec)

contract_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("BAU_heat", LTH, price_managing_heat)

# ##############################################################################################
# Aggregators
# and then we create a third who represents the grid
aggregator_name = "Enedis"
aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

# here we create a second one put under the orders of the first
aggregator_name = "general_aggregator"
aggregator_elec = Aggregator(aggregator_name, LVE, supervisor_elec, local_electrical_grid_manager, aggregator_grid, contract_grid)  # creation of a aggregator

# here we create another aggregator dedicated to heat
aggregator_name = "Local_DHN"
aggregator_heat = Aggregator(aggregator_name, LTH, supervisor_heat, DHN_manager, aggregator_elec, contract_DHN, 3.6, 3800)  # creation of a aggregator

# ##############################################################################################
# Devices


subclasses_dictionary["Device"]["Photovoltaics"]("PV_field", contract_elec, PV_producer, aggregator_elec, {"device": "standard_field"}, {"panels": 1, "irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})  # creation of a photovoltaic panel field

subclasses_dictionary["Device"]["SolarThermalCollector"]("solar_thermal_collector_field", contract_heat, solar_thermal_producer, aggregator_heat, {"device": "standard_field"}, {"panels": 1, "irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})  # creation of a solar thermal collector

# repartition of contracts according to the chosen proportion
BAU = 500

# BAU contracts
world.agent_generation(BAU, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_1_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation(BAU * 2, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_2_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation(BAU, "cases/Studies/LOCIE_1/AgentTemplates/Agent_5_p_BAU_no_PV.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# ##############################################################################################
# Dataloggers
# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  cluster

graph_options = GraphOptions("Test", "LaTeX", "multiple_series")


def get_quantity(name):
    return world.catalog.get(name)["quantity"]


# global consumption
datalogger_global_consumption = Datalogger("global_consumption", "GlobalConsumption", graph_options=graph_options, graph_labels={"xlabel": "time (\\textit{h})", "ylabel": "consumption (\\textit{kWh})"})

datalogger_global_consumption.add("simulation_time", graph_status="X")
datalogger_global_consumption.add("LVE.energy_consumed", graph_legend="electricity consumption")
datalogger_global_consumption.add("LTH.energy_consumed", graph_legend="heat consumption")

# background consumption
datalogger_background_consumption = Datalogger("background_consumption", "BackgroundConsumption",
                                               graph_options=graph_options,
                                               graph_labels={"xlabel": "time (\\textit{h})",
                                                             "ylabel": "consumption (\\textit{kWh})"})

datalogger_background_consumption.add("simulation_time", graph_status="X")
datalogger_background_consumption.add("1_people_BAU_0_Background_0.LVE.energy_accorded", function=get_quantity, graph_legend="apartment 1")
datalogger_background_consumption.add("2_people_BAU_0_Background_0.LVE.energy_accorded", function=get_quantity, graph_legend="apartment 2")
datalogger_background_consumption.add("5_people_BAU_0_Background_0.LVE.energy_accorded", function=get_quantity, graph_legend="house 5")


# ##############################################################################################
# Simulation
# ##############################################################################################
world.start()




