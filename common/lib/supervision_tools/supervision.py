# This sheet serves as a library containing basic functions


# ##########################################################################################
# Initialization
# ##########################################################################################

def initialize(world, catalog):  # initialization of the supervisor by adding entries later used in the catalog

    for nature in world.natures:  # these entries correspond to the balance made for each nature
        catalog.add(f"{world.name}_{nature}_consumption_balance", 0)
        catalog.add(f"{world.name}_{nature}_production_balance", 0)


# ##########################################################################################
# Dynamic behaviour
# ##########################################################################################

def start_round(world):  # method updating data to the current timestep

    for key in world._consumptions:
        world._consumptions[key]._update()

    for key in world._productions:
        world._productions[key]._update()

    # for key in world._transformers:
    #     world._transformers[key]._update()
    #
    # for key in world._storage:
    #     world._storage[key]._update()


def end_round(world):  # method incrementing the time step and calling dataloggers and daemons
    # it is called after the resolution of the round

    for key in world._dataloggers:  # activation of the dataloggers, they must be called before the daemons,
        # who may have an impact on data
        world._dataloggers[key]._launch()

    for key in world._daemons:  # activation of the daemons
        world._daemons[key]._launch()

    world._update_time()


def make_balance(world, catalog):  # sum the needs and the production for the world

    balance = dict()  # balance is a dictionary containing the balance for each energy type in the world
    for nature in world.natures:
        balance[nature] = [0, 0]  # balance contains the consumption total in first position
    # and the production total in second

    for key in world._consumptions:  # calculus of the total of consumption
        consumption = world._consumptions[key]
        balance[consumption.nature][0] += catalog.get(f"{consumption.name}.energy")

    for key in world._productions:  # calculus of the total of production
        production = world._productions[key]
        balance[production.nature][1] += catalog.get(f"{production.name}.energy")

    for nature in world.natures:  # saving the balance in the catalog
        catalog.set(f"{world.name}_{nature}_consumption_balance", balance[nature][0])
        catalog.set(f"{world.name}_{nature}_production_balance", balance[nature][1])


# WIP
# def stress_calculus(world, catalog):  # calculus of the stress for each local grid
#
#     for nature in world.natures:
#         cons = catalog.get(f"{world.name}_{nature}_consumer_balance")
#         prod = catalog.get(f"{world.name}_{nature}_producer_balance")
#
#         world._stress[world.name][nature] = cons/prod - prod/cons  # this function has the following behavior:
#         # cons/prod --> +inf ==> stress --> +inf
#         # cons/prod  =  1    ==> stress  =  1
#         # cons/prod --> 0    ==> stress --> -inf
#         # but it has no other meaning
#
