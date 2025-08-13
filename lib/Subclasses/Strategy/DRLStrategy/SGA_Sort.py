# Here we are optimizing the coefficients alpha_i of a sorting function based on the swarm genetic hybrid optimization algorithm.
# Aivaliotis-Apostolopoulos P, Loukidis D. Swarming genetic algorithm: A nested fully coupled hybrid of genetic algorithm and particle swarm optimization. PLoS One. 2022
# Hussain et al., 2024, "Crossover-BPSO driven multi-agent technology for managing local energy systems"


# Imports
from GA_Sort import *
from PSO_Sort import *


# #####################################################################################################################
# Main Swarm Genetic Algorithm Optimization Loop for the sorting functions
#######################################################################################################################

def alpha_SGA(full_message: List[Dict], rl_dispatch: float, buying_price: float, selling_price: float,
              n_ga: int, n_pso: int, n_max: int,
              mg: int, mp: int,
              rm: float, nt: int,
              c1: float, c2: float, w: float,
              ncr: int = 1, nel: int = 0,
              w_end: float = 0.0, g_OR_l: int = 0,
              objective_func: Optional[Callable]=None, min_or_max_flag: bool=True):
    """
    The main swarm genetic algorithm optimization loop applied to the sorting functions.
    :param: ng: number of iterations where GA is applied
    :param: np: number of iterations where PSO is applied
    :param: n_max: maximum number of iterations of the overall optimization
    :param: mg: total population size
    :param: mp: total number of particles
    :param: rm: rate of mutation
    :param: nt: tournament size (if tournament size selection is used)
    :param: c1: personal coefficient (for velocity update)
    :param: c2: social coefficient (for velocity update)
    :param: w: inertia coefficient (for velocity update)
    :param: ncr: number of crossover points (if cross over selection is used) - OPTIONAL
    :param: nel: number of elite individuals (if eliticism mechanism is used) - OPTIONAL
    :param: w_end: final inertia coefficient (if damping mechanism is used) - OPTIONAL
    :param: g_OR_l: flag for damping technique (either geometric or linear) - OPTIONAL
    """
    # initialization of population
    my_horizon = find_largest_horizon(full_message)
    input_vector = normalize_my_input(full_message, rl_dispatch, buying_price, selling_price, my_horizon)
    my_population = initialize_my_population(mg, input_vector)

    # Outer optimization loop
    for out_iter in range(1, n_max + 1):
        if out_iter % n_ga != 0:  # GA loop
            # compute fitness
            sorted_output = [compute_and_order_output(input_vector, individual) for individual in my_population]
            my_allocation = [serve_and_execute_order(full_message, rl_dispatch, my_output) for my_output in sorted_output]
            my_costs = [compute_cost(tup[0], tup[1], objective_func) for tup in my_allocation]
            my_fitness = calculate_fitness(my_costs, min_or_max_flag)
            # perform selection
            selected_pop = selection_phase(my_population, my_fitness, nt, nel, selection_method=0)
            # replace population by next generation
            next_generation = []
            for i in range(0, len(selected_pop), 2):
                parent1 = selected_pop[i]
                parent2 = selected_pop[i + 1]
                # perform crossover
                child1, child2 = crossover_phase_alpha(parent1, parent2, ncr, crossover_method=0)
                # perform mutation
                next_generation = mutation_phase_alpha(next_generation, child1, child2, rm, mutation_method=0)
            # finally the next generation replaces the current population
            my_population = next_generation

        else:  # PSO loop
            # random selection of individuals for PSO
            selected_for_pso = random.sample(my_population, mp)
            rest_of_population = deepcopy(my_population)
            for individual in selected_for_pso:
                rest_of_population.remove(individual)

            my_particles = [alpha_Particle(GA_individual=individual) for individual in selected_for_pso]

            # the global best
            my_scores, my_distributions = compute_scores(full_message, rl_dispatch, input_vector, my_particles, objective_func)
            global_best_position, global_best_score, best_idx = evaluate_position(my_particles, my_scores, min_or_max_flag)

            for in_iter in range(n_pso):
                # Computing the inertia coefficient
                if g_OR_l == 0:  # no damping technique is used
                    inertia_coefficient = w
                elif g_OR_l == 1:  # linear damping is used to compute the inertia coefficient
                    inertia_coefficient = apply_linear_damping(w, w_end, in_iter, n_pso)
                else:  # geometric damping is used to compute the inertia coefficient
                    inertia_coefficient = apply_geometric_decay(w, w_end, in_iter, n_pso)

                # Updating each particle position and velocity
                update_position_and_velocity(full_message, rl_dispatch, input_vector,
                                             my_particles, global_best_position,
                                             inertia_coefficient, c1, c2,
                                             min_or_max_flag,
                                             crossover_prob=0, crossover_alpha=0, objective_func=objective_func)

                # Updating the global score and position
                my_scores, my_distributions = compute_scores(full_message, rl_dispatch, input_vector, my_particles, objective_func)
                global_best_position, global_best_score, best_idx = evaluate_position(my_particles, my_scores, min_or_max_flag)

            pso_sub_population = [particle.position for particle in my_particles]
            my_population = [*pso_sub_population, *rest_of_population]

    # Computing final scores of the entire population and identifying the global best solution
    final_sorted_output = [compute_and_order_output(input_vector, individual) for individual in my_population]
    final_allocation = [serve_and_execute_order(full_message, rl_dispatch, my_output) for my_output in final_sorted_output]
    final_cost = [compute_cost(tup[0], tup[1], objective_func) for tup in final_allocation]
    final_fitness = calculate_fitness(final_cost, min_or_max_flag)
    best_index = int(np.argmax(final_fitness))  # the index corresponding to the best performance


    return my_population[best_index], final_allocation[best_index][0], final_cost[best_index]  # the distribution with the best performance is returned






