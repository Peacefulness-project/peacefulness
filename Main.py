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

from common.lib.NatureList import NatureList

from common.ExternalGrid import ExternalGrid

from common.LocalGrid import LocalGrid

from common.Agent import Agent

from common.Cluster import Cluster

from usr.Devices.DummyDevice import DummyConsumption, DummyProduction

from common.Datalogger import Datalogger

from usr.Daemons.DummyDaemon import DummyDaemon

# ##############################################################################################
# Minimum
# the following objects are necessary for the simulation to be performed
# you need exactly one object of each type
# ##############################################################################################

# ##############################################################################################
# Creation of the world
# a world <=> a case, it contains all the model
# a world needs just a name
name_world = "Earth"
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
name_supervisor = "glaDOS"
supervisor = Supervisor(name_supervisor, "DummySupervisorMain.py")
supervisor.description = "this supervisor is a really basic one. It just serves as a " \
                         "skeleton/example for your (more) clever supervisor."
world.register_supervisor(supervisor)


# ##############################################################################################
# Nature list
# this object defines the different natures present in world
# some are predefined but it is possible to create user-defined natures
nature = NatureList()  # creation of a nature
name_new_nature = "Orgone"
nature.add(name_new_nature, "mysterious organic energy")  # Optional addition of a new energy nature
world.set_natures(nature)  # registration


# ##############################################################################################
# Time Manager
# this object manages the two times (physical and iteration)
# it needs a start date, the value of an iteration in s and the total number of iterations
start_date = datetime.datetime.now()  # a start date in the datetime format
world.set_time_manager(start_date, 1, 24)  #

# ##############################################################################################
# Model
# the following objects are the one describing the case studied
# you need at least one local grid and one agent to create a device
# no matter the type, you can create as much objects as you want
# ##############################################################################################

# ##############################################################################################
# Local grid
# this object represents the grids inside wolrd
# it allows to define who is able to exchange with who
name_local_grid_elec = "Enedis"
local_grid_elec = LocalGrid(name_local_grid_elec, "LVE")  # creation
world.register_local_grid(local_grid_elec)  # registration


# ##############################################################################################
# External grid
# this object represents grids outside world which interact with it
name_external_grid = "RTE"
external_grid_elec = ExternalGrid(name_external_grid, "LVE", name_local_grid_elec)  # creation
world.register_external_grid(external_grid_elec)  # registration


# ##############################################################################################
# Agent
# this object represents the owner of devices
# all devices need an agent
name_agent = "James Bond"
agent = Agent(name_agent)  # creation of an agent
world.register_agent(agent)  # registration

name_elec_contract = "contrat classique"
agent.set_contract("LVE", name_elec_contract)  # definition of a contract


# ##############################################################################################
# Cluster
# this object is a collection of devices wanting to isolate themselves as much as they can
# clusters need 2 arguments: a name and a nature of energy
name_cluster = "general cluster"
cluster = Cluster(name_cluster, "LVE", name_local_grid_elec)  # creation of a cluster
world.register_cluster(cluster)  # registration


# ##############################################################################################
# Devices
# these objects regroup production, consumption, storage and transformation devices
# they at least need a name and a nature
# some devices are pre-defined (such as PV) but user can add some by creating new classes in lib

# creation of our devices
consumptionInputFile="usr/Devices/DummyLoadProfile.input"
e1 = DummyConsumption("Essai", name_local_grid_elec, name_agent, consumptionInputFile, name_cluster)  # creation of a consumption point
c1 = DummyProduction("Toto", name_local_grid_elec, name_agent, name_cluster)  # creation of a production point
# the nature of these dummy devices is LVE by definition

print(e1)  # displays the name and the type of the device
print(c1)  # displays the name and the type of the device
world.catalog.print_debug()  # displays the content of the catalog

# registration of our devices
# note that the same method is used for all kind of devices
world.register_device(e1)  # registration of a consumption device
world.register_device(c1)  # registration of a production device

world.catalog.print_debug()  # displays the content of the catalog

# there is another way to create devices using a class method "mass_create"
# this method is user-defined for each specific device
# it takes 3 arguments: the number of devices, a root name for the devices ( "root name"_"number")
# and a world to be registered in
DummyConsumption.mass_create(10, "conso", world, name_local_grid_elec, name_agent, consumptionInputFile)  # creation and registration of
# 10 dummy consumptions
DummyProduction.mass_create(10, "prod", world, name_local_grid_elec, name_agent)  # creation and registration of
# 10 dummy productions


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
dem = DummyDaemon("MonDemonDeMidi", 10)  # creation
world.register_daemon(dem)  # registration


# ##############################################################################################
# Work in progress
# here begins the supervision, which is not implemented yet

world.start()

