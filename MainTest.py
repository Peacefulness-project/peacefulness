# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================
#
#                                               PEACEFULNESS
#
#           Platform for transverse evaluation of control strategies for multi-energy smart grids
#
#
#
# Coordinators: Dr E. Franquet, Dr S. Gibout (erwin.franquet@univ-pau.fr, stephane.gibout@univ-pau.fr)
# Contributors (alphabetical order): Dr E. Franquet, Dr S. Gibout, T. Gronier
# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================
# ==================================================================================================================


# ##############################################################################################
# Importations
from datetime import datetime

from time import process_time

from src.tools.Utilities import adapt_path

from src.common.World import World

from src.common.Nature import Nature
from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses

from src.tools.GraphAndTex import GraphOptions


# ##############################################################################################
# Performance measurement
CPU_time = process_time()

# ##############################################################################################
# Settings
# the following objects are necessary for the simulation to be performed
# you need exactly one object of each type
# ##############################################################################################


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
pathExport = "./Results"
world.set_directory(pathExport)


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("tournesol")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24*365)  # number of time steps simulated


# ##############################################################################################
# Optional
world.complete_message("CO2", 0)


# ##############################################################################################
# Model
# the following objects are the one describing the case studied
# you need at least one local grid and one agent to create a device
# no matter the type, you can create as much objects as you want
# ##############################################################################################

# ##############################################################################################
# Nature list
# this object represents a nature of energy present in world

# low voltage electricity
LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()


# ##############################################################################################
# Daemon
# this object updates values of the catalog not taken in charge by anyone else
# TOU_prices = "TOU_prices"
# flat_prices_elec = "flat_prices_elec"
# flat_prices_heat = "flat_prices_heat"
# owned_by_aggregator = "owned_by_aggregator"

# Price Managers
# these daemons fix a price for a given nature of energy
price_manager_owned_by_the_aggregator = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("owned_by_aggregator_daemon", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # as these devices are owned by the aggregator, energy is free
price_manager_RTP_elec = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("RTP_prices_elec", {"location": "France"})  # sets prices for flat rate
price_manager_TOU_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.1, 0.2], "selling_price": [0.1, 0.2], "on-peak_hours": [[12, 24]]})  # sets prices for TOU rate
price_manager_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_grid", {"nature": LVE.name, "buying_price": 0.5, "selling_price": 0.1})  # sets prices for flat rate
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_elec", {"nature": LVE.name, "buying_price": 0.1, "selling_price": 0.1})  # sets prices for flat rate


price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.15, "selling_price": 0.1})  # sets prices for flat rate
price_manager_RTP_heat = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("RTP_prices_heat", {"location": "France"})  # sets prices for flat rate
price_manager_TOU_heat = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_heat", {"nature": LTH.name, "buying_price": [0.1, 0.2], "selling_price": [0.1, 0.2], "on-peak_hours": [[12, 24]]})  # sets prices for TOU rate


limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator
limit_price_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.30, "limit_selling_price": 0.00})  # sets prices for the system operator


# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Zaragoza"})

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

# ground temperature
# this daemon is responsible for the value of the ground temperature in the catalog
ground_temperature_daemon = subclasses_dictionary["Daemon"]["GroundTemperatureDaemon"]({"location": "France"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Pau"})

# Water flow
# this daemon is responsible for updating the value of the flow of water for an electric dam
water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "GavedePau_Pau"})

# Sun position daemon
# this daemon is responsible for updating the value of position of the sun in the sky
sun_position_daemon = subclasses_dictionary["Daemon"]["SunPositionDaemon"]({"location": "Pau"})

# Forecast
# this daemon is supposed to create predictions about future consumption and demands
forecast_daemon = subclasses_dictionary["Daemon"]["DummyForecasterDaemon"]("dummy_forecaster")

# ##############################################################################################
# Strategy
# this object defines a strategy of supervision through 3 steps: local distribution, formulation of its needs, remote distribution

# the BAU strategy
strategy_elec = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# the heat strategy
# strategy_heat = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# the strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Agent
# this object represents the owner of devices
# all devices need an agent
PV_producer = Agent("PV_producer")  # creation of an agent

WT_producer = Agent("WT_producer")  # creation of an agent

dam_producer = Agent("dam_producer")  # creation of an agent

DHN_producer = Agent("DHN_producer")  # creation of an agent

heat_pump_owner = Agent("heat_pump_owner")

aggregator_manager = Agent("aggregator_manager")

CO2_producer = Agent("CO2_producer")

dummy_agent = Agent("dummy")

storer_owner = Agent("storer_owner")

# ##############################################################################################
# Contract
# this object has 3 roles: managing the dissatisfaction, managing the billing and defining the operations allowed to the strategy
# contracts have to be defined for each nature for each agent BUT are not linked initially to a nature

# producers
BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_grid)

BAU_heat = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_manager_heat)

cooperative_contract_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_heat", LTH, price_manager_heat)

cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_RTP_elec)

contract_owned_by_aggregator = subclasses_dictionary["Contract"]["CooperativeContract"]("owned_by_aggregator_contract", LVE, price_manager_owned_by_the_aggregator)

