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
name_world = "Disc World"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
pathExport = "./Results"  #
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
               24)  # number of time steps simulated

# ##############################################################################################
# Model
# the following objects are the one describing the case studied
# you need at least one local grid and one agent to create a device
# no matter the type, you can create as much objects as you want
# ##############################################################################################

# ##############################################################################################
# Supervisor
# this object defines a strategy of supervision through 3 steps: local distribution, formulation of its needs, remote distribution
description = "this supervisor is a really basic one. It just serves as a " \
              "skeleton/example for your (more) clever supervisor."
name_supervisor = "glaDOS"
supervisor = User.Supervisors.AlwaysSatisfied.AlwaysSatisfied(name_supervisor, description)
world.register_supervisor(supervisor)

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

nature_name = "DHW"
nature_description = "Energy used to heat Domestic Hot Water"
DHW = Nature(nature_name, nature_description)  # creation of a nature
world.register_nature(DHW)  # registration


# ##############################################################################################
# Cluster
# this object is a collection of devices wanting to isolate themselves as much as they can
# clusters need 2 arguments: a name and a nature of energy
# there is also a third argument to precise if the cluster is considered as an infinite grid

# and then we create a third who represents the grid
cluster_name = "Enedis"
cluster_grid = Cluster(cluster_name, elec, grid_supervisor)
world.register_cluster(cluster_grid)  # registration

# and then we create a third who represents the grid
cluster_name = "Important_source_of_heat_power_for_heating"
cluster_grid_heat = Cluster(cluster_name, heat, grid_supervisor)
world.register_cluster(cluster_grid_heat)  # registration

# and then we create a third who represents the grid
cluster_name = "Important_source_of_heat_power_for_DHW"
cluster_grid_DHW = Cluster(cluster_name, DHW, grid_supervisor)
world.register_cluster(cluster_grid_DHW)  # registration

# here we create a first cluster dedicated to electricity
cluster_name = "elec_mesh"
sup_cluster_elec = Cluster(cluster_name, elec, supervisor, cluster_grid)
world.register_cluster(sup_cluster_elec)  # registration

# here we create a second one put under the orders of the first
cluster_name = "general_cluster"
cluster_elec = Cluster(cluster_name, elec, supervisor, sup_cluster_elec)  # creation of a cluster
world.register_cluster(cluster_elec)  # registration

# here we create another cluster dedicated to heat
cluster_name = "Local_DHN"
cluster_heat = Cluster(cluster_name, heat, supervisor, cluster_grid_heat)  # creation of a cluster
world.register_cluster(cluster_heat)  # registration

# here we create another cluster dedicated to heat
cluster_name = "Local_DHW_network"
cluster_DHW = Cluster(cluster_name, DHW, supervisor, cluster_grid_DHW)  # creation of a cluster
world.register_cluster(cluster_DHW)  # registration


# ##############################################################################################
# Contracts
# this object has 3 roles: managing the dissatisfaction, managing the billing and defining the operations allowed to the supervisor
# contracts have to be defined for each nature for each agent BUT are not linked initially to a nature
classic_contract_elec = User.Contracts.TOUEgoistContract.TOUEgoistContract("classic_contract_elec", elec, {"selling_price": 0.1, "buying_price": 0.05})
world.register_contract(classic_contract_elec)

cooperative_contract_elec = User.Contracts.TOUCooperativeContract.TOUCooperativeContract("cooperative_contract_elec", elec, {"selling_price": 0.1, "buying_price": 0.05})
world.register_contract(cooperative_contract_elec)

classic_contract_heat = User.Contracts.TOUEgoistContract.TOUEgoistContract("classic_contract_heat", heat, {"selling_price": 0.1, "buying_price": 0.05})
world.register_contract(classic_contract_heat)

classic_contract_DHW = User.Contracts.TOUEgoistContract.TOUEgoistContract("classic_contract_DHW", DHW, {"selling_price": 0.1, "buying_price": 0.05})
world.register_contract(classic_contract_DHW)


# ##############################################################################################
# Agent
# this object represents the owner of devices
# all devices need an agent
agent = Agent("James Bond")  # creation of an agent
world.register_agent(agent)  # registration

agent.set_contract(elec, classic_contract_elec)
agent.set_contract(heat, classic_contract_heat)


# ##############################################################################################
# Devices
# these objects regroup production, consumption, storage and transformation devices
# they at least need a name and a nature
# some devices are pre-defined (such as PV) but user can add some by creating new classes in lib

# creation of our devices
# basic device
Light1 = User.Devices.NonControllableDevice.Light.Light("Light_basic", classic_contract_elec, agent, sup_cluster_elec, "residential", "house")  # creation of a consumption point
Light2 = User.Devices.NonControllableDevice.Light.Light("Light_offset", classic_contract_elec, agent, sup_cluster_elec, "offset", "house")  # creation of a consumption point
# shiftable device
e2 = User.Devices.ShiftableDevice.Dishwasher.Dishwasher("Dishwasher1", classic_contract_elec, agent, sup_cluster_elec, "family", "medium_consumption")  # creation of a consumption point
# adjustable device
charger = User.Devices.AdjustableDevice.Charger.Charger("Charger1", classic_contract_elec, agent, sup_cluster_elec, "default", "laptop_charger")
# temperature-related devices are a sub-class of adjustable devices
# these devices need additional parameters to model their physic
e3 = User.Devices.AdjustableDevice.Heating.Heating("Heating1", classic_contract_heat, agent, cluster_heat, "residential", "house_heat")  # creation of a consumption point
# production devices
st = User.Devices.NonControllableDevice.SolarThermalCollector.SolarThermalCollector("solar_captor", classic_contract_heat, agent, cluster_heat, "ECOS", "ECOS", {"surface": 2})  # creation of a solar thermal collector
c1 = User.Devices.NonControllableDevice.PV.PV("PV", classic_contract_elec, agent, sup_cluster_elec, "ECOS", "ECOS", {"surface": 2})  # creation of a photovoltaic panel