# my_demands = [{"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 120, "price": 0.85, "flexibility": [12, 27, 35, 41], "interruptibility": 1, "coming_volume": 350},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 110, "price": 0.65, "flexibility": [0], "interruptibility": 0, "coming_volume": 0},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 90, "price": 0.75, "flexibility": [0, 0], "interruptibility": 0, "coming_volume": 0},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 150, "price": 0.4, "flexibility": [0, 0, 0], "interruptibility": 0, "coming_volume": 0},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 180, "price": 0.45, "flexibility": [12, 27], "interruptibility": 1, "coming_volume": 500},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 300, "price": 0.25, "flexibility": [27, 35, 41], "interruptibility": 1, "coming_volume": 1000},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 20, "price": 1.05, "flexibility": [0, 0, 0, 0], "interruptibility": 0, "coming_volume": 0},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 45, "price": 0.8, "flexibility": [12, 35, 41], "interruptibility": 1, "coming_volume": 140},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 75, "price": 0.78, "flexibility": [1], "interruptibility": 1, "coming_volume": 270},
#               {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 105, "price": 0.7, "flexibility": [0], "interruptibility": 0, "coming_volume": 0}]
#
# my_offers = [{"type": "standard", "energy_minimum": - 120, "energy_nominal": 0, "energy_maximum": 0, "price": 0.5, "flexibility": [-150, -100], "interruptibility": 1, "coming_volume": - 250},
#              {"type": "standard", "energy_minimum": - 110, "energy_nominal": 0, "energy_maximum": 0, "price": 0.69, "flexibility": [-120, -30], "interruptibility": 1, "coming_volume": - 150},
#              {"type": "standard", "energy_minimum": - 90, "energy_nominal": 0, "energy_maximum": 0, "price": 0.89, "flexibility": [0], "interruptibility": 0, "coming_volume": 0},
#              {"type": "standard", "energy_minimum": - 150, "energy_nominal": 0, "energy_maximum": 0, "price": 0.42, "flexibility": [0], "interruptibility": 0, "coming_volume": 0},
#              {"type": "standard", "energy_minimum": - 180, "energy_nominal": 0, "energy_maximum": 0, "price": 0.4, "flexibility": [0, 0], "interruptibility": 0, "coming_volume": 0},
#              {"type": "standard", "energy_minimum": - 380, "energy_nominal": 0, "energy_maximum": 0, "price": 0.35, "flexibility": [-1000], "interruptibility": 1, "coming_volume": - 1000},
#              {"type": "standard", "energy_minimum": - 20, "energy_nominal": 0, "energy_maximum": 0, "price": 1.05, "flexibility": [0], "interruptibility": 0, "coming_volume": 0}]
#
# my_storage = [{"type": "storage", "energy_minimum": - 120, "energy_nominal": 0, "energy_maximum": 30, "price": 0.1, "state_of_charge": 0.35, "capacity": 1000, "self_discharge_rate": 0.002, "efficiency": 0.89},
#               {"type": "storage", "energy_minimum": - 110, "energy_nominal": 0, "energy_maximum": 15, "price": 0.69, "state_of_charge": 0.47, "capacity": 500, "self_discharge_rate": 0.001, "efficiency": 0.91},
#               {"type": "storage", "energy_minimum": - 90, "energy_nominal": 0, "energy_maximum": 5, "price": 0.89, "state_of_charge": 0.81, "capacity": 250, "self_discharge_rate": 0.003, "efficiency": 0.73},
#               {"type": "storage", "energy_minimum": -150, "energy_nominal": 0, "energy_maximum": 45, "price": 0.42, "state_of_charge": 0.68, "capacity": 1250, "self_discharge_rate": 0.006, "efficiency": 0.61}]
#
# e_con = 850.
# e_prod = - 700.
# e_sto = - 150.
# buy_p = 0.69
# sell_p = 0.42
#
#
#
# print(alpha_SGA(my_demands, e_con, buy_p, sell_p, 25, 50, 100, 100, 30, 0.6942, 20, 0.81, 0.89, 0.73))
# print(alpha_SGA(my_offers, e_prod, buy_p, sell_p, 25, 50, 100, 100, 30, 0.6942, 20, 0.81, 0.89, 0.73))
# print(alpha_SGA(my_storage, e_sto, buy_p, sell_p, 25, 50, 100, 100, 30, 0.6942, 20, 0.81, 0.89, 0.73))


