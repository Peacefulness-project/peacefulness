# this sheet is the main for supervision
# it is integrated directly in a method of world
# "world" refers to world and "catalog" to his catalog

import common.lib.supervision_tools.supervision as sup

# Resolution

sup.initialize(world, catalog)  # create relevant entries in the catalog

for i in range(0, world.time_limit, 1):
    sup.start_round(world)  # order the devices to update their needs

    sup.make_balance(world, catalog)  # sum the needs and the production for each nature

    for key in world.devices:  # consumption and production balances
        device = world.devices[key]

        for nature in device.natures:
            # consumption balance
            consumption = catalog.get(f"{device.name}.{nature.name}.energy_wanted")

    for nature in world.natures:
        pass  # here, a wonderful calculation takes place
        # results are then written in the catalog
        # for the moment, everyone is satisfied and no balance is made at all

    sup.end_round(world)  # activate the daemons, the dataloggers and increments time


world.catalog.print_debug()  # display the content of the catalog
print(world)  # give the name of the world and the quantity of productions and consumptions



