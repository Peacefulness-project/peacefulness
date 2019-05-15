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
import datetime

from common.Core import World

from common.Catalog import Catalog

from common.Supervisor import Supervisor

from common.Nature import Nature

from common.Agent import Agent

from common.Cluster import Cluster

from usr.Devices.DummyDevice import DummyConsumption, DummyShiftableConsumption, DummyAdjustableConsumption, DummyProduction

from common.Datalogger import Datalogger

from usr.Daemons.DummyDaemon import DummyDaemon
from usr.Daemons.DissatisfactionErosion import DissatisfactionErosionDaemon

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
# Creation of a data catalog
# this object is a dictionary where goes all data needing to be seen by several objects
data = Catalog()  # creation
data.add("Version", "0.0")  # General information
world.set_catalog(data)  # registration

world.catalog.print_debug()  # displays the content of the catalog
print(world)


# ##############################################################################################
# Definition of the path to the files
pathExport = "./Results"  #
world.set_directory(pathExport)  # registration


# ##############################################################################################
# Supervisor --> il est en stand-by
# this object contains just the path to  your supervisor script and a brief description of what it does


# TODO -> PAS BEAU -> ATTENDRE LA REFONTE DE LA PARTIE SUPERVISEUR

description = "this supervisor is a really basic one. It just serves as a " \
              "skeleton/example for your (more) clever supervisor."
name_supervisor = "glaDOS"
supervisor = Supervisor(name_supervisor, "DummySupervisorMain.py", description)

world.register_supervisor(supervisor)


# ##############################################################################################
# Time Manager
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime.datetime.now()  # a start date in the datetime format
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
# Nature list
# this object represents a nature of energy present in world
Elec = Nature("LVE")  # creation of a nature
Elec.add_description("Low Voltage Electricity")  # Optional description of the nature
world.register_nature(Elec)  # registration


# ##############################################################################################
# Agent
# this object represents the owner of devices
# all devices need an agent
agent = Agent("James Bond")  # creation of an agent
world.register_agent(agent)  # registration

name_elec_contract = "contrat classique"
agent.set_contract(Elec, name_elec_contract)  # definition of a contract


# ##############################################################################################
# Cluster
# this object is a collection of devices wanting to isolate themselves as much as they can
# clusters need 2 arguments: a name and a nature of energy
# there is also a third argument to precise if the cluster is considered as an infinite grid
cluster = Cluster("general cluster", Elec)  # creation of a cluster
world.register_cluster(cluster)  # registration

# here we add a grid, which represents an infinite producer
elec_grid = Cluster("Enedis", Elec, True)
world.register_cluster(elec_grid)  # registration

# ##############################################################################################
# Devices
# these objects regroup production, consumption, storage and transformation devices
# they at least need a name and a nature
# some devices are pre-defined (such as PV) but user can add some by creating new classes in lib

# creation of our devices
consumption_input_file = "usr/Datafiles/DummyBaseloadProfile.input"
e1 = DummyConsumption("Essai", agent, consumption_input_file, cluster)  # creation of a consumption point
production_input_file = "usr/Datafiles/DummyProductionProfile.input"
c1 = DummyProduction("Toto", agent, production_input_file, cluster)  # creation of a production point

# TODO: Créer les classes de base
# shiftable device
shiftable_consumption_input_file = "usr/Datafiles/DummyShiftableLoadProfile.input"
e2 = DummyShiftableConsumption("Dishwasher", agent, shiftable_consumption_input_file, cluster)  # creation of a consumption point
# adjustable device
adjustable_consumption_input_file = "usr/Datafiles/DummyAdjustableLoadProfile.input"
e3 = DummyAdjustableConsumption("Heating", agent, adjustable_consumption_input_file, cluster)  # creation of a consumption point

# the nature of these dummy devices is LVE by definition

# print(e1)  # displays the name and the type of the device
# print(c1)  # displays the name and the type of the device
world.catalog.print_debug()  # displays the content of the catalog

# registration of our devices
# note that the same method is used for all kind of devices
world.register_device(e1)  # registration of a consumption device
world.register_device(e2)  # registration of a consumption device
world.register_device(e3)  # registration of a consumption device
world.register_device(c1)  # registration of a production device

# world.catalog.print_debug()  # displays the content of the catalog

# there is another way to create devices using a class method "mass_create"
# this method is user-defined for each specific device
# it takes 3 more arguments: the number of devices, a root name for the devices (name = "root name"_"number")
# and a world to be registered in
DummyConsumption.mass_create(10, "conso", world, agent, consumption_input_file, elec_grid)
# creation and registration of 10 dummy consumptions
DummyProduction.mass_create(10, "prod", world, agent, production_input_file, cluster)
# creation and registration of 10 dummy productions


# ##############################################################################################
# Dataloggers
# this object is in charge of exporting data into files at a given iteration frequency

# dataloggers need at least 3 arguments: a name, a file name and a period of activation
# the first logger writes all the available data at each turn
logger = Datalogger("log2", "essai.txt", 1)  # creation
world.register_datalogger(logger)  # registration
logger.add_all()  # this datalogger exports all the data available in the catalog

# the second logger writes only time and Toto every 20 turns
# as it is not activated for each turn, it will return, for each numerical data,
# the mean, the min and the max between two activations
# the 4th argument is a boolean: if it is true, the datalogger will integrate the data between two activations
logger2 = Datalogger("log10", "essai2.txt", 20, 1)  # creation
world.register_datalogger(logger2)  # registration
logger2.add("simulation_time")  # this datalogger exports only the current iteration


# ##############################################################################################
# Daemons
# this object updates entries of the catalog which do not belong to any other object
# as an example, it can update some meteorological data

# daemons need 2 arguments: a name and a period of activation
daemon = DummyDaemon("MonDemonDeMidi", 10)  # creation
world.register_daemon(daemon)  # registration

# dissatisfaction erosion
# this daemon reduces slowly the dissatisfaction of all agents over the time
# here it is set like this: 10% of dissatisfaction will remain after one week (168 hours) has passed
dissatisfaction_management = DissatisfactionErosionDaemon("DissatisfactionErosion", 1, 0.9, 168)  # creation
world.register_daemon(dissatisfaction_management)  # registration


# ##############################################################################################
# Work in progress
# here begins the supervision, which is not implemented yet

world.start()

