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

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses


# ##############################################################################################
# Performance measurement
CPU_time = process_time()

# ##############################################################################################
# Minimum
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
start_date = datetime.now()  # a start date in the datetime format
start_date = start_date.replace(year=2019, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24*7)  # number of time steps simulated

# ##############################################################################################
# Model
# the following objects are the one describing the case studied
# you need at least one local grid and one agent to create a device
# no matter the type, you can create as much objects as you want
# ##############################################################################################

# ##############################################################################################
# Strategy
# this object defines a strategy of supervision through 3 steps: local distribution, formulation of its needs, remote distribution

# AutarkyEmergency AlwaysSatisfied WhenProfitable

# the BAU strategy
description = "Always serves everybody, whatever it can cost to him."
name_strategy = "elec_strategy"
strategy_elec = subclasses_dictionary["AlwaysSatisfied"](world, name_strategy, description)

# the heat strategy
description = "Always serves everybody, whatever it can cost to him."
name_strategy = "heat_strategy"
strategy_heat = subclasses_dictionary["SubaggregatorHeatEmergency"](world, name_strategy, description)

# the strategy grid, which always proposes an infinite quantity to sell and to buy
description = "this strategy represents the ISO. Here, we consider that it has an infinite capacity to give or to accept energy"
name_strategy = "benevolent_operator"
grid_strategy = subclasses_dictionary["Grid"](world, name_strategy, description)

# ##############################################################################################
# Nature list
# this object represents a nature of energy present in world
nature_name = "LVE"
nature_description = "Low Voltage Electricity"
elec = Nature(world, nature_name, nature_description)  # creation of a nature

nature_name = "Heat"
nature_description = "Energy transported by a district heating network"
heat = Nature(world, nature_name, nature_description)  # creation of a nature

# ##############################################################################################
# Aggregator
# this object is a collection of devices wanting to isolate themselves as much as they can
# aggregators need 2 arguments: a name and a nature of energy
# there is also a third argument to precise if the aggregator is considered as an infinite grid

# and then we create a third who represents the grid
aggregator_name = "Enedis"
aggregator_grid = Aggregator(world, aggregator_name, elec, grid_strategy)

# here we create a second one put under the orders of the first
aggregator_name = "general_aggregator"
aggregator_elec = Aggregator(world, aggregator_name, elec, strategy_elec, aggregator_grid)  # creation of a aggregator

# here we create another aggregator dedicated to heat
aggregator_name = "Local_DHN"
aggregator_heat = Aggregator(world, aggregator_name, heat, strategy_heat)  # creation of a aggregator


# ##############################################################################################
# Contract
# this object has 3 roles: managing the dissatisfaction, managing the billing and defining the operations allowed to the strategy
# contracts have to be defined for each nature for each agent BUT are not linked initially to a nature

# producers
TOU_prices = "TOU_prices"
BAU_elec = subclasses_dictionary["TOUEgoistContract"](world, "BAU_elec", elec, TOU_prices)

flat_prices_heat = "flat_prices_heat"
BAU_heat = subclasses_dictionary["FlatEgoistContract"](world, "BAU_heat", heat, flat_prices_heat)
cooperative_contract_heat = subclasses_dictionary["FlatCooperativeContract"](world, "cooperative_contract_heat", heat, flat_prices_heat)

flat_prices_elec = "flat_prices_elec"
# cooperative_elec = subclasses_dictionary["Flattract"](world, "BAU_elec", elec, flat_prices_elec)
# cooperative_contract_elec = subclasses_dictionary["FlatCooperativeContract"](world, "cooperative_contract_elec", elec, flat_prices_elec)

owned_by_aggregator = "owned_by_aggregator"
cooperative_contract_elec = subclasses_dictionary["FlatCooperativeContract"](world, "cooperative_contract_elec", elec, owned_by_aggregator)


