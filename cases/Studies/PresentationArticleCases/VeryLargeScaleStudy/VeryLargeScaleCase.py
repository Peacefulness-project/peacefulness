# script pour de la prédiction de consommation

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
world.set_directory("cases/Studies/PresentationArticleCases/Results/VeryLargeScaleCase/")  # here, you have to put the path to your results directory

# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("sunflower")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2019, month=3, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24 * 31)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Creation of nature
LVE = load_low_voltage_electricity()

LTH = load_low_temperature_heat()


# ##############################################################################################
# Creation of daemons

# Price Managers
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_elec", {"nature": LVE.name, "buying_price": 0.15, "selling_price": 0.10})  # sets prices for flat rate

price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_heat", {"nature": LVE.name, "buying_price": 0.15, "selling_price": 0.1})  # sets prices for flat rate

# Limit Prices
limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator

limit_price_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator

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

strategy_heat = subclasses_dictionary["Strategy"]["SubaggregatorHeatEmergency"]()


# ##############################################################################################
# Manual creation of agents
aggregator_owner = Agent("aggregator_owner")

heat_pump_owner = Agent("heat_pump")


# ##############################################################################################
# Manual creation of contracts

local_electrical_grid_contract = subclasses_dictionary["Contract"]["EgoistContract"]("local_electrical_grid_contract", LVE, price_manager_elec)

district_heating_contract = subclasses_dictionary["Contract"]["EgoistContract"]("district_heating_contract", LTH, price_manager_heat)

heat_pump_contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("heat_pump_contract_elec", LVE, price_manager_elec)

heat_pump_contract_heat = subclasses_dictionary["Contract"]["EgoistContract"]("heat_pump_contract_heat", LTH, price_manager_heat)

# ##############################################################################################
# Creation of aggregators
national_grid = Aggregator("national_grid", LVE, strategy_grid, aggregator_owner)

full_elec_renewable_district = Aggregator("full_elec_renewable_district", LVE, strategy_light_autarky, aggregator_owner, national_grid, local_electrical_grid_contract)

DHN_bound_renewable_district = Aggregator("DHN_bound_renewable_district", LVE, strategy_light_autarky, aggregator_owner, national_grid, local_electrical_grid_contract)

DHN = Aggregator("district_heating_network", LTH, strategy_heat, aggregator_owner, DHN_bound_renewable_district, district_heating_contract, 3.5, {"buying": 2000, "selling": 0})

old_district = Aggregator("old_district", LVE, strategy_light_autarky, aggregator_owner, national_grid, local_electrical_grid_contract)


# ##############################################################################################
# Manual creation of devices

# heat_pump = subclasses_dictionary["Device"]["HeatPump"]("converter", [heat_pump_contract_elec, heat_pump_contract_heat], heat_pump_owner, DHN_bound_renewable_district, DHN, {"device": "dummy_heat_pump"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/HeatPump.json")


# ##############################################################################################
# Automated generation of complete agents (i.e with devices and contracts)

# Performance measurement
CPU_time_generation_of_device = process_time()

# 50 000 dwellings
# 50% Ego, 30% Coop, 20% Curt

# Premier eco-quartier, 10 000 dwellings
# full elec with PV
# 50% 2 people and 50% 5 people

# Egoist contracts
world.agent_generation("", 2500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_BAU_house_PV.json", [full_elec_renewable_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})
world.agent_generation("", 2500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_BAU_PV.json", [full_elec_renewable_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})

# Cooperative contracts
world.agent_generation("", 1500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_DLC_house_PV.json", [full_elec_renewable_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})
world.agent_generation("", 1500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_DLC_PV.json", [full_elec_renewable_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})

# Curtailment contracts
world.agent_generation("", 1000, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_curtailment_house_PV.json", [full_elec_renewable_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})
world.agent_generation("", 1000, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_curtailment_PV.json", [full_elec_renewable_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})


# Second eco-quartier, 10 000 dwellings
# elec and DHN with ST
# 50% 2 people and 50% 5 people

# Egoist contracts
world.agent_generation("", 2500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_BAU_house_no_PV.json", [DHN, DHN_bound_renewable_district], {"LVE": price_manager_elec, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})
world.agent_generation("", 2500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_BAU_no_PV.json", [DHN, DHN_bound_renewable_district], {"LVE": price_manager_elec, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})

# Cooperative contracts
world.agent_generation("", 1500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_DLC_house_no_PV.json", [DHN, DHN_bound_renewable_district], {"LVE": price_manager_elec, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})
world.agent_generation("", 1500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_DLC_no_PV.json", [DHN, DHN_bound_renewable_district], {"LVE": price_manager_elec, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})

# Curtailment contracts
world.agent_generation("", 1000, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_curtailment_house_no_PV.json", [DHN, DHN_bound_renewable_district], {"LVE": price_manager_elec, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})
world.agent_generation("", 1000, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_curtailment_no_PV.json", [DHN, DHN_bound_renewable_district], {"LVE": price_manager_elec, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon, "irradiation_daemon": irradiation_daemon})


# flat, 30 000 dwellings
# full elec with nothing
# 40% 1 people, 30% 2 people and 30% 5 people

# Egoist contracts
world.agent_generation("", 6000, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_1_BAU.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 4500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_BAU.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 4500, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_BAU_apartment.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# Cooperative contracts
world.agent_generation("", 3600, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_1_DLC.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 2700, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_DLC.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 2700, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_DLC_apartment.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

# Curtailment contracts
world.agent_generation("", 2400, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_1_curtailment.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 1800, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_2_curtailment.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
world.agent_generation("", 1800, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Agent_5_curtailment_apartment.json", [old_district], {"LVE": price_manager_elec}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})


# CPU time measurement
CPU_time_generation_of_device = process_time() - CPU_time_generation_of_device  # time taken by the initialization
filename = world._catalog.get("path") + "/outputs/CPU_time.txt"  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the device generation phase: {CPU_time_generation_of_device}\n")
file.close()

# ##############################################################################################
# Creation of dataloggers
graph_options = GraphOptions("graph_options_1", "LaTeX", "single_series")

# datalogger for balances
# these dataloggers record the balances for each nature and aggregator
subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=24)
subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period=24)
subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["PeakToAverageDatalogger"]()

subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period=24)
subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period=24)
subclasses_dictionary["Datalogger"]["WeightedSelfSufficiencyDatalogger"](period=24)
subclasses_dictionary["Datalogger"]["WeightedSelfSufficiencyDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("PhotovoltaicsAdvanced", 24)
subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("PhotovoltaicsAdvanced", "global")

subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("SolarThermalCollector", 24)
subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("SolarThermalCollector", "global")

subclasses_dictionary["Datalogger"]["CurtailmentDatalogger"](period=24)
subclasses_dictionary["Datalogger"]["WeightedCurtailmentDatalogger"](period=24)
subclasses_dictionary["Datalogger"]["WeightedCurtailmentDatalogger"](period="global")

subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"](period=24)
subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"](period="global")


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



