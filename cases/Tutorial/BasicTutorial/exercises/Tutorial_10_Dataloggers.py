# Tutorial 10
# Dataloggers
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_10_dataloggers  # a specific importation

# ##############################################################################################
# Usual importations
from datetime import datetime

from os import chdir

from src.common.World import World

from src.common.Nature import Nature
from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent

from src.common.Aggregator import Aggregator

from src.common.Datalogger import Datalogger

from src.tools.GraphAndTex import GraphOptions

# ##############################################################################################
# Rerooting
chdir("../../../../")


# ##############################################################################################
# Importation of subclasses
from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


# ##############################################################################################
# Settings
# ##############################################################################################

# ##############################################################################################
# Creation of the world
name_world = "tuto_world"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
pathExport = "cases/Tutorial/BasicTutorial/Results"
world.set_directory(pathExport)


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("sunflower")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               168)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Natures

LVE = load_low_voltage_electricity()

LTH = load_low_temperature_heat()

Nature("PW", "Pressurized Water")

# ##############################################################################################
# Daemon

# price managers
price_manager_TOU_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("elec_prices", {"nature": LVE.name, "buying_price": [0.17, 0.12], "selling_price": [0.15, 0.15], "on-peak_hours": [[6, 12], [13, 23]]})

price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("heat_prices", {"nature": LTH.name, "buying_price": 0.12, "selling_price": 0.10})

# limit prices
limit_price_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.20, "limit_selling_price": 0.10})

limit_price_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.14, "limit_selling_price": 0.08})

# Meteorological daemons
indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Pau"})

sun_position_daemon = subclasses_dictionary["Daemon"]["SunPositionDaemon"]({"location": "Pau"})

water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "GavedePau_Pau"})


# ##############################################################################################
# Strategy

grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

elec_strategy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

heat_strategy = subclasses_dictionary["Strategy"]["LightAutarkyEmergency"]()


# ##############################################################################################
# Agent

producer = Agent("producer")

aggregator_owner = Agent("aggregators_owner")

consumer = Agent("consumer")


# ##############################################################################################
# Contract

BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("elec_contract_egoist", LVE, price_manager_TOU_elec)

curtailment_elec = subclasses_dictionary["Contract"]["CurtailmentContract"]("elec_contract_curtailment", LVE, price_manager_TOU_elec)

cooperative_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("heat_contract_cooperative", LTH, price_manager_heat)


# ##############################################################################################
# Aggregator

aggregator_grid = Aggregator("grid", LVE, grid_strategy, aggregator_owner)

aggregator_elec = Aggregator("aggregator_elec", LVE, elec_strategy, aggregator_owner, aggregator_grid, BAU_elec)  # creation of a aggregator

aggregator_heat = Aggregator("aggregator_heat", LTH, heat_strategy, aggregator_owner, aggregator_elec, BAU_elec, efficiency=3.5, capacity=1000)  # creation of a aggregator


# ##############################################################################################
# Device

subclasses_dictionary["Device"]["Photovoltaics"]("PV_field", BAU_elec, producer, aggregator_elec, {"device": "standard_field"}, {"panels": 500, "irradiation_daemon": irradiation_daemon})

subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", curtailment_elec, producer, aggregator_elec, {"device": "standard"}, {"wind_speed_daemon": wind_daemon})

subclasses_dictionary["Device"]["Background"]("background", BAU_elec, consumer, aggregator_elec, {"user": "family", "device": "family"})

subclasses_dictionary["Device"]["Dishwasher"]("dishwasher", BAU_elec, consumer, aggregator_elec, {"user": "family", "device": "medium_consumption"})

subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank", cooperative_heat, consumer, aggregator_heat, {"user": "family", "device": "family_heat"}, {"cold_water_temperature_daemon": water_temperature_daemon})

subclasses_dictionary["Device"]["Heating"]("heating", cooperative_heat, consumer, aggregator_heat, {"user": "residential", "device": "house_heat"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon})

# ##############################################################################################
# Automated generation of agents

world.agent_generation(50, "lib/AgentTemplates/DummyAgent.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_TOU_elec, "LTH": price_manager_heat}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon, "wind_speed_daemon": wind_daemon})


# ##############################################################################################
# Datalogger

# Inherited dataloggers for the balances of self-consumption and energy exchanges
# TODO: create a datalogger of the subclass "SelfSufficiencyDatalogger" with a period of 1

# TODO: create a datalogger of the subclass "NatureBalancesDatalogger" with a period "global"

# First basic instance of datalogger, which will be used for I/O operations, to handle a simple consumer
# TODO: create a graph_option object exporting in "csv" format

# TODO: create a datalogger called "consumer_datalogger_1", exporting data to the file "ConsumerData1", with a period of 2 rounds and creating a graph in csv

# TODO: add to the datalogger "consumer_datalogger_1" the key "simulation_time" to be used as the "X" axis

# TODO: add to the datalogger "consumer_datalogger_1" the key "consumer.LVE.energy_bought" to be used as the "Y" axis

# Second instance of datalogger, which will be used for I/O operations, to handle a consumer with more exported values
# TODO: create a graph_option object exporting in "csv" and in "LaTeX" formats, with a "single_series" graph type

# TODO: create a datalogger called "consumer_datalogger_2", exporting data to the file "ConsumerData2", with a period of 2 rounds and creating a graph in csv and in LaTeX

# TODO: add to the datalogger "consumer_datalogger_2" the key "simulation_time" as the "X" axis

# TODO: add to the datalogger "consumer_datalogger_2" the key "consumer.LVE.energy_bought" as a "Y" series

# TODO: add to the datalogger "consumer_datalogger_2" the key "consumer.LTH.energy_bought" as a "Y" series

# Third instance of datalogger, which will be used for I/O operations, to handle a consumer with extended options for exported values
# TODO: create a graph_option object exporting in "csv" and in "LaTeX" formats, with a "multiple_series" graph_type

# TODO: create a datalogger called "consumer_datalogger_3", exporting data to the file "ConsumerData3", with a period of 4 rounds and creating a graph in csv and in LaTeX

# TODO: add to the datalogger "consumer_datalogger_3" the key "simulation_time" as the "X" axis

# TODO: add to the datalogger "consumer_datalogger_3" the key "consumer.LVE.energy_bought" as a "Y" series, with "$\alpha$" as a legend and with a graph style "lines"

# TODO: add to the datalogger "consumer_datalogger_3" the key "consumer.LTH.energy_bought" as a "Y" series, with "$\beta$" as a legend and with a graph style "points"

# Fourth instance of datalogger, which will be used for I/O operations, to handle a consumer with more extended options for exported values
# TODO: create a graph_option object exporting in "csv", in "LaTeX" and in "matplotlib" formats, with a "multiple_series" graph_type

# TODO: create a datalogger called "consumer_datalogger_4", exporting data to the file "ConsumerData4", with a period of 4 rounds and creating a graph in csv, in LaTeX and in matplotlib, with a "multiple_series" graph type.

# TODO: add to the datalogger "consumer_datalogger_4" the key "simulation_time" to be used as the "X" axis

# TODO: add to the datalogger "consumer_datalogger_4" the key "consumer.LVE.energy_bought" as a "Y" series and with "$P_1$" as a legend

# TODO: add to the datalogger "consumer_datalogger_4" the key "consumer.LTH.energy_bought" as a "Y" series, and with "$P_2$" as a legend

# TODO: add to the datalogger "consumer_datalogger_4" the key "consumer.LTH.energy_bought" as a "Y2" series, with "$\mathcal{C}$" as a legend and with a graph style "points"


# ##############################################################################################
# Correction
correction_10_dataloggers()


