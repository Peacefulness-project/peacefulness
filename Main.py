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

from src.tools.GraphAndTex import graph_options


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
start_date = datetime(year=2020, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24*365)  # number of time steps simulated

#world.choose_exports("matplotlib")

# ##############################################################################################
# Optionnal
#world.complete_message("CO2", 0)


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
price_manager_cooperative_elec = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("RTP_prices_elec", {"location": "France"})  # sets prices for flat rate
price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.15, "selling_price": 0.1})  # sets prices for flat rate
price_manager_TOU_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.2125, 0.15], "selling_price": [0, 0], "on-peak_hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
price_manager_RTP_heat = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("RTP_prices_heat", {"location": "France"})  # sets prices for flat rate

limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.1})  # sets prices for the system operator
limit_price_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.30, "limit_selling_price": 0.00})  # sets prices for the system operator


# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Lyon"})

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "Pau"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Lyon"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["Daemon"]["WindDaemon"]({"location": "Lyon"})
wind_daemon_2 = subclasses_dictionary["Daemon"]["WindDaemon"]({"location": "Pau"})

#SunPosition
sun_position_daemon = subclasses_dictionary["Daemon"]["SunPositionDaemon"]({"location": "Lyon"})
sun_position_daemon = subclasses_dictionary["Daemon"]["SunPositionDaemon"]({"location": "Pau"})

# Water Flow
water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "Saone_Lyon"})
water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "GavedePau_Pau"})

# Forecast
# this daemon is supposed to create predictions about future consumption and demands
forecast_daemon = subclasses_dictionary["Daemon"]["DummyForecasterDaemon"]("dummy_forecaster")

# ##############################################################################################
# Strategy
# this object defines a strategy of supervision through 3 steps: local distribution, formulation of its needs, remote distribution

# the BAU strategy
strategy_elec = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# the heat strategy
strategy_heat = subclasses_dictionary["Strategy"]["SubaggregatorHeatEmergency"]()

# the strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Agent
# this object represents the owner of devices
# all devices need an agent
WT_producer = Agent("WT_producer")  # creation of an agent

DHN_producer = Agent("DHN_producer")  # creation of an agent

heat_pump_owner = Agent("heat_pump_owner")

aggregator_manager = Agent("aggregator_manager")

CO2_producer = Agent("CO2_producer")

solar_owner = Agent("solar_owner")

# ##############################################################################################
# Contract
# this object has 3 roles: managing the dissatisfaction, managing the billing and defining the operations allowed to the strategy
# contracts have to be defined for each nature for each agent BUT are not linked initially to a nature

# producers
BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_TOU_elec)

BAU_heat = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_manager_heat)

cooperative_contract_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_heat", LTH, price_manager_heat)

cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_cooperative_elec)

contract_owned_by_aggregator = subclasses_dictionary["Contract"]["CooperativeContract"]("owned_by_aggregator_contract", LVE, price_manager_owned_by_the_aggregator)

contract_converter_heat = subclasses_dictionary["Contract"]["ThresholdPricesContract"]("contract_converter_heat", LTH, price_manager_RTP_heat, {"buying_threshold": 0, "selling_threshold": 0.2})

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
aggregator_heat = Aggregator(aggregator_name, LTH, strategy_heat, aggregator_manager, aggregator_elec, BAU_elec)  # creation of a aggregator


# ##############################################################################################
# Device
# these objects regroup production, consumption, storage and transformation devices
# they at least need a name and a nature
# some devices are pre-defined (such as PV) but user can add some by creating new classes in lib

wind_turbine_Alois = subclasses_dictionary["Device"]["WindTurbine_Alois"]("wind_turbine_Alois", BAU_elec, WT_producer, aggregator_elec, {"device": "standard"}, {"location": "Lyon", "rugosity": "flat"})  # creation of a wind turbine

#heat_production = subclasses_dictionary["Device"]["DummyProducer"]("heat_production", cooperative_contract_heat, DHN_producer, aggregator_heat, "ECOS", "ECOS")  # creation of a heat production unit

heating = subclasses_dictionary["Device"]["Heating"]("heating", cooperative_contract_heat, DHN_producer, aggregator_heat, {"user": "residential", "device": "house_heat"}, {"location": "Pau"})

Jack = subclasses_dictionary["Device"]["SolarThermalCollector"]("Jack", BAU_heat, solar_owner, aggregator_heat, {"device": "standard"}, {"location": "Lyon", "panels": 6})

Michel = subclasses_dictionary["Device"]["PV_Alois"]("Michel", BAU_elec, solar_owner, aggregator_elec, {"device": "standard_field"}, {"location": "Lyon", "panels": 6})

#subclasses_dictionary["Device"]["WindTurbine"]("Toto", BAU_elec, solar_owner, aggregator_elec, "ECOS", {"location": "Lyon"})

Dam = subclasses_dictionary["Device"]["ElectricDam"]("Dam", BAU_elec, DHN_producer, aggregator_elec, {"device": "Kaplan"}, {"height": 10, "location": "Saone_Lyon"})

Tour = subclasses_dictionary["Device"]["SolarTower"]("Tour", BAU_elec, solar_owner, aggregator_elec, {"device": "molten_salt"}, {"location": "Lyon", "surface": 100})

# Performance measurement
CPU_time_generation_of_device = process_time()
# the following method create "n" agents with a predefined set of devices based on a JSON file
#world.agent_generation(1, "lib/AgentTemplates/EgoistSingle.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_TOU_elec, "LTH": price_manager_heat})
#world.agent_generation(1, "lib/AgentTemplates/EgoistFamily.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_TOU_elec, "LTH": price_manager_heat})
#world.agent_generation(1, "lib/AgentTemplates/DummyAgent.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_cooperative_elec, "LTH": price_manager_heat})

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

# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  aggregator
subclasses_dictionary["Datalogger"]["AgentBalancesDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["AgentBalancesDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["PeakToAverageDatalogger"]()
subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period=1)
subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period="global")


# datalogger used to get back producer outputs
producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")
producer_datalogger.add("physical_time", graph_status="X")

# producer_datalogger.add(f"{WT_producer.name}.LVE.energy_erased")
# producer_datalogger.add(f"{WT_producer.name}.LVE.energy_sold")
# producer_datalogger.add(f"{DHN_producer.name}.LTH.energy_erased")
# producer_datalogger.add(f"{DHN_producer.name}.LTH.energy_sold")
# producer_datalogger.add(f"{heat_pump_owner.name}.LVE.energy_bought")
# producer_datalogger.add(f"{heat_pump_owner.name}.LTH.energy_sold")

# producer_datalogger.add(f"{PV_producer.name}.LVE.energy_erased")
# producer_datalogger.add(f"{solar_thermal_collector_producer.name}.LTH.energy_erased")
# producer_datalogger.add(f"{PV_producer.name}.LVE.energy_sold")
# producer_datalogger.add(f"{solar_thermal_collector_producer.name}.LTH.energy_sold")
#
# producer_datalogger.add(f"{PV_field.name}_exergy_in")
# producer_datalogger.add(f"{solar_thermal_collector_field.name}_exergy_in")
# producer_datalogger.add(f"{PV_field.name}_exergy_out")
# producer_datalogger.add(f"{solar_thermal_collector_field.name}_exergy_out")
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

# Exports


# CPU time measurement
CPU_time = process_time() - CPU_time  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the initialization phase: {CPU_time}\n")
file.close()


# ##############################################################################################
# here we have the possibility to save the world to use it later
save_wanted = True

if save_wanted:
    CPU_time = process_time()  # CPU time measurement

    # world.save()  # saving the world

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




