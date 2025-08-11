# In this file, a Hybrid Genetic Algorithm Particle Swarm Optimization function is defined to allocate energy resources determined
# at the level of energy areas (aggregators) by the DRL agent to the level of the individual energy systems (devices).
# Aivaliotis-Apostolopoulos P, Loukidis D. Swarming genetic algorithm: A nested fully coupled hybrid of genetic algorithm and particle swarm optimization. PLoS One. 2022
# Hussain et al., 2024, "Crossover-BPSO driven multi-agent technology for managing local energy systems"

# Imports
from GA_Distribution import *
from PSO_Distribution import *
from typing import Callable, Optional


# #####################################################################################################################
# Main Swarm Genetic Algorithm Optimization Loop
#######################################################################################################################
def sga_algorithm(total_demand: float, total_offer: float, total_storage: float, n_ga: int, n_pso: int, n_max: int,
                  sorted_demands: List[Dict], sorted_offers: List[Dict], sorted_storage: List[Dict],
                  mg: int, mp: int,
                  rm: float, nt: int,
                  c1: float, c2: float, w: float,
                  ncr: int = 1, nel: int = 0,
                  w_end: float = 0.0, g_OR_l: int = 0,
                  objective_function: Optional[Callable]=None) -> Tuple:
    """
    The main swarm genetic algorithm optimization loop.
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
    # initialize population
    lower_bounds, upper_bounds, weights = bounds_and_weights(sorted_demands, sorted_offers, sorted_storage)
    population = initialize_my_population(mg, sorted_demands, sorted_offers, sorted_storage, total_demand, total_offer, total_storage, lower_bounds, upper_bounds)

    # Outer optimization loop
    for out_iter in range(1, n_max + 1):
        if out_iter % n_ga != 0:  # GA loop
            # compute fitness
            if objective_function:
                scores = [objective_function(individual) for individual in population]
            else:
                scores = [compute_cost_ga(individual, weights) for individual in population]
            fitness_vector = determine_fitness(scores)
            # perform selection
            selected_pop = selection_phase(population, fitness_vector, nt, nel)
            # replace population by next generation
            next_generation = []
            for i in range(0, len(selected_pop), 2):
                parent1 = selected_pop[i]
                parent2 = selected_pop[i + 1]
                # perform crossover
                child1, child2 = crossover_phase(parent1, parent2, lower_bounds, upper_bounds, total_demand, total_offer, total_storage, len(sorted_demands), len(sorted_offers), len(sorted_storage), ncr)
                # perform mutation
                next_generation = mutation_phase(next_generation, child1, child2, rm, lower_bounds, upper_bounds, total_demand, total_offer, total_storage, len(sorted_demands), len(sorted_offers), len(sorted_storage))
            # finally the next generation replaces the current population
            population = next_generation

        else:  # PSO loop
            # random selection of individuals for PSO
            selected_for_pso = random.sample(population, mp)
            rest_of_population = deepcopy(population)
            for individual in selected_for_pso:
                rest_of_population.remove(individual)

            if objective_function:
                scores = [objective_function(individual) for individual in selected_for_pso]
            else:
                scores = [compute_cost_ga(individual, weights) for individual in selected_for_pso]

            particles = [Particle(GA_individual=individual) for individual in selected_for_pso]

            # the global best
            best_idx = int(np.argmin(np.array(scores)))
            pso_global_best_position = particles[best_idx].position
            pso_global_best_score = scores[best_idx]

            for in_iter in range(n_pso):
                # Computing the inertia coefficient
                if g_OR_l == 0:  # no damping technique is used
                    inertia_coefficient = w
                elif g_OR_l == 1:  # linear damping is used to compute the inertia coefficient
                    inertia_coefficient = apply_linear_damping(w, w_end, in_iter, n_pso)
                else:  # geometric damping is used to compute the inertia coefficient
                    inertia_coefficient = apply_geometric_decay(w, w_end, in_iter, n_pso)

                # Updating each particle position and velocity
                update_particles(particles, pso_global_best_position, inertia_coefficient, c1, c2, lower_bounds, upper_bounds, weights, total_demand, total_offer, total_storage, len(sorted_demands), len(sorted_offers), len(sorted_storage))

                # Updating the global score and position
                for particle in particles:
                    if objective_function:
                        score = objective_function(particle.position)
                    else:
                        score = compute_cost_ga(particle.position, weights)

                    if score < pso_global_best_score:
                        pso_global_best_position = deepcopy(particle.position)
                        pso_global_best_score = score

            pso_sub_population = [particle.position for particle in particles]
            population = [*pso_sub_population, *rest_of_population]

        # Updating global best of the entire population
        if objective_function:
            scores = [objective_function(individual) for individual in population]
        else:
            scores = [compute_cost_ga(individual, weights) for individual in population]

    # the global best solution
    best_idx = int(np.argmax(np.array(scores)))
    global_best_individual = population[best_idx]
    global_best_score = scores[best_idx]

    return global_best_individual





# my_demands = [{"type": "demand", "quantity_min": 0, "quantity": 120, "price": 0.85}, {"type": "demand", "quantity_min": 0, "quantity": 110, "price": 0.65},
#               {"type": "demand", "quantity_min": 0, "quantity": 90, "price": 0.75},
#               {"type": "demand", "quantity_min": 0, "quantity": 150, "price": 0.4}, {"type": "demand", "quantity_min": 0, "quantity": 180, "price": 0.45},
#               {"type": "demand", "quantity_min": 0, "quantity": 300, "price": 0.25}, {"type": "demand", "quantity_min": 0, "quantity": 20, "price": 1.05},
#               {"type": "demand", "quantity_min": 0, "quantity": 45, "price": 0.8}, {"type": "demand", "quantity_min": 0, "quantity": 75, "price": 0.78},
#               {"type": "demand", "quantity_min": 0, "quantity": 105, "price": 0.7}]
#
# my_offers = [{"type": "offer", "quantity_min": - 120, "quantity": 0, "price": 0.5}, {"type": "offer", "quantity_min": - 110, "quantity": 0, "price": 0.69},
#              {"type": "offer", "quantity_min": - 90, "quantity": 0, "price": 0.89}, {"type": "offer", "quantity_min": - 150, "quantity": 0, "price": 0.42},
#              {"type": "offer", "quantity_min": - 180, "quantity": 0, "price": 0.4},
#               {"type": "offer", "quantity_min": - 380, "quantity": 0, "price": 0.35}, {"type": "offer", "quantity_min": - 20, "quantity": 0, "price": 1.05}]
#
# my_storage = [{"type": "storage", "quantity_min": - 120, "quantity": 30, "price": 0.81},
#               {"type": "storage", "quantity_min": - 110, "quantity": 15, "price": 0.69},
#              {"type": "storage", "quantity_min": - 90, "quantity": 5, "price": 0.89},
#               {"type": "storage", "quantity_min": -150, "quantity": 45, "price": 0.42}]
#
# e_con = 850.
# e_prod = - 700.
# e_sto = - 150.
#
#
# print(sga_algorithm(e_con, e_prod, e_sto, 25, 50, 100, my_demands, my_offers, my_storage, 100, 30, 0.6942, 20, 0.81, 0.89, 0.73))


