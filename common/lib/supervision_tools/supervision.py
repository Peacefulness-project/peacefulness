# This sheet serves as a library containing basic functions


# ##########################################################################################
# Initialization
# ##########################################################################################

def initialize(world, catalog):  # initialization of the supervisor by adding entries later used in the catalog

    # for world
    for nature in world.natures:  # these entries correspond to the balance made for each nature
        catalog.add(f"{world.name}_{nature}_consumption_balance", 0)
        catalog.add(f"{world.name}_{nature}_production_balance", 0)

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

    for key in world.devices:
        world._devices[key]._update()

    for key in world.agents:
        world._agents[key]._update()


def end_round(world):  # function incrementing the time step and calling dataloggers and daemons
    # it is called after the resolution of the round

    for key in world.devices:
        world._devices[key].react()

    for key in world.dataloggers:  # activation of the dataloggers, they must be called before the daemons,
        # who may have an impact on data
        world._dataloggers[key]._launch()

    for key in world.daemons:  # activation of the daemons
        world._daemons[key]._launch()

    world._update_time()


def make_balance(world, catalog):  # sum the needs and the production for the world

    # the following variable will account the sums of energy
    world_balance = dict()  # balance for each energy type in world
    agent_balance = dict()  # balance for each energy type for one agent
    cluster_balance = dict()  # balance for one cluster

    # initialization of the dictionaries
    for nature in world.natures:
        # balance contains the consumption total in first position and the production total in second
        world_balance[nature] = [0, 0]
        agent_balance[nature] = dict()

    for nature in world.natures:
        for name in world.agents:
            agent_balance[nature][name] = [0, 0]

    for name in world.clusters:
        cluster_balance[name] = [0, 0]

    # balance
    for key in world.devices:  # consumption and production balances
        device = world.devices[key]

        for nature in device.natures:
            # consumption balance
            consumption = catalog.get(f"{device.name}.{nature.name}.asked_energy")
            world_balance[nature.name][0] += consumption
            agent_balance[nature.name][device.agent.name][0] += consumption
            cluster_balance[device.natures[nature].name][0] += consumption

            # production balance
            production = catalog.get(f"{device.name}.{nature.name}.proposed_energy")
            world_balance[nature.name][1] += production
            agent_balance[nature.name][device.agent.name][1] += production
            cluster_balance[device.natures[nature].name][1] += production

    # writing the balance in the catalog
    # for world
    for nature in world.natures:  # saving the balance in the catalog
        catalog.set(f"{world.name}_{nature}_consumption_balance", world_balance[nature][0])
        catalog.set(f"{world.name}_{nature}_production_balance", world_balance[nature][1])

    # for agents
    for nature in world.natures:  # saving the balance in the catalog
        for name in world.agents:
            catalog.set(f"{name}_{nature}_consumption_balance", agent_balance[nature][name][0])
            catalog.set(f"{name}_{nature}_production_balance", agent_balance[nature][name][1])

    # for clusters
    for name in world.clusters:  # saving the balance in the catalog
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

