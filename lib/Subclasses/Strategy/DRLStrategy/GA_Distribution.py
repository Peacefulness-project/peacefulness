# In this file, a Hybrid Genetic Algorithm Particle Swarm Optimization function is defined to allocate energy resources determined
# at the level of energy areas (aggregators) by the DRL agent to the level of the individual energy systems (devices).
# Aivaliotis-Apostolopoulos P, Loukidis D. Swarming genetic algorithm: A nested fully coupled hybrid of genetic algorithm and particle swarm optimization. PLoS One. 2022
# Hussain et al., 2024, "Crossover-BPSO driven multi-agent technology for managing local energy systems"

# Imports
from typing import List, Dict, Tuple
import numpy as np
import random


# #####################################################################################################################
# Genetic Algorithm Utilities
#######################################################################################################################
# todo Initialization of the population - param. size + ub/lb from sorted_demands, sorted_offers and sorted_storage
def initialize_my_population(pop_size: int, sorted_demands: List[Dict], sorted_offers: List[Dict], sorted_storage: List[Dict],
                             total_demand: float, total_offer: float, total_storage: float, lower_bounds: List, upper_bounds: List) -> List[Tuple]:
    """
    This function is used to generate the initial population for the optimization.
    """
    global_population = []
    for _ in range(pop_size):
        individual = []
        for element in [sorted_demands, sorted_offers, sorted_storage]:
            for index in range(len(element)):
                individual.append(random.uniform(element[index]["quantity_min"], element[index]["quantity"]))
        individual = tuple(individual)
        individual = ensure_constraints_ga(individual, lower_bounds, upper_bounds, total_demand, total_offer, total_storage, len(sorted_demands), len(sorted_offers), len(sorted_storage))
        global_population.append(individual)

    return global_population


def bounds_and_weights(sorted_demands: List[Dict], sorted_offers: List[Dict], sorted_storage: List[Dict]) -> Tuple[List, List, List]:
    """
    This function is used to store the energy prices as weights for the cost function (specific to distribution to individual energy systems).
    """
    optimization_prices = []
    Emin = []
    Emax = []
    for element in [sorted_demands, sorted_offers, sorted_storage]:
        for device in element:
            Emin.append(device["quantity_min"])
            Emax.append(device["quantity"])
            optimization_prices.append(device["price"])

    return Emin, Emax, optimization_prices

# todo Fitness evaluation
# may directly be the return value of the optimization objective function
# it can also be the return value of each individual term in the optimization objective function
def compute_cost_ga(params, prices) -> float:
    """
    This function computes the cost based on the energy flow and prices values (specific to distribution to individual energy systems).
    """
    individual = np.array(params)
    weights = np.array(prices)

    return abs(np.dot(individual, weights))


def determine_fitness(costs: List[float]) -> np.ndarray:
    """
    This function returns the fitness of each individual of the population.
    """
    costs = np.array(costs)
    global_best = np.min(costs)  # the best solution from the current population
    fitness = global_best / (costs + 1e-12)  # the fitness vector of the current population

    return fitness


# todo Selection of individuals
# techniques => roulette wheel selection, tournament selection and rank-based selection
def apply_eliticism(population: List[Tuple], fitness: np.ndarray, elite_size: int) -> [List[Tuple], List[Tuple]]:
    """
    This function is used to select elite individuals and pass them directly onto the next generation of population.
    """
    sorted_pop = sorted(zip(population, fitness), key=lambda x: x[1], reverse=True)
    elites = sorted_pop[:elite_size]  # the elite individuals
    mongrel = sorted_pop[elite_size:]  # rest of the population

    return elites, mongrel


def rank_based_selection(population: List[Tuple], fitness: np.ndarray) -> List[Tuple]:
    """
    This function identifies selected parents based on rank-based selection technique.
    """
    desc_idx = np.argsort(-fitness)  # descending sort of fitness

    rank = np.empty(len(population), dtype=int)
    rank[desc_idx] = np.arange(1, len(population) + 1)  # rank array

    # selection probabilities
    weights = (len(population) - rank + 1).astype(float)
    probs = weights / (weights.sum() + 1e-12)

    # sampling parents
    indices = np.random.choice(len(population), size=len(population), replace=True, p=probs)

    return [population[i] for i in indices]


