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

from common.lib.DummyEntity import DummyConsumer, DummyProducer

from common.Datalogger import Datalogger


# Creation of a data catalog
data = Catalog()
data.add("Version", "0.0")


# Creation of the world
# a world needs a name and a data catalog
world = World("Earth", data)

world.catalog.print_debug()

print(world)

# Creation of our entities
# They need at least a name
# Later, some more specific entities could require more information
e1 = DummyConsumer("Essai")
c1 = DummyProducer("Toto")

print(e1)
print(c1)

world.catalog.print_debug()

# Addition of our entities to our world
world.add(e1)
world.add(c1)

world.catalog.add("Toto", 12)
world.catalog.add("Lolo", 14)

world.catalog.print_debug()

# Creation of the dataloggers, which write desired data in a file
# A datalogger needs a catalog, a filename and, optionally, a writing frequency
logger = Datalogger(world.catalog, "essai.txt", 2)
logger2 = Datalogger(world.catalog, "essai2.txt", 20)

logger.add("time")
logger.add_all()

logger2.add("time")
logger2.add("Toto")


for i in range(0, 100, 1):
    world.catalog.set("time", i)
    logger.process(i)
    logger2.process(i)

print(world)