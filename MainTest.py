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
from src.tools.AgentGenerator import agent_generation

from src.common.Strategy import *
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
name_world = "clustering_case_day"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
pathExport = "./Results"
world.set_directory(pathExport)


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("sunflower")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2018, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               8760)  # number of time steps simulated


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
# LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()

# low pressure gas
# LPG = load_low_pressure_gas()


# ##############################################################################################
# Daemon
# this object updates values of the catalog not taken in charge by anyone else
# TOU_prices = "TOU_prices"
# flat_prices_elec = "flat_prices_elec"
# flat_prices_heat = "flat_prices_heat"
# owned_by_aggregator = "owned_by_aggregator"

# Price Managers
# these daemons fix a price for a given nature of energy
# price_manager_owned_by_the_aggregator = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("owned_by_aggregator_daemon", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # as these devices are owned by the aggregator, energy is free
# price_manager_RTP_elec = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("RTP_prices", {"location": "France", "buying_coefficient": 1, "selling_coefficient": 1})  # sets prices for flat rate
# price_manager_TOU_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.1, 0.2], "selling_price": [0.1, 0.2], "on-peak_hours": [[12, 24]]})  # sets prices for TOU rate
# price_manager_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_grid", {"nature": LVE.name, "buying_price": 0.5, "selling_price": 0.1})  # sets prices for flat rate
# price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_elec", {"nature": LVE.name, "buying_price": 0.1, "selling_price": 0.1})  # sets prices for flat rate

price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("heat_price", {"buying_price": 0.5,
                                                                                          "selling_price": 0.2})  # sets prices for TOU rate

# price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.15, "selling_price": 0.1})  # sets prices for flat rate
# price_manager_RTP_heat = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("RTP_prices_heat", {"location": "France", "coefficient": 1})  # sets prices for flat rate
# price_manager_TOU_heat = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_heat", {"nature": LTH.name, "buying_price": [0.1, 0.2], "selling_price": [0.1, 0.2], "on-peak_hours": [[12, 24]]})  # sets prices for TOU rate


# limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator
limit_price_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.8, "limit_selling_price": 0.1})  # sets prices for the system operator
# limit_price_gas = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LPG.name, "limit_buying_price": 0.30, "limit_selling_price": 0.00})  # sets prices for the system operator


# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
# indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
# outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Zaragoza"})

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
# cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

# ground temperature
# this daemon is responsible for the value of the ground temperature in the catalog
# ground_temperature_daemon = subclasses_dictionary["Daemon"]["GroundTemperatureDaemon"]({"location": "France"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
# irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
# wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Pau"})

# Water flow
# this daemon is responsible for updating the value of the flow of water for an electric dam
# water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "GavedePau_Pau"})

# Sun position daemon
# this daemon is responsible for updating the value of position of the sun in the sky
# sun_position_daemon = subclasses_dictionary["Daemon"]["SunPositionDaemon"]({"location": "Pau"})

# ##############################################################################################
# Strategy
# this object defines a strategy of supervision through 3 steps: local distribution, formulation of its needs, remote distribution

# the BAU strategy
# strategy_elec = subclasses_dictionary["Strategy"]["LightAutarkyFullButFew"](get_emergency)

# the heat strategy
strategy_heat = subclasses_dictionary["Strategy"]["WhenProfitablePartialButAll"]()

# the strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Agent
# this object represents the owner of devices
# all devices need an agent
# PV_producer = Agent("PV_producer")  # creation of an agent

# WT_producer = Agent("WT_producer")  # creation of an agent

# producer = Agent("producer")  # creation of an agent

DHN_producer = Agent("DHN_producer")  # creation of an agent

# heat_pump_owner = Agent("heat_pump_owner")

# aggregator_manager = Agent("aggregator_manager")

# CO2_producer = Agent("CO2_producer")

# dummy_agent = Agent("dummy")

# storer_owner = Agent("storer_owner")