def tournament_based_selection(population: List[Tuple], fitness: np.ndarray, tournament_size: int) -> List[Tuple]:
    """
    This function identifies selected parents based on tournament-based selection technique.
    """
    # Pair each individual with its fitness once
    pop_and_fit = list(zip(population, fitness))
    selected_parents = []

    for _ in range(len(population)):
        tournament = [random.choice(pop_and_fit) for _ in range(tournament_size)]  # sample with replacement
        # pick the one with highest fitness
        winner = max(tournament, key=lambda pair: pair[1])[0]
        selected_parents.append(winner)

    return selected_parents


def roulette_wheel_based_selection(population: List[Tuple], fitness: np.ndarray) -> List[Tuple]:
    """
    This function identifies selected parents based on roulette_wheel-based selection technique.
    """
    total = fitness.sum()
    probs = fitness / (total + 1e-12)  # drawing probabilities

    # Draw indices
    chosen_indices = np.random.choice(len(population), size=len(population), replace=True, p=probs)

    return [population[i] for i in chosen_indices]


def selection_phase(population: List[Tuple], fitness_vector: np.ndarray, tournament_size: int, number_of_elites: int = 0, selection_method: int=0) -> List[Tuple]:
    """
    The selection function.
    """
    # selection_method = random.choice([0, 1, 2])

    if number_of_elites > 0:  # if eliticism mechanism is used
        bourgeoisie, proletaria = apply_eliticism(population, fitness_vector, number_of_elites)
        individuals_to_be_selected, their_fitnesses = zip(*proletaria)
        individuals_to_be_selected = list(individuals_to_be_selected)
        their_fitnesses = np.array(their_fitnesses)
        if selection_method == 0:  # roulette-wheel selection is used
            selected_pop = roulette_wheel_based_selection(individuals_to_be_selected, their_fitnesses)
        elif selection_method == 1:  # tournament selection is used
            selected_pop = tournament_based_selection(individuals_to_be_selected, their_fitnesses, tournament_size)
        else:  # rank-based selection is used
            selected_pop = rank_based_selection(individuals_to_be_selected, their_fitnesses)
        elite_pop, elite_fit = zip(*bourgeoisie)
        elite_pop = list(elite_pop)
        selected_pop = [*elite_pop, *selected_pop]

    else:  # if eliticism mechanism is not used
        if selection_method == 0:  # roulette-wheel selection is used
            selected_pop = roulette_wheel_based_selection(population, fitness_vector)
        elif selection_method == 1:  # tournament selection is used
            selected_pop = tournament_based_selection(population, fitness_vector, tournament_size)
        else:  # rank-based selection is used
            selected_pop = rank_based_selection(population, fitness_vector)

    return selected_pop


# todo Crossover
# techniques => single-point crossover, multi-point crossover, uniform crossover and blend crossover
def blend_crossover(parent1: Tuple, parent2: Tuple) -> [Tuple, Tuple]:
    """
    This blend-based crossover function is used to create offspring individuals while ensuring the energy conservation constraint.
    """
    alpha = np.random.rand()
    child1 = alpha * np.array(parent1) + (1 - alpha) * np.array(parent2)
    child2 = (1 - alpha) * np.array(parent1) + alpha * np.array(parent2)

    return tuple(child1), tuple(child2)


# The following 2 techniques are not compatible with the direct use of GA to distribution to individual systems
def multi_point_crossover(parent1: Tuple, parent2: Tuple, number_of_points: int=1) -> [Tuple, Tuple]:
    """
    This function performs N-point crossover between two parent sequences of equal length and returns two offspring.
    """
    if len(parent1) != len(parent2):
        raise ValueError("Parents must be of equal length")
    if not (1 <= number_of_points < len(parent1)):
        raise ValueError("number_of_points must be between 1 and n-1")

    alpha = sorted(np.random.choice(np.arange(1, len(parent1)), size=number_of_points, replace=False))

    child1, child2 = [], []
    switch_flag = False
    cp_idx = 0

    for index in range(len(parent1)):
        if index < alpha[0] and index == alpha[cp_idx]:
            switch_flag = not switch_flag
            cp_idx += 1

        if switch_flag:
            child1.append(parent2[index])
            child2.append(parent1[index])
        else:
            child1.append(parent1[index])
            child2.append(parent2[index])

    return tuple(child1), tuple(child2)


