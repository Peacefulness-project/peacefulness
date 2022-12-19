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
chdir("../../../../")  # here, you have to put the path to the root of project (the main directory)


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
world.set_directory("cases/Studies/PresentationArticleCases/Results/RandomizationExample/")  # here, you have to put the path to your results directory

# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("sunflower")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2019, month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24 * 7)  # number of time steps simulated


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

price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_heat", {"nature": LTH.name, "buying_price": 0.15, "selling_price": 0.10})  # sets prices for flat rate

# Limit Prices
limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.1})  # sets prices for the system operator

limit_price_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.2, "limit_selling_price": 0.1})  # sets prices for the system operator

# Indoor temperature
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Marseille_not_averaged"})

# Water temperature
cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

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

heat_producer = Agent("heat_producer")


# ##############################################################################################
# Manual creation of contracts

# aggregators
local_electrical_grid_contract = subclasses_dictionary["Contract"]["EgoistContract"]("local_electrical_grid_contract", LVE, price_manager_elec)

district_heating_network_contract = subclasses_dictionary["Contract"]["EgoistContract"]("district_heating_network_contract", LTH, price_manager_heat)

# producers
cooperative_elec_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_elec_contract", LVE, price_manager_elec)

egoist_elec_contract = subclasses_dictionary["Contract"]["EgoistContract"]("egoist_contract_elec", LVE, price_manager_elec)

cooperative_heat_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_heat_contract", LTH, price_manager_heat)


# ##############################################################################################
# Creation of aggregators
national_grid = Aggregator("national_grid", LVE, strategy_grid, aggregator_owner)

local_electrical_grid = Aggregator("local_electrical_grid", LVE, strategy_light_autarky, aggregator_owner, national_grid, local_electrical_grid_contract)

district_heating_network = Aggregator("district_heating_network", LTH, strategy_light_autarky, aggregator_owner, local_electrical_grid, district_heating_network_contract)


# ##############################################################################################
# Manual creation of devices


# ##############################################################################################
# Automated generation of complete agents (i.e with devices and contracts)

# Performance measurement
CPU_time_generation_of_device = process_time()


world.agent_generation("", 1000, "cases/Studies/PresentationArticleCases/AdditionalData/AgentTemplates/Randomization_example.json", [local_electrical_grid, district_heating_network], {"LVE": price_manager_elec, "LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})


# CPU time measurement
CPU_time_generation_of_device = process_time() - CPU_time_generation_of_device  # time taken by the initialization
filename = world._catalog.get("path") + "/outputs/CPU_time.txt"  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the device generation phase: {CPU_time_generation_of_device}\n")
file.close()

# ##############################################################################################
# Creation of dataloggers
export_graph_options_1 = GraphOptions("test_graph_options", "LaTeX")

producer_datalogger = Datalogger("agent_alone", "AgentAlone", graph_options=export_graph_options_1, graph_labels={"xlabel": "time", "ylabel": "producer"})
producer_datalogger.add("simulation_time", graph_status="X")
producer_datalogger.add(f"_2_people_example_0.LVE.energy_bought")
producer_datalogger.add(f"_2_people_example_0.LTH.energy_bought")

subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](graph_options=export_graph_options_1)
subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]("global", export_graph_options_1)


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


