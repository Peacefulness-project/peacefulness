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
from common.Core import World

from common.Catalog import Catalog

from common.lib.DummyDevice import DummyConsumption, DummyProduction

from common.Datalogger import Datalogger

from common.CaseDirectory import CaseDirectory

from common.TimeManager import TimeManager

from common.lib.EnergyTypes import NatureList

from usr.DummyDaemon import DummyDaemon

from common.Agent import Agent

from common.Cluster import Cluster


# ##############################################################################################
# Creation of the world
# a world needs just a name
world = World("Earth")  # creation


# ##############################################################################################
# Creation of a data catalog
data = Catalog()  # creation
data.add("Version", "0.0")  # General information
world.set_catalog(data)  # registration

world.catalog.print_debug()  # displays the content of he catalog
print(world)


# ##############################################################################################
# Case Directory
directory = CaseDirectory("./Results")  # creation
world.set_directory(directory)  # registration


# ##############################################################################################
# Time Manager
time_manager = TimeManager()  # creation
world.set_time_manager(time_manager)  # registration


# ##############################################################################################
# Nature list
nature = NatureList()  # creation of a nature
nature.add("Orgone", "mysterious organic energy")  # Optional addition of new energy natures
world.set_natures(nature)  # registration


# ##############################################################################################
# Devices
# creation of our devices
e1 = DummyConsumption("Essai")  # creation of a consumption point
c1 = DummyProduction("Toto")  # creation of a production point

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
DummyConsumption.mass_create(10, "conso", world)  # creation and registration of 10 dummy consumptions
DummyProduction.mass_create(10, "prod", world)  # creation and registration of 10 dummy productions


# ##############################################################################################
# Cluster
# clusters need 2 arguments: a name and a nature of energy
cluster_general = Cluster("cluster general", "LVE")  # creation of a cluster
world.register_cluster(cluster_general)  # registration
world.link_cluster("cluster general", ["Essai", "Toto"])  # link between the cluster and devices


# ##############################################################################################
# Agent
pollueur1 = Agent("pollueur 1")  # creation of an agent
pollueur1.set_contract("LVE", "contrat classique")  # definition of a contract

world.register_agent(pollueur1)  # registration
world.link_agent("pollueur 1", world._productions)  # link between the agent and devices
world.link_agent("pollueur 1", world._consumptions)  # link between the agent and devices


# ##############################################################################################
# Dataloggers
# dataloggers need 3 arguments: a name, a file name and a period of activation

# the first logger writes all the available data at each turn
logger = Datalogger("log2", "essai.txt", 2)  # creation
world.register_datalogger(logger)  # registration
logger.add_all()  # this datalogger exports all the data available in the catalog

# the second logger writes only time and Toto every 20 turns
logger2 = Datalogger("log10", "essai2.txt", 20, 1)  # creation
world.register_datalogger(logger2)  # registration
logger2.add("simulation_time")  # this datalogger exports only the current iteration


# ##############################################################################################
# Daemons
# daemons need 2 arguments: a name and a period of activation
dem = DummyDaemon("MonDemonDeMidi", 10)  # creation
world.register_daemon(dem)  # registration


# ##############################################################################################
# Work in progress

world.check()  # check if everything is fine in world definition

for i in range(0, 100, 1):  # a little test to verify that everything goes well
    world.next()  # activates the daemons, the dataloggers and the time manager

print(world)  # gives the name of the world and the quantity of producers and consumers
