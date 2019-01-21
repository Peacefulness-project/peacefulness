#  This sheet describes the supervisor, i.e the component ruling the distribution of energy in our grid


# The supervisor function is the main function
# It calls the chosen strategy
def supervisor(world, strategy):

    results = dict()  # It contains all the results of the supervisor
    # It is organized first by step and then by nature of energy

    while world.current_time < world.time_limit:

        world.update()  # updating consumers and producers data

        # calling the chosen strategy to solve the time step
        results_timestep = strategy(world)

        results["results_for_timestep_" + str(world.current_time)] = results_timestep
        print(results["results_for_timestep_" + str(world.current_time)])

        world.next()  # incrementation of the step

    # Writing of the results
    results_file = open("Results", "w")
    results_file.write("Results of our simulation\n"
                       "For each time step, information about each nature of energy "
                       "are provided\n")
    for i in range(world.time_limit):
        results_file.write("\nstep" + str(i) +
                "\nnature, energy asked, energy proposed, presence of the grid,"
                " energy consumed locally, energy exchanged with the grid\n")
        for nat in NATURE:
            results_file.write(nat + " " + str(results["results_for_timestep_" + str(i)][nat]) + "\n")
    results_file.close()


def strat_test(world):  # a strategy which objective is only to test our program
    # here, our "strategy" is just to print if there is a lack or an excess of energy

    # Initialization
    # The keys of the dictionaries correspond to the nature of energy
    results_timestep = dict()  # It's this dictionary which will be returned
    intermediate_table = dict()  # It contains the variables used to arbitrate

    for nat in NATURE:
        intermediate_table[nat] = [0,  # asked energy
                                   0,  # proposed energy
                                   0   # presence of the grid
                                   ]

        results_timestep[nat] = [0,  # asked energy
                                 0,  # proposed energy
                                 0,  # presence of the grid
                                 0,  # energy consumed locally
                                 0   # energy given by the grid (<0 means energy has been sold to the grid)
                                 ]

    for key in world.entity_dict:  # balance of energy, sum of offer and demand
        entity = world.entity_dict[key]
        if type(entity) in CONS:
            intermediate_table[entity.nature][0] += entity.energy
        elif type(entity) in PROD:
            if type(entity) != MainGrid:
                intermediate_table[entity.nature][1] += entity.energy
            else:
                intermediate_table[entity.nature][2] = 1  # It means there is a grid

    print('for the time step', world.current_time, ':')
    for nat in NATURE:
        # energy consumed locally
        results_timestep[nat][3] = min(intermediate_table[nat][0],
                                       intermediate_table[nat][1])

        if intermediate_table[nat][2] == 0:  # If there is no grid
            if intermediate_table[nat][0] < intermediate_table[nat][1]:
                print('Too much', nat, 'on the grid')
            elif intermediate_table[nat][0] > intermediate_table[nat][1]:
                print('Not enough', nat, 'on the grid')
            else:
                print('There is no problem for', nat)
        else:  # If there is a grid
            print('There is no problem for', nat)
            # energy exchanged with the grid
            results_timestep[nat][4] = intermediate_table[nat][1] - \
                                       intermediate_table[nat][0]

    for nat in NATURE:
        results_timestep[nat][0] = intermediate_table[nat][0]  # energy asked by consumers
        results_timestep[nat][1] = intermediate_table[nat][1]  # energy proposed by producers
        results_timestep[nat][2] = intermediate_table[nat][2]  # presence of the grid

    return results_timestep
