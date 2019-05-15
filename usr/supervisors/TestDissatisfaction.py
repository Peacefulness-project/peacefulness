# this sheet is the main for supervision
# it is integrated directly in a method of world
# "world" refers to world and "catalog" to his catalog

import common.lib.supervision_tools.supervision as sup

# Resolution

sup.initialize(world, catalog)  # create relevant entries in the catalog

for i in range(0, world.time_limit, 1):
    sup.start_round(world)  # order the devices to update their needs

    sup.make_balance(world, catalog)  # sum the needs and the production for each nature

    # as long as the priority is not maximal, the device won't be served
    # this way, some dissatisfaction is supposed to appear
    for device in world.devices:
        if world.catalog.get(f"{world.devices[device].name}.priority") < 1:
            for nature in world.devices[device].natures:
                catalog.set(f"{device}.{nature.name}.asked_energy", 0)

    sup.end_round(world)  # activate the daemons, the dataloggers and increments time


world.catalog.print_debug()  # display the content of the catalog


