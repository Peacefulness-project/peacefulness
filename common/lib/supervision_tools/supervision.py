# This sheet serves as a library containing basic functions


# ##########################################################################################
# Initialization
# ##########################################################################################

def initialize(world, catalog):  # initialization of the supervisor by adding entries later used in the catalog

    # for world
    for nature in world.natures:  # these entries correspond to the balance made for each nature
        catalog.add(f"{world.name}_{nature}_consumption_balance", 0)
        catalog.add(f"{world.name}_{nature}_production_balance", 0)

    # for local grids
    for name in world.local_grids:
        catalog.add(f"{name}_consumption_balance", 0)
        catalog.add(f"{name}_production_balance", 0)

    # for agents
    for nature in world.natures:  # these entries correspond to the balance made for each nature
        for name in world.agents:
            catalog.add(f"{name}_{nature}_consumption_balance", 0)
            catalog.add(f"{name}_{nature}_production_balance", 0)

    # for clusters
    for name in world.clusters:
        catalog.add(f"{name}_consumption_balance", 0)
        catalog.add(f"{name}_production_balance", 0)


# ##########################################################################################
# Dynamic behavior
# ##########################################################################################

def start_round(world):  # function updating data to the current timestep

    for key in world.consumptions:
        world._consumptions[key]._update()

    for key in world.productions:
        world._productions[key]._update()

    # for key in world._transformers:
    #     world._transformers[key]._update()
    #
    # for key in world._storage:
    #     world._storage[key]._update()

    for key in world.external_grids:
        world._external_grids[key]._update()

    for key in world.agents:
        world._agents[key]._update()


def end_round(world):  # function incrementing the time step and calling dataloggers and daemons
    # it is called after the resolution of the round

    for key in world.dataloggers:  # activation of the dataloggers, they must be called before the daemons,
        # who may have an impact on data
        world._dataloggers[key]._launch()

    for key in world.daemons:  # activation of the daemons
        world._daemons[key]._launch()

    world._update_time()


def make_balance(world, catalog):  # sum the needs and the production for the world

    # the following variable will account the sums of energy
    world_balance = dict()  # balance for each energy type in world
    local_grid_balance = dict()  # balance for one local grid
    agent_balance = dict()  # balance for each energy type for one agent
    cluster_balance = dict()  # balance for one cluster

    # initialization of the dictionaries
    for nature in world.natures:
        # balance contains the consumption total in first position and the production total in second
        world_balance[nature] = [0, 0]
        agent_balance[nature] = dict()

    for name in world.local_grids:
        local_grid_balance[name] = [0, 0]

    for nature in world.natures:
        for name in world.agents:
            agent_balance[nature][name] = [0, 0]

    for name in world.clusters:
        cluster_balance[name] = [0, 0]

    # balance
    for key in world.consumptions:  # consumption balance for each kind of object
        consumption = world.consumptions[key]
        world_balance[consumption.nature][0] += catalog.get(f"{consumption.name}.energy")
        local_grid_balance[consumption.grid][0] += catalog.get(f"{consumption.name}.energy")
        agent_balance[consumption.nature][consumption.agent][0] += catalog.get(f"{consumption.name}.energy")
        if consumption.cluster is not None:
            cluster_balance[consumption.cluster][0] += catalog.get(f"{consumption.name}.energy")

    for key in world.productions:  # production balance for each kind of object
        production = world.productions[key]
        world_balance[production.nature][1] += catalog.get(f"{production.name}.energy")
        local_grid_balance[production.grid][1] = catalog.get(f"{production.name}.energy")
        agent_balance[production.nature][production.agent][1] += catalog.get(f"{production.name}.energy")
        if production.cluster is not None:  # cluster are optional and so a test is needed
            cluster_balance[production.cluster][1] = catalog.get(f"{production.name}.energy")

    # writing the balance in the catalog
    # for world
    for nature in world.natures:  # saving the balance in the catalog
        catalog.set(f"{world.name}_{nature}_consumption_balance", world_balance[nature][0])
        catalog.set(f"{world.name}_{nature}_production_balance", world_balance[nature][1])

    # for local grids
    for name in world.local_grids:
        catalog.set(f"{name}_consumption_balance", local_grid_balance[name][0])
        catalog.set(f"{name}_production_balance", local_grid_balance[name][1])

    # for agents
    for nature in world.natures:  # saving the balance in the catalog
        for name in world.agents:
            catalog.set(f"{name}_{nature}_consumption_balance", agent_balance[nature][name][0])
            catalog.set(f"{name}_{nature}_production_balance", agent_balance[nature][name][1])

    # for clusters
    for name in world.clusters:
        catalog.set(f"{name}_consumption_balance", cluster_balance[name][0])
        catalog.set(f"{name}_production_balance", cluster_balance[name][1])


def stress_calculus(world, catalog):  # calculus of the stress for each local grid

    stress = dict()  # dictionary containing the stress for each different nature of energy

    for nature in world.natures:
        cons = catalog.get(f"{world.name}_{nature}_consumption_balance")
        prod = catalog.get(f"{world.name}_{nature}_production_balance")

        stress[nature] = cons/prod - prod/cons  # this function has the following behavior:
        # cons/prod --> +inf ==> stress --> +inf
        # cons/prod  =  1    ==> stress  =  1
        # cons/prod --> 0    ==> stress --> -inf
        # but it has no other meaning

    return stress

