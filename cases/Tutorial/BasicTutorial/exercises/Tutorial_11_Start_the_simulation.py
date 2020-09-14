# Tutorial 11
# Start the simulation
from cases.Tutorial.BasicTutorial.AdditionalData.Correction_scripts import correction_11_start_the_simulation  # a specific importation

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

# low voltage electricity
LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()


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

subclasses_dictionary["Device"]["PV"]("PV_field", BAU_elec, producer, aggregator_elec, {"device": "standard_field"}, {"panels": 500, "irradiation_daemon": irradiation_daemon})

subclasses_dictionary["Device"]["WindTurbine"]("wind_turbine", curtailment_elec, producer, aggregator_elec, {"device": "standard"}, {"wind_speed_daemon": wind_daemon})

subclasses_dictionary["Device"]["Background"]("background", BAU_elec, consumer, aggregator_elec, {"user": "family", "device": "family"})

subclasses_dictionary["Device"]["Dishwasher"]("dishwasher", BAU_elec, consumer, aggregator_elec, {"user": "family", "device": "medium_consumption"})

subclasses_dictionary["Device"]["HotWaterTank"]("hot_water_tank", cooperative_heat, consumer, aggregator_heat, {"user": "family", "device": "family_heat"}, {"cold_water_temperature_daemon": water_temperature_daemon})

subclasses_dictionary["Device"]["Heating"]("heating", cooperative_heat, consumer, aggregator_heat, {"user": "residential", "device": "house_heat"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon})

# ##############################################################################################
# Automated generation of agents

world.agent_generation(50, "lib/AgentTemplates/DummyAgent.json", [aggregator_elec, aggregator_heat], {"LVE": price_manager_TOU_elec, "LTH": price_manager_heat}, {"irradiation_daemon": irradiation_daemon, "outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": water_temperature_daemon, "wind_speed_daemon": wind_daemon, "sun_position_daemon": sun_position_daemon, "water_flow_daemon": water_flow_daemon})


# ##############################################################################################
# Datalogger

# Inherited dataloggers for the balances of self-consumption and energy exchanges
subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](1)

subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]("global")

# First basic instance of datalogger, which will be used for I/O operations, to handle a simple consumer
export_graph_options_1 = GraphOptions("csv")

consumer_datalogger_1 = Datalogger("consumer_datalogger_1", "ConsumerData1", 2, graph_options=export_graph_options_1, graph_labels={"xlabel": "X", "ylabel": "Y"})

consumer_datalogger_1.add("simulation_time", graph_status="X")

consumer_datalogger_1.add("consumer.LVE.energy_bought", graph_status="Y")

# Second instance of datalogger, which will be used for I/O operations, to handle a consumer with more exported values
export_graph_options_2 = GraphOptions(["csv", "LaTeX"], "multiple_series")

consumer_datalogger_2 = Datalogger("consumer_datalogger_2", "ConsumerData2", 2, graph_options=export_graph_options_2, graph_labels={"xlabel": "X", "ylabel": "Y"})

consumer_datalogger_2.add("simulation_time", graph_status="X")

consumer_datalogger_2.add("consumer.LVE.energy_bought", graph_status="Y")
consumer_datalogger_2.add("consumer.LTH.energy_bought", graph_status="Y")

# Third instance of datalogger, which will be used for I/O operations, to handle a consumer with extended options for exported values
export_graph_options_3 = GraphOptions(["csv", "LaTeX"], "multiple_series")

axis_labels = {"xlabel": "X-axis", "ylabel": "Y-axis"}
consumer_datalogger_3 = Datalogger("consumer_datalogger_3", "ConsumerData3", 4, graph_options=export_graph_options_3, graph_labels=axis_labels)

consumer_datalogger_3.add("simulation_time", graph_status="X")

consumer_datalogger_3.add("consumer.LVE.energy_bought", graph_status="Y", graph_legend=r"$\alpha$", graph_style="lines")
consumer_datalogger_3.add("consumer.LTH.energy_bought", graph_status="Y", graph_legend=r"$\beta$", graph_style="points")

# Fourth instance of datalogger, which will be used for I/O operations, to handle a consumer with more extended options for exported values
export_graph_options_4 = GraphOptions(["csv", "LaTeX", "matplotlib"], "multiple_series")

axis_labels = {"xlabel": "$t \, [\si{\hour}]$", "ylabel": "$\mathcal{P}_{ref.} \, [\si{\watt}]$"}
consumer_datalogger_4 = Datalogger("consumer_datalogger_4", "ConsumerData4", 4, graph_options=export_graph_options_4, graph_labels=axis_labels)

consumer_datalogger_4.add("simulation_time", graph_status="X")

consumer_datalogger_4.add("consumer.LVE.energy_bought", graph_status="Y", graph_legend=r"$P_1$", graph_style="lines")
consumer_datalogger_4.add("consumer.LTH.energy_bought", graph_status="Y", graph_legend=r"$P_2$", graph_style="lines")
consumer_datalogger_4.add("consumer.money_spent", graph_status="Y2", graph_legend=r"$\mathcal{C}$", graph_style="points")


# ##############################################################################################
# Start the simulation
# TODO: start the simulation using the method start of world

# ##############################################################################################
# Correction
correction_11_start_the_simulation()