# ##############################################################################################
# Agent
# this object represents the owner of devices
# all devices need an agent
WT_producer = Agent(world, "WT_producer")  # creation of an agent

DHN_producer = Agent(world, "DHN_producer")  # creation of an agent

heat_pump_owner = Agent(world, "heat_pump_owner")


# ##############################################################################################
# Converter
heatpump = subclasses_dictionary["HeatPump"](world, "heat_pump", BAU_elec, heat_pump_owner, aggregator_elec, aggregator_heat, "dummy_heat_pump")


# ##############################################################################################
# Device
# these objects regroup production, consumption, storage and transformation devices
# they at least need a name and a nature
# some devices are pre-defined (such as PV) but user can add some by creating new classes in lib

wind_turbine = subclasses_dictionary["WindTurbine"](world, "wind_turbine", cooperative_contract_elec, WT_producer, aggregator_elec, "ECOS", "ECOS")  # creation of a wind turbine
heat_production = subclasses_dictionary["GenericProducer"](world, "heat_production", cooperative_contract_heat, DHN_producer, aggregator_heat, "ECOS", "ECOS")  # creation of a heat production unit

# Performance measurement
CPU_time_generation_of_device = process_time()
# the following method create "n" agents with a predefined set of devices based on a JSON file


# # # BAU contracts
world.agent_generation(1, "lib/AgentTemplates/EgoistSingle.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "Heat": flat_prices_heat})
world.agent_generation(1, "lib/AgentTemplates/EgoistFamily.json", [aggregator_elec, aggregator_heat], {"LVE": TOU_prices, "Heat": flat_prices_heat})
world.agent_generation(0, "lib/AgentTemplates/DummyAgent.json", [aggregator_elec, aggregator_heat], {"LVE": flat_prices_elec, "Heat": flat_prices_heat})

# CPU time measurement
CPU_time_generation_of_device = process_time() - CPU_time_generation_of_device  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the device generation phase: {CPU_time_generation_of_device}\n")
file.close()


# ##############################################################################################
# Daemon
# this object updates values of the catalog not taken in charge by anyone else

# dissatisfaction erosion
# this daemon reduces slowly the dissatisfaction of all agents over the time
# here it is set like this: 10% of dissatisfaction will remain after one week (168 hours) has passed
# dissatisfaction_management = subclasses_dictionary[DissatisfactionErosionDaemon"](world, "DissatisfactionErosion", 1, {"coef_1": 0.9, "coef_2": 168})  # creation

# Price Managers
# these daemons fix a price for a given nature of energy
price_manager_owned_by_the_aggregator = subclasses_dictionary["PriceManagerDaemon"](world, "toto", 1, {"nature": elec.name, "buying_price": 0, "selling_price": 0, "identifier": owned_by_aggregator})  # as these devices are owned by the aggregator, energy is free
price_manager_cooperative_elec = subclasses_dictionary["PriceManagerDaemon"](world, "titi", 1, {"nature": elec.name, "buying_price": 0.15, "selling_price": 0.1, "identifier": flat_prices_elec})  # sets prices for flat rate
price_manager_heat = subclasses_dictionary["PriceManagerDaemon"](world, "Picsou", 1, {"nature": heat.name, "buying_price": 0.15, "selling_price": 0.1, "identifier": flat_prices_heat})  # sets prices for flat rate
price_manager_elec = subclasses_dictionary["PriceManagerTOUDaemon"](world, "Flairsou", 1, {"nature": elec.name, "buying_price": [0.2125, 0.15], "selling_price": [0, 0], "hours": [[6, 12], [14, 23]], "identifier": TOU_prices})  # sets prices for TOU rate
price_elec_grid = subclasses_dictionary["GridPricesDaemon"](world, "LVE_tariffs", 1, {"nature": elec.name, "grid_buying_price": 0.2, "grid_selling_price": 0.1})  # sets prices for the system operator
price_heat_grid = subclasses_dictionary["GridPricesDaemon"](world, "Heat_tariffs", 1, {"nature": heat.name, "grid_buying_price": 0.30, "grid_selling_price": 0.00})  # sets prices for the system operator

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = subclasses_dictionary["IndoorTemperatureDaemon"](world, "indoor_temperature", 1)

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["OutdoorTemperatureDaemon"](world, "outdoor_temperature_daemon", {"location": "Pau"})

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = subclasses_dictionary["ColdWaterDaemon"](world, "water_temperature_daemon", {"location": "Pau"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["IrradiationDaemon"](world, "irradiation_daemon", {"location": "Pau"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["WindDaemon"](world, "wind_speed_daemon", {"location": "Pau"})


# ##############################################################################################
# Datalogger
# this object is in charge of exporting data into files at a given iteration frequency
# world.catalog.print_debug()  # displays the content of the catalog

# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  aggregator
# contract_balances = subclasses_dictionary["ContractBalanceDatalogger"]()
aggregator_balances = subclasses_dictionary["AggregatorBalanceDatalogger"](world)
nature_balances = subclasses_dictionary["NatureBalanceDatalogger"](world)

#
# ECOS_agent_datalogger = subclasses_dictionary["ECOSDatalogger"].ECOSAgentDatalogger("month")
# ECOS_aggregator_datalogger = subclasses_dictionary["ECOSDatalogger"].ECOSDatalogger()
# global_values_datalogger = subclasses_dictionary["ECOSDatalogger"].GlobalValuesDatalogger()
# world.register_datalogger(ECOS_agent_datalogger)  # registration
# world.register_datalogger(ECOS_aggregator_datalogger)  # registration
# world.register_datalogger(global_values_datalogger)  # registration

# datalogger used to get back producer outputs
producer_datalogger = Datalogger(world, "producer_datalogger", "ProducerBalances.txt")

producer_datalogger.add(f"{WT_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{WT_producer.name}.LVE.energy_sold")
producer_datalogger.add(f"{DHN_producer.name}.Heat.energy_erased")
producer_datalogger.add(f"{DHN_producer.name}.Heat.energy_sold")
producer_datalogger.add(f"{heat_pump_owner.name}.LVE.energy_bought")
producer_datalogger.add(f"{heat_pump_owner.name}.Heat.energy_sold")

# producer_datalogger.add(f"{PV_producer.name}.LVE.energy_erased")
# producer_datalogger.add(f"{solar_thermal_collector_producer.name}.Heat.energy_erased")
# producer_datalogger.add(f"{PV_producer.name}.LVE.energy_sold")
# producer_datalogger.add(f"{solar_thermal_collector_producer.name}.Heat.energy_sold")
#
# producer_datalogger.add(f"{PV_field.name}_exergy_in")
# producer_datalogger.add(f"{solar_thermal_collector_field.name}_exergy_in")
# producer_datalogger.add(f"{PV_field.name}_exergy_out")
# producer_datalogger.add(f"{solar_thermal_collector_field.name}_exergy_out")
producer_datalogger.add("Pau.reference_temperature")
producer_datalogger.add("Pau.irradiation_value")

test_datalogger = Datalogger(world, "test_datalogger", "test")
test_datalogger.add("egoist_single_0.LVE.energy_bought")
test_datalogger.add("egoist_single_0.Heat.energy_bought")
test_datalogger.add("egoist_single_0.money_spent")

test_datalogger.add("egoist_family_0.LVE.energy_bought")
test_datalogger.add("egoist_family_0.Heat.energy_bought")
test_datalogger.add("egoist_family_0.money_spent")

test_datalogger.add("egoist_single_0_Heating_0.LVE.energy_accorded")
test_datalogger.add("egoist_single_0_HotWaterTank_0.LVE.energy_accorded")

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
    world.save()  # saving the world

# ##############################################################################################
# Work in progress
# here begins the supervision, which is not implemented yet
world.start()