def uniform_crossover(parent1: Tuple, parent2: Tuple) -> [Tuple, Tuple]:
    """
    This function performs uniform crossover between two parent sequences of equal length and returns two offspring.
    """
    child1 = []
    child2 = []
    for index in range(len(parent1)):
        if random.random() < 0.5:
            child1.append(parent1[index])
            child2.append(parent2[index])
        else:
            child1.append(parent2[index])
            child2.append(parent1[index])

    return tuple(child1), tuple(child2)


def crossover_phase(parent1: Tuple, parent2: Tuple, lower_bounds: List, upper_bounds: List, total_demand: float, total_offer: float, total_storage: float,
                    number_of_demands: int, number_of_offers: int, number_of_storage: int, crossover_point: int=2, crossover_method: int=2):
    """
    The crossover phase function.
    """
    # crossover_method = random.choice([0, 1, 2])
    if crossover_method == 0:  # blend crossover method is used
        child1, child2 = blend_crossover(parent1, parent2)
    elif crossover_method == 1:  # uniform crossover method is used
        child1, child2 = uniform_crossover(parent1, parent2)
    else:  # multipoint crossover method is used (one-point by default)
        child1, child2 = multi_point_crossover(parent1, parent2, crossover_point)

    # Ensuring the energy conservation constraint
    child1 = ensure_constraints_ga(child1, lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage)
    child2 = ensure_constraints_ga(child2, lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage)

    return child1, child2


# todo Mutation
# depending on the encoding scheme
def creep_mutation(individual: Tuple, mutation_rate: float, upper_bound: List, lower_bound: List) -> Tuple:
    """
    In this mutation function, a unique and random chromosome is chosen within an individual and its value either de/increases.
    """
    individual = list(individual)
    for index in range(len(individual)):
        if random.random() < mutation_rate:
            mutation_amount = random.uniform(-5, 5)
            individual[index] += mutation_amount
            # Ensure the individual stays within bounds
            individual[index] = max(min(individual[index], upper_bound[index]), lower_bound[index])

    return tuple(individual)


# simply using 1 - x1 (or complementary X1max - x1 + X1min will not work since energy conservation is not respected)
# The following 3 techniques are not compatible with the direct use of GA to distribution to individual systems
def swap_mutation(individual: Tuple, mutation_rate: float, num_swaps: int = 1) -> Tuple:
    """
    In this mutation function, two genes are swapped for num_swaps times.
    """
    individual = list(individual)
    if random.random() < mutation_rate:
        for _ in range(num_swaps):
            idx1, idx2 = np.random.choice(np.arange(len(individual)), size=2, replace=False)  # the two indexes of chromosomes are identified
            individual[idx1], individual[idx2] = individual[idx2], individual[idx1]  # the two chromosomes are swapped

    return tuple(individual)


def scramble_mutation(individual: Tuple, mutation_rate: float) -> Tuple:
    """
    In this mutation function, for a random sequence of genes, the values are shuffled.
    """
    individual = list(individual)

    if random.random() < mutation_rate:
        # Pick two distinct points and sort them
        i, j = sorted(random.sample(range(len(individual)), 2))
        # Extract the segment
        segment = individual[i:j+1]
        # Shuffle in place
        random.shuffle(segment)
        # Write it back
        individual[i:j + 1] = segment

    return tuple(individual)


def inversion_mutation(individual: Tuple, mutation_rate: float) -> Tuple:
    """
    In this mutation function, for a random sequence of genes, the values are reversed.
    """
    individual = list(individual)

    if random.random() < mutation_rate:
        # Pick two distinct points and sort them
        i, j = sorted(random.sample(range(len(individual)), 2))
        # Reverse in-place the segment [i, j]
        individual[i:j+1] = reversed(individual[i:j+1])

    return tuple(individual)


