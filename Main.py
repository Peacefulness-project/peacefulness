

from common.Core import World

from common.Catalog import Catalog

from common.lib.DummyEntity import DummyConsumer, DummyProducer

from common.Datalogger import Datalogger



data = Catalog()
data.add("Version","0.0")


# Creation of the world
world = World("Earth", data)

world.catalog.print_debug()

print(world)


e1 = DummyConsumer("Essai")
c1 = DummyProducer("Toto")

print(e1)
print(c1)

world.catalog.print_debug()


world.add(e1)
world.add(c1)

logger = Datalogger(world.catalog, "essai.txt",2)
logger2 = Datalogger(world.catalog, "essai2.txt",20)


world.catalog.add("Toto",12)
world.catalog.add("Lolo",14)

world.catalog.print_debug()

logger.add("time")
logger.add_all()


logger2.add("time")
logger2.add("Toto")


for i in range(0,100,1):
    world.catalog.set("time",i)
    print(i)
    logger.process(i)
    logger2.process(i)



print(world)