world.catalog.print_debug()  # displays the content of the catalog

# registration of our devices
# note that the same method is used for all kind of devices
world.register_device(Light1)  # registration of a consumption device
world.register_device(Light2)  # registration of a consumption device
world.register_device(charger)  # registration of a consumption device
world.register_device(e2)  # registration of a consumption device
world.register_device(e3)  # registration of a consumption device
world.register_device(c1)  # registration of a production device
world.register_device(st)  # registration of a production device


# Performance measurement
CPU_time_generation_of_device = process_time()
# the following method create "n" agents with a predefined set of devices based on a JSON file
world.agent_generation(10, "usr/AgentTemplates/DummyAgent.json", [cluster_elec, cluster_heat])
world.agent_generation(30, "usr/AgentTemplates/EgoistFamily.json", cluster_elec)
world.agent_generation(30, "usr/AgentTemplates/EgoistSingle.json", cluster_elec)
world.agent_generation(30, "usr/AgentTemplates/CooperativeSingle.json", cluster_elec)
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
dissatisfaction_management = User.Daemons.DissatisfactionErosionDaemon.DissatisfactionErosionDaemon("DissatisfactionErosion", 1, {"coef_1": 0.9, "coef_2": 168})  # creation
world.register_daemon(dissatisfaction_management)  # registration

# Price Managers
# this daemon fixes a price for a given nature of energy
price_manager_elec = User.Daemons.PriceManagerDaemon.PriceManagerDaemon("Picsou", 1, {"nature": elec.name, "buying_price": 0.1, "selling_price": 0.05})  # sets prices for flat rate
price_manager_heat = User.Daemons.PriceManagerDaemon.PriceManagerDaemon("Flairsou", 1, {"nature": heat.name, "buying_price": 0.1, "selling_price": 0.05})  # sets prices fro flat rate
price_elec_grid = User.Daemons.GridPricesDaemon.GridPricesDaemon("EDF_tariffs", 1, {"nature": elec.name, "grid_buying_price": 0.05, "grid_selling_price": 0.15})  # sets prices for the system operator
price_heat_grid = User.Daemons.GridPricesDaemon.GridPricesDaemon("DHN_tariffs", 1, {"nature": heat.name, "grid_buying_price": 0.05, "grid_selling_price": 0.15})  # sets prices for the system operator
price_DHW_grid = User.Daemons.GridPricesDaemon.GridPricesDaemon("DHW_tariffs", 1, {"nature": DHW.name, "grid_buying_price": 0.05, "grid_selling_price": 0.15})  # sets prices for the system operator
world.register_daemon(price_manager_elec)  # registration
world.register_daemon(price_manager_heat)  # registration
world.register_daemon(price_elec_grid)  # registration
world.register_daemon(price_heat_grid)  # registration
world.register_daemon(price_DHW_grid)  # registration

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
temperature_daemon = User.Daemons.PauTemperatureDaemon.PauTemperatureDaemon("Azzie", 1)
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

# dataloggers need at least 3 arguments: a name, a file name and a period of activation
# the first logger writes all the available data at each turn
logger = Datalogger("log2", "essai.txt", 1)  # creation
world.register_datalogger(logger)  # registration
logger.add_all()  # this datalogger exports all the data available in the catalog

# the second logger writes only time and Toto every 20 turns
# as it is not activated for each turn, it will return, for each numerical data,
# the mean, the min and the max between two activations
# the 4th argument is a boolean: if it is true, the datalogger will integrate the data between two activations
logger2 = Datalogger("log10", "essai2.txt", 1, 1)  # creation
world.register_datalogger(logger2)  # registration
logger2.add("simulation_time")  # this datalogger exports only the current iteration
logger2.add("physical_time")


# datalogger for balances
# these dataloggers record the balances for each agent, contract, nature and  cluster
contract_balances = User.Dataloggers.Balances.ContractBalanceDatalogger()
cluster_balances = User.Dataloggers.Balances.ClusterBalanceDatalogger()
agent_balances = User.Dataloggers.Balances.AgentBalanceDatalogger()
nature_balances = User.Dataloggers.Balances.NatureBalanceDatalogger()
ECOS_datalogger = User.Dataloggers.ECOS.ECOS()

world.register_datalogger(contract_balances)  # registration
world.register_datalogger(cluster_balances)  # registration
world.register_datalogger(agent_balances)  # registration
world.register_datalogger(nature_balances)  # registration
world.register_datalogger(ECOS_datalogger)  # registration


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