contract_storage_elec = subclasses_dictionary["Contract"]["ThresholdPricesContract"]("contract_storage_elec", LVE, price_manager_TOU_elec, {"buying_threshold": 0.1, "selling_threshold": 0.2})
contract_storage_heat = subclasses_dictionary["Contract"]["ThresholdPricesContract"]("contract_storage_heat", LTH, price_manager_TOU_heat, {"buying_threshold": 0.1, "selling_threshold": 0.21})

contract_test = subclasses_dictionary["Contract"]["CurtailmentRampContract"]("contract_ramp", LVE, price_manager_TOU_elec, {"bonus": 0.005, "depreciation_time": 24*30, "depreciation_residual": 0.01})

# ##############################################################################################
# Aggregator
# this object is a collection of devices wanting to isolate themselves as much as they can
# aggregators need 2 arguments: a name and a nature of energy
# there is also a third argument to precise if the aggregator is considered as an infinite grid

# and then we create a third who represents the grid
aggregator_name = "Enedis"
aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, aggregator_manager)

# here we create a second one put under the orders of the first
aggregator_name = "general_aggregator"
aggregator_elec = Aggregator(aggregator_name, LVE, strategy_elec, aggregator_manager, aggregator_grid, BAU_elec, forecaster=forecast_daemon)  # creation of a aggregator

# here we create another aggregator dedicated to heat
aggregator_name = "Local_DHN"
aggregator_heat = Aggregator(aggregator_name, LTH, strategy_elec, aggregator_manager, aggregator_elec, BAU_elec, 1, {"buying": 10000, "selling": 0})  # creation of a aggregator


# ##############################################################################################
# Device
# these objects regroup production, consumption, storage and transformation devices
# they at least need a name and a nature
# some devices are pre-defined (such as Photovoltaics) but user can add some by creating new classes in lib


