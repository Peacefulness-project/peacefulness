# first run for SFT 2020
# Control simulation: everything goes as actually in France. This run will give us a reference to measure the efficiency of our method.
# Exchange strategy: BAU
# Distribution strategy: N.A
# Contracts: 100 Normal, 0 DLC, 0 Curtailment


# ##############################################################################################
# Importations
from datetime import datetime

from time import process_time

from tools.Utilities import adapt_path

from common.Core import World

from common.Supervisor import Supervisor

from common.Nature import Nature

from common.Agent import Agent

from common.Cluster import Cluster

from common.Datalogger import Datalogger

import usr.UserDefinedClasses as User


# ##############################################################################################
# Performance measurement
CPU_time = process_time()

# ##############################################################################################
# Minimum
# the following objects are necessary for the simulation to be performed
# you need exactly one object of each type
# ##############################################################################################

# ##############################################################################################
# Creation of the world
# a world <=> a case, it contains all the model
# a world needs just a name
name_world = "ECOS_collab_2020"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
pathExport = "published_cases/ECOS_collab_2020/Results/Profitable_high_DSM_mean"
world.set_directory(pathExport)  # registration


# ##############################################################################################
# Definition of the random seed to be used
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("tournesol")


# ##############################################################################################
# Time Manager
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime.now()  # a start date in the datetime format
start_date = start_date.replace(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24*365+1)  # number of time steps simulated

# ##############################################################################################
# Model
# the following objects are the one describing the case studied
# you need at least one local grid and one agent to create a device
# no matter the type, you can create as much objects as you want
# ##############################################################################################

# ##############################################################################################
# Supervisor
# this object defines a strategy of supervision through 3 steps: local distribution, formulation of its needs, remote distribution
# elec supervisor
description = "Refuses to exchange with outside."
name_supervisor = "NoExchange"
supervisor_elec = User.Supervisors.WhenProfitableEmergency.WhenProfitableEmergency(name_supervisor, description)
world.register_supervisor(supervisor_elec)

# the heat supervisor
description = "Always serves everybody, whatever it can cost to him."
name_supervisor = "heat_supervisor"
supervisor_heat = User.Supervisors.SubclusterHeatEmergency.SubclusterHeatEmergency(name_supervisor, description)
world.register_supervisor(supervisor_heat)

# the supervisor grid, which always proposes an infinite quantity to sell and to buy
description = "this supervisor represents the ISO. Here, we consider that it has an infinite capacity to give or to accept energy"
name_supervisor = "benevolent_operator"
grid_supervisor = User.Supervisors.Grid.Grid(name_supervisor, description)
world.register_supervisor(grid_supervisor)

# ##############################################################################################
# Nature list
# this object represents a nature of energy present in world
nature_name = "LVE"
nature_description = "Low Voltage Electricity"
elec = Nature(nature_name, nature_description)  # creation of a nature
world.register_nature(elec)  # registration

nature_name = "Heat"
nature_description = "Energy transported by a district heating network"
heat = Nature(nature_name, nature_description)  # creation of a nature
world.register_nature(heat)  # registration

# ##############################################################################################
# Cluster
# this object is a collection of devices wanting to isolate themselves as much as they can
# clusters need 2 arguments: a name and a nature of energy
# there is also a third argument to precise if the cluster is considered as an infinite grid

# and then we create a third who represents the grid
cluster_name = "Enedis"
cluster_grid = Cluster(cluster_name, elec, grid_supervisor)
world.register_cluster(cluster_grid)  # registration

# here we create a second one put under the orders of the first
cluster_name = "general_cluster"
cluster_elec = Cluster(cluster_name, elec, supervisor_elec, cluster_grid, 1, 100000)  # creation of a cluster
world.register_cluster(cluster_elec)  # registration

# here we create another cluster dedicated to heat
cluster_name = "Local_DHN"
cluster_heat = Cluster(cluster_name, heat, supervisor_heat, cluster_elec, 3.6, 3000)  # creation of a cluster
world.register_cluster(cluster_heat)  # registration


# ##############################################################################################
# Contracts
# this object has 3 roles: managing the dissatisfaction, managing the billing and defining the operations allowed to the supervisor
# contracts have to be defined for each nature for each agent BUT are not linked initially to a nature