# ##############################################################################################
# Contract
# this object has 3 roles: managing the dissatisfaction, managing the billing and defining the operations allowed to the strategy
# contracts have to be defined for each nature for each agent BUT are not linked initially to a nature
heat_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("contract_heat", LTH, price_manager_heat)

heat_contract_curtailment = subclasses_dictionary["Contract"]["CurtailmentContract"]("heat_well", LTH,
                                                                                     price_manager_heat)
heat_contract_BAU = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_manager_heat)

# producers
# BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_grid)
# BAU_gas = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_gas", LPG, price_manager_grid)

# BAU_heat = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_manager_heat)

# cooperative_contract_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_heat", LTH, price_manager_heat)

# cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_RTP_elec)

# cooperative_contract_gas = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_gas", LPG, price_manager_RTP_elec)

# contract_owned_by_aggregator = subclasses_dictionary["Contract"]["CooperativeContract"]("owned_by_aggregator_contract", LVE, price_manager_owned_by_the_aggregator)

# contract_storage_elec = subclasses_dictionary["Contract"]["ThresholdPricesContract"]("contract_storage_elec", LVE, price_manager_TOU_elec, {"buying_threshold": 0.1, "selling_threshold": 0.2})
# contract_storage_heat = subclasses_dictionary["Contract"]["ThresholdPricesContract"]("contract_storage_heat", LTH, price_manager_TOU_heat, {"buying_threshold": 0.1, "selling_threshold": 0.21})

# contract_test = subclasses_dictionary["Contract"]["CurtailmentRampContract"]("contract_ramp", LVE, price_manager_TOU_elec, {"bonus": 0.005, "depreciation_time": 24*30, "depreciation_residual": 0.01})

# ##############################################################################################
# Aggregator
aggregator_name = "peakload_gas_plant"  # external grid
aggregator_grid = Aggregator(aggregator_name, LTH, grid_strategy, DHN_producer)
aggregator_name = "district_heating_microgrid"
aggregator_district = Aggregator(aggregator_name, LTH, strategy_heat, DHN_producer, aggregator_grid, heat_contract,
                                 efficiency=1, capacity={"buying": 1100, "selling": 0})

# this object is a collection of devices wanting to isolate themselves as much as they can
# aggregators need 2 arguments: a name and a nature of energy
# there is also a third argument to precise if the aggregator is considered as an infinite grid

# and then we create a third who represents the grid
# aggregator_name = "Enedis"
# aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, aggregator_manager)

# here we create a second one put under the orders of the first
# aggregator_name = "general_aggregator"
# aggregator_elec = Aggregator(aggregator_name, LVE, strategy_elec, aggregator_manager, aggregator_grid, BAU_elec)  # creation of a aggregator

# here we create another aggregator dedicated to heat
# aggregator_name = "Local_DHN"
# aggregator_heat = Aggregator(aggregator_name, LTH, strategy_elec, aggregator_manager, aggregator_elec, BAU_elec, 1, {"buying": 7894456, "selling": 45612})  # creation of a aggregator

# name = "gas_aggregator"
# aggregator_gas = Aggregator(name, LPG, strategy_elec, aggregator_manager, aggregator_elec, BAU_elec, 1)