def mutation_phase(next_generation: List, child1: Tuple, child2: Tuple, rate_of_mutation: float, lower_bounds: List, upper_bounds: List,
                   total_demand: float, total_offer: float, total_storage: float,
                   number_of_demands: int, number_of_offers: int, number_of_storage: int, mutation_method: int=3):
    """
    The mutation phase function.
    """
    # mutation_method = random.choice([0, 1, 2, 3])
    if mutation_method == 0:  # creep mutation is used
        next_generation.append(ensure_constraints_ga(creep_mutation(child1, rate_of_mutation, lower_bounds, upper_bounds), lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage))
        next_generation.append(ensure_constraints_ga(creep_mutation(child2, rate_of_mutation, lower_bounds, upper_bounds), lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage))
    elif mutation_method == 1:  # swap mutation is used
        next_generation.append(ensure_constraints_ga(swap_mutation(child1, rate_of_mutation), lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage))
        next_generation.append(ensure_constraints_ga(swap_mutation(child2, rate_of_mutation), lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage))
    elif mutation_method == 2:  # scramble mutation is used
        next_generation.append(ensure_constraints_ga(scramble_mutation(child1, rate_of_mutation), lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage))
        next_generation.append(ensure_constraints_ga(scramble_mutation(child2, rate_of_mutation), lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage))
    else:  # inversion mutation is used
        next_generation.append(ensure_constraints_ga(inversion_mutation(child1, rate_of_mutation), lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage))
        next_generation.append(ensure_constraints_ga(inversion_mutation(child2, rate_of_mutation), lower_bounds, upper_bounds, total_demand, total_offer, total_storage, number_of_demands, number_of_offers, number_of_storage))

    return next_generation

# todo Replacement
# which individuals are moving to the next generation
def ensure_constraints_ga(individual: Tuple, lower_bounds: List, upper_bounds: List, total_demand: float, total_offer: float, total_storage: float,
                          number_of_demands: int, number_of_offers: int, number_of_storage: int,
                          tolerance:float=1e-6, max_iter:int=10):
    """
    This function is used to tweak the individual's genes to ensure energy conservation constraint.
    It is also used to ensure that the individual's genes respect the energy dispatch decision of the DRL agent.
    """
    individual = np.array(individual).astype(float)
    individual -= sum(individual) / individual.size

    # Individual energy systems upper/lower bounds constraint
    individual = np.clip(individual, np.array(lower_bounds), np.array(upper_bounds))

    # Energy conservation constraint
    offset = sum(individual)

    # DRL energy dispatch constraint
    cons_offset = sum(individual[: number_of_demands]) - total_demand
    prod_offset = sum(individual[number_of_demands : number_of_demands + number_of_offers]) - total_offer
    stor_offset = sum(individual[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage]) - total_storage

    iteration = 0

    while abs(offset) > tolerance and iteration < max_iter:
        # flexible demand units
        free_demands = np.where((individual[: number_of_demands] > np.array(lower_bounds[: number_of_demands])) & (individual[: number_of_demands] < np.array(upper_bounds[: number_of_demands])))[0]
        if free_demands.size != 0 and abs(cons_offset) > tolerance:
            individual[free_demands] -= cons_offset / free_demands.size

        # flexible offer units
        free_offers = np.where((individual[number_of_demands : number_of_demands + number_of_offers] > np.array(lower_bounds[number_of_demands : number_of_demands + number_of_offers])) & (individual[number_of_demands : number_of_demands + number_of_offers] < np.array(upper_bounds[number_of_demands : number_of_demands + number_of_offers])))[0]
        if free_offers.size != 0 and abs(prod_offset) > tolerance:
            individual[free_offers + number_of_demands] -= prod_offset / free_offers.size

        # flexible storage units
        free_storage = np.where((individual[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage] > np.array(lower_bounds[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage])) & (individual[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage] < np.array(upper_bounds[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage])))[0]
        if free_storage.size != 0 and abs(stor_offset) > tolerance:
            individual[free_storage + number_of_demands + number_of_offers] -= stor_offset / free_storage.size

        # indices that are not at bounds (free to change)
        free = np.where((individual > np.array(lower_bounds)) & (individual < np.array(upper_bounds)))[0]
        if free.size == 0:
            break  # can't redistribute further
        offset = sum(individual)
        individual[free] -= offset / free.size
        individual = np.clip(individual, np.array(lower_bounds), np.array(upper_bounds))

        # checking for the next iteration
        offset = sum(individual)
        cons_offset = sum(individual[: number_of_demands]) - total_demand
        prod_offset = sum(individual[number_of_demands: number_of_demands + number_of_offers]) - total_offer
        stor_offset = sum(individual[number_of_demands + number_of_offers: number_of_demands + number_of_offers + number_of_storage]) - total_storage
        iteration += 1

    # If still outside tolerance, try to absorb residual into a single variable if possible
    if abs(cons_offset) > tolerance:
        # look for any index where moving it by -residual keeps it within bounds
        for index in range(number_of_demands):
            new_val = individual[index] - cons_offset
            if np.array(lower_bounds)[index] <= new_val <= np.array(upper_bounds)[index]:
                individual[index] = new_val
                break

    if abs(prod_offset) > tolerance:
        # look for any index where moving it by -residual keeps it within bounds
        for index in range(number_of_offers):
            new_val = individual[index + number_of_demands] - prod_offset
            if np.array(lower_bounds)[index + number_of_demands] <= new_val <= np.array(upper_bounds)[index + number_of_demands]:
                individual[index + number_of_demands] = new_val
                break

    if abs(stor_offset) > tolerance:
        # look for any index where moving it by -residual keeps it within bounds
        for index in range(number_of_storage):
            new_val = individual[index + number_of_demands + number_of_offers] - stor_offset
            if np.array(lower_bounds)[index + number_of_demands + number_of_offers] <= new_val <= np.array(upper_bounds)[index + number_of_demands + number_of_offers]:
                individual[index + number_of_demands + number_of_offers] = new_val
                break

    if abs(offset) > tolerance:
        # look for any index where moving it by -residual keeps it within bounds
        for index in range(individual.size):
            new_val = individual[index] - offset
            if np.array(lower_bounds)[index] <= new_val <= np.array(upper_bounds)[index]:
                individual[index] = new_val
                break

    return tuple(individual.tolist())