# subclasses_dictionary["Device"]["LatentHeatStorage"]("heat_storage_3", contract_storage_heat, storer_owner, aggregator_heat, {"device": "industrial_water_tank"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name})
# subclasses_dictionary["Device"]["Background"]("background", contract_test, dummy_agent, aggregator_elec, {"user": "ECOS", "device": "ECOS_5"})
# subclasses_dictionary["Device"]["DummyProducer"]("production", contract_owned_by_aggregator, heat_pump_owner, aggregator_elec, {"device": "elec"}, {"max_power": 1})
subclasses_dictionary["Device"]["PhotovoltaicsAdvanced"]("PV_field", cooperative_contract_elec, PV_producer, aggregator_elec, {"device": "standard_field"}, {"panels": 20000, "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "irradiation_daemon": irradiation_daemon.name})  # creation of a photovoltaic panel field
subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", cooperative_contract_elec, WT_producer, aggregator_elec, {"device": "ECOS_high"}, {"wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine
subclasses_dictionary["Device"]["ElectricDam"]("electric_dam", cooperative_contract_elec, dam_producer, aggregator_elec, {"device": "Pelton"}, {"height": 5, "max_power": 3000, "water_flow_daemon": water_flow_daemon.name})  # creation of an electric dam

# Performance measurement
CPU_time_generation_of_device = process_time()
# the following method create "n" agents with a predefined set of devices based on a JSON file
# world.agent_generation("single", 20, "lib/AgentTemplates/EgoistSingle.json", aggregator_elec, {"LVE": price_manager_TOU_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
# world.agent_generation("family", 20, "lib/AgentTemplates/EgoistFamily.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_TOU_elec, "LTH": price_manager_heat}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
# world.agent_generation("dummy", 1, "lib/AgentTemplates/DummyAgent.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_RTP_elec, "LTH": price_manager_heat}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "wind_speed_daemon": wind_daemon, "water_flow_daemon": water_flow_daemon, "sun_position_daemon": sun_position_daemon})

# CPU time measurement
CPU_time_generation_of_device = process_time() - CPU_time_generation_of_device  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the device generation phase: {CPU_time_generation_of_device}\n")
file.close()


# ##############################################################################################
# Datalogger
# this object is in charge of exporting data into files at a given iteration frequency
# world.catalog.print_debug()  # displays the content of the catalog

export_graph_options_1 = GraphOptions("test_graph_options", "LaTeX")

test_contract_datalogger = Datalogger("test_contract_datalogger", "StorageData", graph_options=export_graph_options_1)
test_contract_datalogger.add("physical_time", graph_status="X")
# test_contract_datalogger.add(f"dummy.LVE.energy_bought")
# test_contract_datalogger.add(f"dummy.LVE.energy_erased")



# producer_datalogger.add(f"{price_manager_TOU_heat.name}.buying_price")
# producer_datalogger.add(f"{price_manager_TOU_heat.name}.selling_price")
# producer_datalogger.add(f"{outdoor_temperature_daemon.location}.current_outdoor_temperature")

# producer_datalogger.add(f"heat_storage_1.LTH.energy_wanted")
# producer_datalogger.add(f"heat_storage_1.LTH.energy_accorded")
# producer_datalogger.add(f"heat_storage_1.energy_stored")
#
# producer_datalogger.add(f"heat_storage_2.LTH.energy_wanted")
# producer_datalogger.add(f"heat_storage_2.LTH.energy_accorded")
# producer_datalogger.add(f"heat_storage_2.energy_stored")
#
# producer_datalogger.add(f"heat_storage_3.LTH.energy_wanted")
# producer_datalogger.add(f"heat_storage_3.LTH.energy_accorded")
# producer_datalogger.add(f"heat_storage_3.energy_stored")
#
# producer_datalogger.add(f"{price_manager_TOU_elec.name}.buying_price")
# producer_datalogger.add(f"{price_manager_TOU_elec.name}.selling_price")
#
# producer_datalogger.add(f"battery.LVE.energy_wanted")
# producer_datalogger.add(f"battery.LVE.energy_accorded")
# producer_datalogger.add(f"battery.energy_stored")


# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  aggregator
# subclasses_dictionary["Datalogger"]["AgentBalancesDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["AgentBalancesDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["AggregatorProfitsDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["AggregatorProfitsDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["PeakToAverageDatalogger"]()
# subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period="month")
# subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["WeightedSelfSufficiencyDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["WeightedSelfSufficiencyDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["CurtailmentDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["CurtailmentDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["WeightedCurtailmentDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["WeightedCurtailmentDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period="global")

# # datalogger used to get back producer outputs
# export_graph_options_1 = GraphOptions("test_graph_options", "LaTeX")
#
producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances", period="global")
#
producer_datalogger.add(f"{PV_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{PV_producer.name}.LVE.energy_sold")
producer_datalogger.add(f"{PV_producer.name}.LVE.energy_bought")

producer_datalogger.add(f"{dam_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{dam_producer.name}.LVE.energy_sold")
producer_datalogger.add(f"{dam_producer.name}.LVE.energy_bought")

producer_datalogger.add(f"{WT_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{WT_producer.name}.LVE.energy_sold")
producer_datalogger.add(f"{WT_producer.name}.LVE.energy_bought")
# producer_datalogger.add(f"{DHN_producer.name}.LTH.energy_erased")
# producer_datalogger.add(f"{DHN_producer.name}.LTH.energy_sold")

# producer_datalogger.add(f"{PV_producer.name}.LVE.energy_erased")
# producer_datalogger.add(f"{solar_thermal_collector_producer.name}.LTH.energy_erased")
# producer_datalogger.add(f"{PV_producer.name}.LVE.energy_sold")
# producer_datalogger.add(f"{solar_thermal_collector_producer.name}.LTH.energy_sold")
#
# producer_datalogger.add(f"{PV_field.name}.exergy_in")
# producer_datalogger.add(f"{solar_thermal_collector_field.name}.exergy_in")
# producer_datalogger.add(f"{PV_field.name}.exergy_out")
# producer_datalogger.add(f"{solar_thermal_collector_field.name}.exergy_out")
# producer_datalogger.add("Pau.reference_temperature")
# producer_datalogger.add("Pau.irradiation_value")
#
# test_datalogger = Datalogger("test_datalogger", "test")
# test_datalogger.add("egoist_single_0.LVE.energy_bought")
# test_datalogger.add("egoist_single_0.LTH.energy_bought")
# test_datalogger.add("egoist_single_0.money_spent")
#
# test_datalogger.add("egoist_family_0.LVE.energy_bought")
# test_datalogger.add("egoist_family_0.LTH.energy_bought")
# test_datalogger.add("egoist_family_0.money_spent")
#
# test_datalogger.add("egoist_single_0_Heating_0.LVE.energy_accorded")
# test_datalogger.add("egoist_single_0_HotWaterTank_0.LVE.energy_accorded")

# subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("Heating")
# subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("Heating", "global")
#
# subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("HotWaterTank")
# subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("HotWaterTank", "global")

# figures
export_graph_options_3 = GraphOptions("toto", ["LaTeX", "matplotlib"], "multiple_series")
# subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("Heating", 24, export_graph_options_3)


# CPU time measurement
CPU_time = process_time() - CPU_time  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the initialization phase: {CPU_time}\n")
file.close()


# ##############################################################################################
# here we have the possibility to save the world to use it later
save_wanted = False

if save_wanted:
    CPU_time = process_time()  # CPU time measurement

    world.save()  # saving the world
    print("plop\n\n\n\n\n")

    path = f"{world.catalog.get('path')}/inputs/save.tar"
    world = World("new_world")  # creation
    world.load(path)

    # CPU time measurement
    CPU_time = process_time() - CPU_time  # time taken by the initialization
    filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
    file = open(filename, "a")  # creation of the file
    file.write(f"time taken by the saving phase: {CPU_time}\n")
    file.close()

# ##############################################################################################
# simulation
CPU_time = process_time()  # CPU time measurement
world.start()


# CPU time measurement
CPU_time = process_time() - CPU_time  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the calculation phase: {CPU_time}\n")
file.close()