# producers
# as we consider that they are the same as the supervisor, we chose to put all their prices to 0
BAU_elec = User.Contracts.TOUEgoistContract.TOUEgoistContract("BAU_elec", elec, {"selling_price": 0, "buying_price": 0})
world.register_contract(BAU_elec)

BAU_heat = User.Contracts.FlatEgoistContract.FlatEgoistContract("BAU_heat", heat, {"selling_price": 0, "buying_price": 0})
world.register_contract(BAU_heat)

# cooperative_contract_elec = User.Contracts.FlatCooperativeContract.FlatCooperativeContract("cooperative_contract_elec", elec, {"selling_price": 0.1, "buying_price": 0.12})
# world.register_contract(cooperative_contract_elec)

cooperative_contract_heat = User.Contracts.FlatCooperativeContract.FlatCooperativeContract("cooperative_contract_heat", heat, {"selling_price": 0, "buying_price": 0})
world.register_contract(cooperative_contract_heat)

# ##############################################################################################
# Agent
# this object represents the owner of devices
# all devices need an agent
PV_producer = Agent("PV_producer")  # creation of an agent
world.register_agent(PV_producer)  # registration
PV_producer.set_contract(elec, BAU_elec)

solar_thermal_collector_producer = Agent("solar_thermal_producer")  # creation of an agent
world.register_agent(solar_thermal_collector_producer)  # registration
solar_thermal_collector_producer.set_contract(heat, BAU_heat)


# ##############################################################################################
# Devices
# these objects regroup production, consumption, storage and transformation devices
# they at least need a name and a nature
# some devices are pre-defined (such as PV) but user can add some by creating new classes in lib
PV_field = User.Devices.NonControllableDevice.PV.PV("PV_field", BAU_elec, PV_producer, cluster_elec, "ECOS", "ECOS_field", {"surface": 18000})  # creation of a photovoltaic panel field
world.register_device(PV_field)  # registration of a production device

solar_thermal_collector_field = User.Devices.NonControllableDevice.SolarThermalCollector.SolarThermalCollector("solar_thermal_collector_field", BAU_heat, solar_thermal_collector_producer, cluster_heat, "ECOS", "ECOS_field", {"surface": 9350})  # creation of a solar thermal collector
world.register_device(solar_thermal_collector_field)  # registration of a production device


# Performance measurement
CPU_time_generation_of_device = process_time()
# the following method create "n" agents with a predefined set of devices based on a JSON file


# BAU contracts
world.agent_generation(165, "usr/AgentTemplates/ECOS2020/AgentECOS_1_BAU.json", [cluster_elec, cluster_heat])
world.agent_generation(330, "usr/AgentTemplates/ECOS2020/AgentECOS_2_BAU.json", [cluster_elec, cluster_heat])
world.agent_generation(165, "usr/AgentTemplates/ECOS2020/AgentECOS_5_BAU.json", [cluster_elec, cluster_heat])

# DLC contracts
world.agent_generation(200, "usr/AgentTemplates/ECOS2020/AgentECOS_1_DLC.json", [cluster_elec, cluster_heat])
world.agent_generation(400, "usr/AgentTemplates/ECOS2020/AgentECOS_2_DLC.json", [cluster_elec, cluster_heat])
world.agent_generation(200, "usr/AgentTemplates/ECOS2020/AgentECOS_5_DLC.json", [cluster_elec, cluster_heat])

# Curtailment contracts
world.agent_generation(135, "usr/AgentTemplates/ECOS2020/AgentECOS_1_curtailment.json", [cluster_elec, cluster_heat])
world.agent_generation(270, "usr/AgentTemplates/ECOS2020/AgentECOS_2_curtailment.json", [cluster_elec, cluster_heat])
world.agent_generation(135, "usr/AgentTemplates/ECOS2020/AgentECOS_5_curtailment.json", [cluster_elec, cluster_heat])

# CPU time measurement
CPU_time_generation_of_device = process_time() - CPU_time_generation_of_device  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the device generation phase: {CPU_time_generation_of_device}\n")
file.close()

# ##############################################################################################
# Daemons
# this object updates entries of the catalog which do not belong to any other object

# dissatisfaction erosion
# this daemon reduces slowly the dissatisfaction of all agents over the time
# here it is set like this: 10% of dissatisfaction will remain after one week (168 hours) has passed
# dissatisfaction_management = User.Daemons.DissatisfactionErosionDaemon.DissatisfactionErosionDaemon("DissatisfactionErosion", 1, {"coef_1": 0.9, "coef_2": 168})  # creation
# world.register_daemon(dissatisfaction_management)  # registration

