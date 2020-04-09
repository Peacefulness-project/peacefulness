# This script is the one given in example in the github wiki.


# ##############################################################################################
# Importations
# ##############################################################################################

from datetime import datetime

import lib.Subclasses as User
from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.World import World
from src.common.Datalogger import Datalogger
from src.common.Nature import Nature

# ##############################################################################################
# Rerooting
# ##############################################################################################

# here, we reroot this script at the root of the project.
from os import chdir
chdir("../../")  # root of the project


# ##############################################################################################
# Parameters
# ##############################################################################################


# ##############################################################################################
# Creation of the world

name_world = "disc_world"
world = World(name_world)  # creation


# ##############################################################################################
# Results directory

pathExport = "cases/TutorialAndExamples/Results/disc_world"
world.set_directory(pathExport)  # registration


# ##############################################################################################
# Random seed

world.set_random_seed("tournesol")


# ##############################################################################################
# Time

start_date = datetime.now()  # a start date in the datetime format
start_date = start_date.replace(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24*365)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################


# ##############################################################################################
# Creation of supervisors

# the BAU supervisor
description = "Calls the grid only if can't balance the grid alone"
name_supervisor = "elec_supervisor"
supervisor_elec = User.Strategies.LightAutarkyEmergency.LightAutarkyEmergency(name_supervisor, description)
world.register_supervisor(supervisor_elec)

# the heat supervisor
description = "Always ask to buy energy when it needs something but can't sell."
name_supervisor = "heat_supervisor"
supervisor_heat = User.Strategies.SubclusterHeatEmergency.SubclusterHeatEmergency(name_supervisor, description)
world.register_supervisor(supervisor_heat)

# the supervisor grid, which always proposes an infinite quantity to sell and to buy
description = "this supervisor represents the national electrical grid behavior. Here, we consider that it has an infinite capacity to give or to accept energy"
name_supervisor = "benevolent_operator"
national_grid_supervisor = User.Strategies.Grid.Grid(name_supervisor, description)
world.register_supervisor(national_grid_supervisor)


# ##############################################################################################
# Creation of nature

nature_name = "LVE"
nature_description = "Low Voltage Electricity"
elec = Nature(nature_name, nature_description)  # creation of a nature
world.register_nature(elec)  # registration

nature_name = "Heat"
nature_description = "Energy transported by a district heating network"
heat = Nature(nature_name, nature_description)  # creation of a nature
world.register_nature(heat)  # registration


# ##############################################################################################
# Creation of clusters

# we create a first cluster who represents the national electrical grid
cluster_name = "Enedis"
cluster_grid = Aggregator(cluster_name, elec, national_grid_supervisor)
world.register_cluster(cluster_grid)  # registration

# here we create a second one put under the orders of the first
cluster_name = "general_cluster"
cluster_elec = Aggregator(cluster_name, elec, supervisor_elec, cluster_grid, 1, 100000)  # creation of a cluster
world.register_cluster(cluster_elec)  # registration

# here we create another cluster dedicated to heat, under the order of the local electrical grid
cluster_name = "Local_DHN"
cluster_heat = Aggregator(cluster_name, heat, supervisor_heat, cluster_elec, 3.6, 2000)  # creation of a cluster
world.register_cluster(cluster_heat)  # registration


# ##############################################################################################
# Manual creation of contracts

# producers
BAU_elec = User.Contracts.TOUEgoistContract.TOUEgoistContract("BAU_elec", elec, {"selling_price": 0.1, "buying_price": 0.11})
world.register_contract(BAU_elec)

cooperative_contract_elec = User.Contracts.FlatCooperativeContract.FlatCooperativeContract("cooperative_contract_elec", elec, {"selling_price": 0.1, "buying_price": 0.12})
world.register_contract(cooperative_contract_elec)

cooperative_contract_heat = User.Contracts.FlatCooperativeContract.FlatCooperativeContract("cooperative_contract_heat", heat, {"selling_price": 0.08, "buying_price": 0.1})
world.register_contract(cooperative_contract_heat)


# ##############################################################################################
# Manual creation of agents

PV_producer = Agent("PV_producer")  # creation of an agent
world.register_agent(PV_producer)  # registration
PV_producer.set_contract(elec, BAU_elec)

WT_producer = Agent("WT_producer")  # creation of an agent
world.register_agent(WT_producer)  # registration
WT_producer.set_contract(elec, cooperative_contract_elec)

DHN_producer = Agent("DHN_producer")  # creation of an agent
world.register_agent(DHN_producer)  # registration
DHN_producer.set_contract(heat, cooperative_contract_heat)


# ##############################################################################################
# Manual creation of devices

PV_field = User.Devices.NonControllableDevice.PV.PV("PV_field", BAU_elec, PV_producer, cluster_elec, "ECOS", "ECOS_field", {"surface": 2500})  # creation of a photovoltaic panel field
world.register_device(PV_field)  # registration of a production device

