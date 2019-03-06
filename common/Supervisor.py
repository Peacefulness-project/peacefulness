#  This sheet describes the supervisor, i.e the component ruling the distribution of energy in our grid

from common.Core import World
from common.Catalog import Catalog


class Supervisor:  # generic class supervisor

    def __init__(self, name, world):
        self._name = name
        self._world = world
        self._catalog = world.catalog

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def initialize(self, world=None):  # initialization of the supervisor by adding entries later used in the catalog
        if not world:  # if no world is given, the main world is the default value
            world = self._world  # this operation allows not to give a name when calling the method

        for subworld in world._subworlds:
            self.initialize(world._subworlds[subworld])

        for nature in world._natures:
            self._catalog.add(f"{world._name}_{nature}_consumer_balance", 0)
            self._catalog.add(f"{world._name}_{nature}_producer_balance", 0)

    # ##########################################################################################
    # Dynamic behaviour
    # ##########################################################################################

    def process(self):
        pass

    def make_balance(self, world=None):  # make the balance for the world and for each subworld recursively
        if not world:  # if no world is given, the main world is the default value
            world = self._world  # this operation allows not to give a name when the method is called

        balance = dict()  # balance is a dictionary containing the balance for each energy type in the world
        for nature in world._natures:
            balance[nature] = [0, 0]  # balance contains the consumption total in first position
        # and the production total in second

        for subworld in world._subworlds:  # recuperation of the balance of subworlds
            self.make_balance(world._subworlds[subworld])

        for nature in world._natures:
            balance[nature][0] += world._catalog.get(f"{world._name}_{nature}_consumer_balance")
            balance[nature][1] += world._catalog.get(f"{world._name}_{nature}_producer_balance")

        for key in world._consumers:  # calculus of the total of consumption
            consumer = world._consumers[key]
            balance[consumer._nature][0] += consumer._energy

        for key in world._producers:  # calculus of the total of production
            producer = world._producers[key]
            balance[producer._nature][1] += producer._energy

        for nature in world._natures:  # saving the balance in the catalog
            self._catalog.set(f"{world._name}_{nature}_consumer_balance", balance[nature][0])
            self._catalog.set(f"{world._name}_{nature}_producer_balance", balance[nature][1])

    # ##########################################################################################
    # Utility
    # ##########################################################################################





























# # The supervisor function is the main function
# # It calls the chosen strategy
# def supervisor(world, strategy):
#
#     results = dict()  # It contains all the results of the supervisor
#     # It is organized first by step and then by nature of energy
#
#     while world.current_time < world.time_limit:
#
#         world.update()  # updating consumers and producers data
#
#         # calling the chosen strategy to solve the time step
#         results_timestep = strategy(world)
#
#         results["results_for_timestep_" + str(world.current_time)] = results_timestep
#         print(results["results_for_timestep_" + str(world.current_time)])
#
#         world.next()  # incrementation of the step
#
#     # Writing of the results
#     results_file = open("Results", "w")
#     results_file.write("Results of our simulation\n"
#                        "For each time step, information about each nature of energy "
#                        "are provided\n")
#     for i in range(world.time_limit):
#         results_file.write("\nstep" + str(i) +
#                 "\nnature, energy asked, energy proposed, presence of the grid,"
#                 " energy consumed locally, energy exchanged with the grid\n")
#         for nat in NATURE:
#             results_file.write(nat + " " + str(results["results_for_timestep_" + str(i)][nat]) + "\n")
#     results_file.close()
#
#
# def strat_test(world):  # a strategy which objective is only to test our program
#     # here, our "strategy" is just to print if there is a lack or an excess of energy
#
#     # Initialization
#     # The keys of the dictionaries correspond to the nature of energy
#     results_timestep = dict()  # It's this dictionary which will be returned
#     intermediate_table = dict()  # It contains the variables used to arbitrate
#
#     for nat in NATURE:
#         intermediate_table[nat] = [0,  # asked energy
#                                    0,  # proposed energy
#                                    0   # presence of the grid
#                                    ]
#
#         results_timestep[nat] = [0,  # asked energy
#                                  0,  # proposed energy
#                                  0,  # presence of the grid
#                                  0,  # energy consumed locally
#                                  0   # energy given by the grid (<0 means energy has been sold to the grid)
#                                  ]
#
#     for key in world.entity_dict:  # balance of energy, sum of offer and demand
#         entity = world.entity_dict[key]
#         if type(entity) in CONS:
#             intermediate_table[entity.nature][0] += entity.energy
#         elif type(entity) in PROD:
#             if type(entity) != MainGrid:
#                 intermediate_table[entity.nature][1] += entity.energy
#             else:
#                 intermediate_table[entity.nature][2] = 1  # It means there is a grid
#
#     print('for the time step', world.current_time, ':')
#     for nat in NATURE:
#         # energy consumed locally
#         results_timestep[nat][3] = min(intermediate_table[nat][0],
#                                        intermediate_table[nat][1])
#
#         if intermediate_table[nat][2] == 0:  # If there is no grid
#             if intermediate_table[nat][0] < intermediate_table[nat][1]:
#                 print('Too much', nat, 'on the grid')
#             elif intermediate_table[nat][0] > intermediate_table[nat][1]:
#                 print('Not enough', nat, 'on the grid')
#             else:
#                 print('There is no problem for', nat)
#         else:  # If there is a grid
#             print('There is no problem for', nat)
#             # energy exchanged with the grid
#             results_timestep[nat][4] = intermediate_table[nat][1] - \
#                                        intermediate_table[nat][0]
#
#     for nat in NATURE:
#         results_timestep[nat][0] = intermediate_table[nat][0]  # energy asked by consumers
#         results_timestep[nat][1] = intermediate_table[nat][1]  # energy proposed by producers
#         results_timestep[nat][2] = intermediate_table[nat][2]  # presence of the grid
#
#     return results_timestep