# ##############################################################################################
# Device
# these objects regroup production, consumption, storage and transformation devices
# they at least need a name and a nature
# some devices are pre-defined (such as Photovoltaics) but user can add some by creating new classes in lib
heat_sink = subclasses_dictionary["Device"]["Background"]("heat_sink", heat_contract_curtailment, DHN_producer,
                                                          aggregator_district,
                                                          {"user": "artificial_sink", "device": "artificial_sink"},
                                                          filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")

# subclasses_dictionary["Device"]["LatentHeatStorage"]("heat_storage_3", contract_storage_heat, storer_owner, aggregator_heat, {"device": "industrial_water_tank"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name})
# subclasses_dictionary["Device"]["BiomassGasPlant"]("biomass_plant", cooperative_contract_gas, producer, aggregator_gas, {"device": "MSW_Rao"}, {"max_power": 1000, "waste_recharge": 8000, "recharge_period": 24, "storage_capacity": 40000})  # creation of an usine à gaz
# subclasses_dictionary["Device"]["Background"]("background", contract_test, dummy_agent, aggregator_elec, {"user": "ECOS", "device": "ECOS_5"})

# Performance measurement
CPU_time_generation_of_device = process_time()
# the following method create "n" agents with a predefined set of devices based on a JSON file
# agent_generation("single", 200, "lib/AgentTemplates/EgoistSingle.json", aggregator_elec, {"LVE": price_manager_TOU_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
# agent_generation("family", 200, "lib/AgentTemplates/EgoistFamily.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_TOU_elec, "LTH": price_manager_heat}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
# agent_generation("dummy", 1, "lib/AgentTemplates/DummyAgent.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_RTP_elec, "LTH": price_manager_heat}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "wind_speed_daemon": wind_daemon, "water_flow_daemon": water_flow_daemon, "sun_position_daemon": sun_position_daemon})

# CPU time measurement
CPU_time_generation_of_device = process_time() - CPU_time_generation_of_device  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the device generation phase: {CPU_time_generation_of_device}\n")
file.close()


# ##############################################################################################
# Forecaster
# from typing import Tuple
# import random as rd
# def noise_function(depth: int):
#     low_estimation = 1 - rd.random() * 0.01 * depth
#     high_estimation = 1 + rd.random() * 0.01 * depth
#     uncertainty = depth * 0.01
#
#     return low_estimation, high_estimation, uncertainty


# subclasses_dictionary["Forecaster"]["BasicForecaster"]("debug_forecaster", aggregator_elec, noise_function, 5)


# ##############################################################################################
# Datalogger
# this object is in charge of exporting data into files at a given iteration frequency
# world.catalog.print_debug()  # displays the content of the catalog

# export_graph_options_1 = GraphOptions("test_graph_options", "LaTeX")

# test_contract_datalogger = Datalogger("test_contract_datalogger", "StorageData", graph_options=export_graph_options_1)
# test_contract_datalogger.add("physical_time", graph_status="X")

# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  aggregator

# subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["PeakToAverageDatalogger"]()
# subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["CurtailmentDatalogger"](period=2)
# subclasses_dictionary["Datalogger"]["CurtailmentDatalogger"](period="global")

# subclasses_dictionary["Datalogger"]["DeviceQuantityDatalogger"]("tutu", "Tutu", ["dummy_complete_profile_0_ElectricDam_0"], period=1)

# subclasses_dictionary["Datalogger"]["WeightedCurtailmentDatalogger"](period=1)
# subclasses_dictionary["Datalogger"]["WeightedCurtailmentDatalogger"](period="global")

# producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances", period="global")
subclasses_dictionary["Datalogger"]["AgentBalancesDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period=1)
my_device_list = ["heat_sink"]
subclasses_dictionary["Datalogger"]["DeviceQuantityDatalogger"]("device_quantity_frequency_1",
                                                                "DeviceQuantity_frequency_1", my_device_list, period=1)

# figures
# export_graph_options_3 = GraphOptions("Test", ["LaTeX", "matplotlib"], "multiple_series")
# subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("Heating", 24, export_graph_options_3)


# CPU time measurement
CPU_time = process_time() - CPU_time  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the initialization phase: {CPU_time}\n")
file.close()


# ##############################################################################################
# here we have the possibility to save the world to use it later
# save_wanted = False
#
# if save_wanted:
#     CPU_time = process_time()  # CPU time measurement
#
#     world.save()  # saving the world
#     print("plop\n\n\n\n\n")
#
#     path = f"{world.catalog.get('path')}/inputs/save.tar"
#     world = World("new_world")  # creation
#     world.load(path)
#
#     # CPU time measurement
#     CPU_time = process_time() - CPU_time  # time taken by the initialization
#     filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
#     file = open(filename, "a")  # creation of the file
#     file.write(f"time taken by the saving phase: {CPU_time}\n")
#     file.close()

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