# #####################################################################################################################
# Main Genetic Algorithm loop
#######################################################################################################################
def genetic_algorithm(sorted_demands: List[Dict], sorted_offers: List[Dict], sorted_storage: List[Dict],
                      population_size: int, number_of_generations: int, rate_of_mutation: float, tournament_size: int
                      , energy_demand: float, energy_generation: float, energy_storage: float
                      , crossover_point: int=1, number_of_elites: int=0) -> Tuple:
    """
    The main loop of the genetic algorithm that uses different techniques for selection, crossover and mutation with or without the eliticism mechanism.
    :param: population_size - even number of the size of population
    :param: number_of_generations - number of generations (optimization iterations)
    :param: rate_of_mutation - threshold for triggering mutations
    :param: tournament_size - in case of use of tournament selection technique
    :param: crossover_point - in case of use of multi-point selection technique
    :param: number_of_elites - if eliticism mechanism is used
    """
    # initialize the price vector and upper/lower bounds
    lower_bounds, upper_bounds, weights = bounds_and_weights(sorted_demands, sorted_offers, sorted_storage)
    # initialize population
    population = initialize_my_population(population_size, sorted_demands, sorted_offers, sorted_storage, energy_demand, energy_generation, energy_storage, lower_bounds, upper_bounds)
    # generation loop
    for generation in range(number_of_generations):
        # compute fitness
        cost_vector = [compute_cost_ga(individual, weights) for individual in population]
        fitness_vector = determine_fitness(cost_vector)

        # perform selection
        selected_pop = selection_phase(population, fitness_vector, tournament_size, number_of_elites)

        # replace population by next generation
        next_generation = []
        for i in range(0, population_size, 2):
            parent1 = selected_pop[i]
            parent2 = selected_pop[i + 1]

            # perform crossover
            child1, child2 = crossover_phase(parent1, parent2, lower_bounds, upper_bounds, energy_demand, energy_generation, energy_storage, len(sorted_demands), len(sorted_offers), len(sorted_storage), crossover_point)

            # perform mutation
            next_generation = mutation_phase(next_generation, child1, child2, rate_of_mutation, lower_bounds, upper_bounds, energy_demand, energy_generation, energy_storage, len(sorted_demands), len(sorted_offers), len(sorted_storage))

        # finally the next generation replaces the current population
        population = next_generation

    # Final computation of the fitness of the last iteration population
    cost_vector = [compute_cost_ga(individual, weights) for individual in population]
    fitness_vector = determine_fitness(cost_vector)
    best_fitness = int(np.argmax(fitness_vector))  # the index corresponding to the best performance

    return population[best_fitness]  # the distribution with the best performance is returned



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
# print(genetic_algorithm(my_demands, my_offers, my_storage, 100, 100, 0.89, 25, e_con, e_prod, e_sto
#                         , crossover_point=3, number_of_elites=10
#                         ))