# Price Managers
# this daemons fix a price for a given nature of energy
price_manager_elec = User.Daemons.PriceManagerDaemonTOU.PriceManagerDaemonTOU("Picsou", 1, {"nature": elec.name, "buying_prices": [0.2125, 0.15], "selling_prices": [0, 0], "hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
price_elec_grid = User.Daemons.GridPricesDaemon.GridPricesDaemon("LVE_tariffs", 1, {"nature": elec.name, "grid_buying_price": 0.2, "grid_selling_price": 0.1})  # sets prices for the system operator
price_heat_grid = User.Daemons.GridPricesDaemon.GridPricesDaemon("Heat_tariffs", 1, {"nature": heat.name, "grid_buying_price": 0.30, "grid_selling_price": 0.00})  # sets prices for the system operator
world.register_daemon(price_manager_elec)  # registration
world.register_daemon(price_elec_grid)  # registration
world.register_daemon(price_heat_grid)  # registration

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
indoor_temperature_daemon = User.Daemons.IndoorTemperatureDaemon.IndoorTemperatureDaemon("Asie", 1)
world.register_daemon(indoor_temperature_daemon)  # registration

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
temperature_daemon = User.Daemons.OutdoorTemperatureDaemon.OutdoorTemperatureDaemon("Azzie", 1, {"file": "usr/MeteorologicalData/TemperaturesProfiles/PauTemperatures.json"})
world.register_daemon(temperature_daemon)  # registration

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = User.Daemons.ColdWaterDaemon.ColdWaterDaemon("Mephisto", 1)
world.register_daemon(water_temperature_daemon)  # registration

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = User.Daemons.IrradiationDaemon.IrradiationDaemon("Pau")
world.register_daemon(irradiation_daemon)  # registration


# ##############################################################################################
# Dataloggers
# this object is in charge of exporting data into files at a given iteration frequency
# world.catalog.print_debug()  # displays the content of the catalog

# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  cluster
contract_balances = User.Dataloggers.Balances.ContractBalanceDatalogger()
cluster_balances = User.Dataloggers.Balances.ClusterBalanceDatalogger()
nature_balances = User.Dataloggers.Balances.NatureBalanceDatalogger()
world.register_datalogger(contract_balances)  # registration
world.register_datalogger(cluster_balances)  # registration
world.register_datalogger(nature_balances)  # registration

ECOS_agent_datalogger = User.Dataloggers.ECOSDatalogger.ECOSAgentDatalogger("month")
ECOS_cluster_datalogger = User.Dataloggers.ECOSDatalogger.ECOSClusterDatalogger()
global_values_datalogger = User.Dataloggers.ECOSDatalogger.GlobalValuesDatalogger()
world.register_datalogger(ECOS_agent_datalogger)  # registration
world.register_datalogger(ECOS_cluster_datalogger)  # registration
world.register_datalogger(global_values_datalogger)  # registration

# datalogger used to get back producer outputs
producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")
world.register_datalogger(producer_datalogger)  # registration

producer_datalogger.add(f"{PV_producer.name}.LVE.energy_erased")
producer_datalogger.add(f"{solar_thermal_collector_producer.name}.Heat.energy_erased")
producer_datalogger.add(f"{PV_producer.name}.LVE.energy_sold")
producer_datalogger.add(f"{solar_thermal_collector_producer.name}.Heat.energy_sold")

producer_datalogger.add(f"{PV_field.name}_exergy_in")
producer_datalogger.add(f"{solar_thermal_collector_field.name}_exergy_in")
producer_datalogger.add(f"{PV_field.name}_exergy_out")
producer_datalogger.add(f"{solar_thermal_collector_field.name}_exergy_out")


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
# Work in progress
# here begins the supervision, which is not implemented yet
CPU_time = process_time()  # CPU time measurement
world.start()

# CPU time measurement
CPU_time = process_time() - CPU_time  # time taken by the initialization
filename = adapt_path([world._catalog.get("path"), "outputs", "CPU_time.txt"])  # adapting the path to the OS
file = open(filename, "a")  # creation of the file
file.write(f"time taken by the calculation phase: {CPU_time}\n")
file.close()










