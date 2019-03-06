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


from common.Core import World

from common.Catalog import Catalog

from common.lib.DummyEntity import DummyConsumption, DummyProduction

from common.Datalogger import Datalogger

from common.CaseDirectory import CaseDirectory

# from tools.DataProcessingFunctions import dummy_data_function

from usr.DummyDaemon import DummyDaemon

from usr.DummySupervisor import DummySupervisor

# Creation of the case directory
directory = CaseDirectory("./Results")
directory.create()

# Creation of a data catalog
data = Catalog()
data.add("Version", "0.0")


# Creation of the world
# a world needs a name and a data catalog
world = World("Earth", data)

world.catalog.print_debug()  # displays the content of he catalog

print(world)

# Creation of our entities
# They need at least a name
# Later, some more specific entities could resquire more information
e1 = DummyConsumption("Essai")
c1 = DummyProduction("Toto")

print(e1)  # displays the name and the type of the entity
print(c1)  # displays the name and the type of the entity

world.catalog.print_debug()  # displays the content of he catalog

# Addition of our entities to our world
world.add(e1)  # linking the consumer with the world
world.add(c1)  # linking the producer with the world

world.catalog.add("Le chef", "Erwin!")
world.catalog.add("Toto", 12.)
world.catalog.add("Lolo", 14.)

world.catalog.print_debug()  # displays the content of he catalog

DummyConsumption.mass_create(10, "conso", world)  # creation of ten dummy consumers
DummyProduction.mass_create(10, "prod", world)  # creation of ten dummy producers

# Creation of the dataloggers, which write desired data in a file
# A datalogger needs a catalog, a filename and, optionally, a writing frequency

# the first logger writes all the available data at each turn
logger = Datalogger("log2", "essai.txt", 2)
world.register_datalogger(logger)  # linking the datalogger with the world
logger.add_all()
logger.set_path(directory)

# the second logger writes only time and Toto every 20 turns
logger2 = Datalogger("log10", "essai2.txt", 20, 1)
world.register_datalogger(logger2)  # linking the datalogger with the world
logger2.add("simulation_time")
logger2.add("Toto")
logger2.set_path(directory)

# first daemon
dem = DummyDaemon("MonDemonDeMidi", 10)

world.register_daemon(dem)  # linking the daemon with the world

for i in range(0, 100, 1):  # a little test to verify that dataloggers work
    world.next()  # activates the daemons, the dataloggers and manages time

print(world)  # gives the name of the world and the quantity of producers and consumers