wind_turbine = User.Devices.NonControllableDevice.WindTurbine.WindTurbine("wind_turbine", cooperative_contract_elec, WT_producer, cluster_elec, "ECOS", "ECOS")  # creation of a wind turbine
world.register_device(wind_turbine)  # registration of a production device

heat_production = User.Devices.NonControllableDevice.GenericProducer.GenericProducer("heat_production", cooperative_contract_heat, DHN_producer, cluster_heat, "ECOS", "ECOS")  # creation of a heat production unit
world.register_device(heat_production)  # registration of a production device


# ##############################################################################################
# Automated generation of complete agents (i.e with devices and contracts)

# BAU contracts
world.agent_generation(165, "lib/AgentTemplates/AgentTemplates/AgentGitHub_1_BAU.json", [cluster_elec, cluster_heat])
world.agent_generation(330, "lib/AgentTemplates/AgentTemplates/AgentGitHub_2_BAU.json", [cluster_elec, cluster_heat])
world.agent_generation(165, "lib/AgentTemplates/AgentTemplates/AgentGitHub_5_BAU.json", [cluster_elec, cluster_heat])

# DLC contracts
world.agent_generation(200, "lib/AgentTemplates/AgentTemplates/AgentGitHub_1_DLC.json", [cluster_elec, cluster_heat])
world.agent_generation(400, "lib/AgentTemplates/AgentTemplates/AgentGitHub_2_DLC.json", [cluster_elec, cluster_heat])
world.agent_generation(200, "lib/AgentTemplates/AgentTemplates/AgentGitHub_5_DLC.json", [cluster_elec, cluster_heat])

# Curtailment contracts
world.agent_generation(135, "lib/AgentTemplates/AgentTemplates/AgentGitHub_1_curtailment.json", [cluster_elec, cluster_heat])
world.agent_generation(270, "lib/AgentTemplates/AgentTemplates/AgentGitHub_2_curtailment.json", [cluster_elec, cluster_heat])
world.agent_generation(135, "lib/AgentTemplates/AgentTemplates/AgentGitHub_5_curtailment.json", [cluster_elec, cluster_heat])


# ##############################################################################################
# Creation of daemons

# Price Managers
# this daemons fix a price for a given nature of energy
price_manager_elec = User.Daemons.PriceManagerDaemonTOU.PriceManagerDaemonTOU("Picsou", 1, {"nature": elec.name, "buying_prices": [0.12, 0.17], "selling_prices": [0.11, 0.11], "hours": [[6, 12], [14, 23]]})  # sets prices for flat rate
price_elec_grid = User.Daemons.GridPricesDaemon.GridPricesDaemon("LVE_tariffs", 1, {"nature": elec.name, "grid_buying_price": 0.2, "grid_selling_price": 0.05})  # sets prices for the system operator
price_heat_grid = User.Daemons.GridPricesDaemon.GridPricesDaemon("Heat_tariffs", 1, {"nature": heat.name, "grid_buying_price": 0.10, "grid_selling_price": 0.08})  # sets prices for the system operator
world.register_daemon(price_manager_elec)  # registration
world.register_daemon(price_elec_grid)  # registration
world.register_daemon(price_heat_grid)  # registration

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = User.Daemons.IndoorTemperatureDaemon.IndoorTemperatureDaemon("Asie", 1)
world.register_daemon(indoor_temperature_daemon)  # registration

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
temperature_daemon = User.Daemons.OutdoorTemperatureDaemon.OutdoorTemperatureDaemon("Azzie", 1, {"file": "lib/MeteorologicalData/TemperaturesProfiles/TemperatureProfiles.json"})
world.register_daemon(temperature_daemon)  # registration

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = User.Daemons.ColdWaterDaemon.ColdWaterDaemon("Mephisto", 1)
world.register_daemon(water_temperature_daemon)  # registration

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = User.Daemons.IrradiationDaemon.IrradiationDaemon("Pau")
world.register_daemon(irradiation_daemon)  # registration

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = User.Daemons.WindDaemon.WindDaemon("Pau")
world.register_daemon(wind_daemon)  # registration


# ##############################################################################################
# Creation of dataloggers

# datalogger used to get back producer outputs
producer_datalogger = Datalogger(world, "producer_datalogger", "ProducerBalances.txt", 1)
world.register_datalogger(producer_datalogger)  # registration

producer_datalogger.add(f"{PV_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{DHN_producer.name}.Heat.energy_erased")
producer_datalogger.add(f"{WT_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{PV_producer.name}.LVE.energy_sold")
producer_datalogger.add(f"{DHN_producer.name}.Heat.energy_sold")
producer_datalogger.add(f"{WT_producer.name}.LVE.energy_sold")

# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  cluster
cluster_balances = User.Dataloggers.Balances.ClusterBalanceDatalogger()
nature_balances = User.Dataloggers.Balances.NatureBalanceDatalogger()
world.register_datalogger(cluster_balances)  # registration
world.register_datalogger(nature_balances)  # registration


# ##############################################################################################
# here we have the possibility to save the world to use it later
# world.save()  # saving the world


# ##############################################################################################
# Simulation start
world.start()

