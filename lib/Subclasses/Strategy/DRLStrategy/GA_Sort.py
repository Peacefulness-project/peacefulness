# Here we are optimizing the coefficients alpha_i of a sorting function based on the genetic algorithm optimization.

# Constraints ? ===>>> 1 - lower and upper boundaries for energy flows of each individual energy system --------------------------------- ensured with "serve_and_execute_order" + serving the E_min first
# 		       2 - sum of the energy flows of each category of energy systems = RL decision for the energy system category ------ ensured with "serve_and_execute_order"
# 		       3 - energy conservation = sum of energy flows equals 0 ----------------------------------------------------------- ensured via the RL decision itself



# Imports
from GA_Distribution import *
from typing import Optional, Callable
from src.tools.Utilities import sign



# initialize my population : alpha_i ,  i = [1, ..., N], N being the length of the full messages
# inputs => indirect_optimization_demands + indirect_optimization_offers + indirect_optimization_storage
def initialize_my_population(population_size: int, normalized_input: List[Tuple], lower_bound:float= - 1.0, upper_bound:float= 1.0) -> List[Tuple]:
    """
    This function initializes the individuals for the GA.
    It is used to generate the alpha_i for each sorting function (demands, offers & storage).
    Full_message is the normalized input values instead of the raw device messages.
    """
    global_population = []
    for _ in range(population_size):
        individual = []
        for _ in range(len(normalized_input[0])):
            alpha_i = random.uniform(lower_bound, upper_bound)
            individual.append(alpha_i)
        global_population.append(tuple(individual))

    return global_population


# sum alpha_i * info_msg_i = y (normalization)
# 1-step => normalization & preparing the input matrix to the sort function
def normalize_my_input(full_message: List[Dict], dispatch_RL: float, buying_price: float, selling_price: float, horizon:int=0) -> List[Tuple]:
    """
    The energy dispatch decision by the DRL at the aggregator level is used to normalize the energy values for each category.
    For prices, the maximum_buying_price and minimum_selling_price are used.
    """
    normalized_input = []
    used_price = (buying_price + selling_price) / 2
    if full_message[0]["type"] == "standard":  # energy demand/generation
        for element in full_message:
            temp_dict = []
            for key in element:
                if key == "price":
                    temp_dict.append(element[key] / used_price)
                elif key == "flexibility":
                    for step in range(horizon):
                        if step < len(element[key]):
                            temp_dict.append(element[key][step] / dispatch_RL)
                        else:
                            temp_dict.append(element[key][-1] / dispatch_RL)
                elif key == "coming_volume":
                    temp_dict.append(element[key] / (horizon * dispatch_RL))
                elif key == "type":
                    pass
                else:
                    temp_dict.append(element[key] / dispatch_RL)
            normalized_input.append(tuple(temp_dict))
    else:  # energy storage
        for element in full_message:
            temp_dict = []
            for key in element:
                if key == "type":
                    pass
                elif key == "state_of_charge" or key == "self_discharge_rate" or key == "efficiency":
                    temp_dict.append(element[key])
                elif key == "price":
                    temp_dict.append(element[key] / used_price)
                else:
                    temp_dict.append(element[key] / dispatch_RL)
            normalized_input.append(tuple(temp_dict))

    return normalized_input


def find_largest_horizon(full_message: List[Dict]) -> int:
    """
    This function is used to find the largest horizon (forecast) for flexibility of standard devices.
    """
    if not full_message[0]["type"] == "standard":  # if storage devices
        horizon = 0
    else:
        check_list = []
        for element in full_message:
            check_list.append(len(element["flexibility"]))
        horizon = max(check_list)

    return horizon


# sorting y = order of serving devices
def compute_and_order_output(normalized_input: List[Tuple], individual: Tuple) -> Tuple:
    """
    In this function, for each demand/offer/storage, an output value is computed (alpha_i * msg_i).
    These values are then sorted in a descending manner.
    The ordering is 'unique' to each individual (alpha_i) of the population.
    The list of order of serving is returned.
    """
    y_output = []
    alpha_i = np.array(individual)
    for index in range(len(normalized_input)):
        y_output.append(np.dot(alpha_i, np.array(normalized_input[index])))

    return tuple(np.argsort(y_output))


# serving the Emax w.r.t sorting order
def serve_and_execute_order(full_message: List[Dict], dispatch_RL: float, serving_order: Tuple) -> Tuple[np.ndarray, np.ndarray]:
    """
    This function is used to serve the demand/offer/storage according to the order computed with the sorting function.
    It returns two vectors one of the energy quantities given and one of the energy prices.
    """
    ordered_message = []
    ordered_decision = np.zeros(len(full_message))
    ordered_prices = np.zeros(len(full_message))
    for index in serving_order:
        ordered_message.append(full_message[index])

    serve_decision = np.zeros_like(ordered_message)
    price_decision = np.zeros_like(ordered_message)
    for index in range(len(ordered_message)):  # serving the rest
        if abs(dispatch_RL) > 0:  # todo à checker comme même quand je lance la strategy
            if ordered_message[index]["energy_maximum"] > 0 and ordered_message[index]["energy_minimum"] == 0:  # energy consumption
                if abs(ordered_message[index]["energy_maximum"]) > abs(dispatch_RL):
                    serve_decision[index] = dispatch_RL
                    dispatch_RL -= dispatch_RL
                else:  # serving the maximum energy wanted
                    serve_decision[index] = ordered_message[index]["energy_maximum"]
                    dispatch_RL -= ordered_message[index]["energy_maximum"]
            elif ordered_message[index]["energy_minimum"] < 0 and ordered_message[index]["energy_maximum"] == 0:  # energy production
                if abs(ordered_message[index]["energy_minimum"]) > abs(dispatch_RL):
                    serve_decision[index] = dispatch_RL
                    dispatch_RL -= dispatch_RL
                else:  # serving the maximum energy wanted
                    serve_decision[index] = ordered_message[index]["energy_minimum"]
                    dispatch_RL -= ordered_message[index]["energy_minimum"]
            else:  # energy storage
                if abs(dispatch_RL) < abs(ordered_message[index]["energy_maximum"]) and abs(dispatch_RL) < abs(ordered_message[index]["energy_minimum"]):
                    serve_decision[index] = dispatch_RL
                    dispatch_RL -= dispatch_RL
                else:
                    to_be_served = ordered_message[index]["energy_minimum"] if sign(ordered_message[index]["energy_minimum"]) == sign(dispatch_RL) else ordered_message[index]["energy_maximum"]
                    serve_decision[index] = to_be_served
                    dispatch_RL -= to_be_served

            price_decision[index] = ordered_message[index]["price"]
        else:
            pass

    for i, original_index in enumerate(serving_order):  # mapping each decision back to its original index
        ordered_decision[original_index] = serve_decision[i]
        ordered_prices[original_index] = price_decision[i]

    return ordered_decision, ordered_prices


# checking boundaries, DRL dispatch decision and energy conservation ? (constraints)
# checking the operational objective (cost) ?
def compute_cost(allocation_decision: np.ndarray, allocation_prices: np.ndarray, objective_func:Optional[Callable]=None):
    """
    This function reflects the optimization objective.
    By default, it computes the "operational cost" (energy flows X energy prices)
    """
    if not objective_func:
        computed_cost = abs(np.dot(allocation_decision, allocation_prices))
    else:
        computed_cost = objective_func(allocation_decision, allocation_prices)

    return computed_cost


# determining fitness
def calculate_fitness(costs: List[float], min_or_max_flag:bool=True) -> np.ndarray:
    """
    This function returns the fitness of each individual of the population.
    """
    costs = np.array(costs)
    if min_or_max_flag:
        global_best = np.min(costs)  # the best solution from the current population (minimization problem by default)
    else:
        global_best = np.max(costs)  # the best solution from the current population (maximization problem)

    fitness = global_best / (costs + 1e-12)  # the fitness vector of the current population

    return fitness


# selection + crossover + mutation processes => replacement of current population => passing to next generation
# selection phase is the same
# crossover phase
def crossover_phase_alpha(parent1: Tuple, parent2: Tuple, crossover_point: int=1, crossover_method: int=0):
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

    return child1, child2


# mutation phase
def creep_mutation_alpha(individual: Tuple, mutation_rate: float, lower_bound:float=-1.0, upper_bound:float=1.0) -> Tuple:
    """
    In this mutation function, a unique and random chromosome is chosen within an individual and its value either de/increases.
    """
    individual = list(individual)
    for index in range(len(individual)):
        if random.random() < mutation_rate:
            mutation_amount = random.uniform(-0.5, 0.5)
            individual[index] += mutation_amount
            # Ensure the individual stays within bounds
            individual[index] = max(min(individual[index], upper_bound), lower_bound)

    return tuple(individual)


def mutation_phase_alpha(next_generation: List, child1: Tuple, child2: Tuple, rate_of_mutation: float, mutation_method: int=3):
    """
    The mutation phase function.
    """
    # mutation_method = random.choice([0, 1, 2, 3])
    if mutation_method == 0:  # creep mutation is used
        next_generation.append(creep_mutation_alpha(child1, rate_of_mutation))
        next_generation.append(creep_mutation_alpha(child2, rate_of_mutation))
    elif mutation_method == 1:  # swap mutation is used
        next_generation.append(swap_mutation(child1, rate_of_mutation))
        next_generation.append(swap_mutation(child2, rate_of_mutation))
    elif mutation_method == 2:  # scramble mutation is used
        next_generation.append(scramble_mutation(child1, rate_of_mutation))
        next_generation.append(scramble_mutation(child2, rate_of_mutation))
    else:  # inversion mutation is used
        next_generation.append(inversion_mutation(child1, rate_of_mutation))
        next_generation.append(inversion_mutation(child2, rate_of_mutation))

    return next_generation



# #####################################################################################################################
# Main Genetic Algorithm loop
#######################################################################################################################
def genetic_algorithm_alpha(full_message: List[Dict], rl_dispatch: float,
                      buying_price: float, selling_price: float,
                      population_size: int, number_of_generations: int, rate_of_mutation: float, tournament_size: int,
                      crossover_point: int = 1, number_of_elites: int = 0,
                      objective_func: Optional[Callable] = None, min_or_max_flag: bool = True):
    """
    The main loop of the genetic algorithm that uses different techniques for selection, crossover and mutation with or without the eliticism mechanism.
    """
    # Initialization of the population for the three sorting functions (consumption, production, storage)
    ####################################################################################################
    # 1 - The demand and offer horizons are determined (forecast, flexibility)
    my_horizon = find_largest_horizon(full_message)

    # 2 - the input is normalized
    input_vector = normalize_my_input(full_message, rl_dispatch, buying_price, selling_price, my_horizon)

    # 3 - finally we generate the populations (individuals consisting of tuples of alpha_i)
    my_population = initialize_my_population(population_size, input_vector)

    # Optimization loop through generations
    for generation in range(number_of_generations):
        # Evaluating the fitness of every individual
        ############################################
        # 1 - the sorting output of each sorting function is determined
        sorted_output = [compute_and_order_output(input_vector, individual) for individual in my_population]

        # 2 - then energy allocation is executed following this order
        my_allocation = [serve_and_execute_order(full_message, rl_dispatch, my_output) for my_output in sorted_output]

        # 3 - the cost is then determined as function of the energy allocated
        my_costs = [compute_cost(tup[0], tup[1], objective_func) for tup in my_allocation]

        # 4 - finally the fitness is computed
        my_fitness = calculate_fitness(my_costs, min_or_max_flag)

        # Replacing population by next generation
        ##################################
        # 1 - perform the selection process
        selected_pop = selection_phase(my_population, my_fitness, tournament_size, number_of_elites, selection_method=0)

        next_generation = []
        for i in range(0, population_size, 2):
            parent1 = selected_pop[i]
            parent2 = selected_pop[i + 1]

            # 2 - perform the crossover process
            child1, child2 = crossover_phase_alpha(parent1, parent2, crossover_point, crossover_method=0)

            # 3 - perform the mutation process
            next_generation = mutation_phase_alpha(next_generation, child1, child2, rate_of_mutation, mutation_method=0)

        # finally the next generation replaces the current population
        my_population = next_generation

    # Final computation of the fitness of the last iteration population
    final_sorted_output = [compute_and_order_output(input_vector, individual) for individual in my_population]
    final_allocation = [serve_and_execute_order(full_message, rl_dispatch, my_output) for my_output in final_sorted_output]
    final_cost = [compute_cost(tup[0], tup[1], objective_func) for tup in final_allocation]
    final_fitness = calculate_fitness(final_cost, min_or_max_flag)
    best_index = int(np.argmax(final_fitness))  # the index corresponding to the best performance

    return my_population[best_index], final_allocation[best_index][0], final_cost[best_index]  # the distribution with the best performance is returned



# #####################################################################################################################
# Optimization of sorting function
#######################################################################################################################
def optimize_sorting_func(demand_full_message: List[Dict], offer_full_message: List[Dict], storage_full_message: List[Dict],
                          rl_cons: float, rl_prod: float, rl_stor: float,
                          buy_p: float, sell_p: float,
                          pop_size: int, genz: int, r_mu: float, tourna_z: int, crs_p: int, numb_el: int,
                          obj_func: Optional[Callable], minmax: bool):
    """
    This function is the one called in DRL_Strategy.top_down method.
    Once training of DRL finishes, 3 sorting functions (storage, consumption & production) are 'trained' per aggregator.
    The "weights" / alpha_i constituting the best individual are then frozen and the sorting functions are used as they are.
    """
    demand_alphas, demand_allocation, demand_cost = genetic_algorithm_alpha(demand_full_message, rl_cons, buy_p, sell_p, pop_size, genz, r_mu, tourna_z, crs_p, numb_el, obj_func, minmax)
    offer_alphas, offer_allocation, offer_cost = genetic_algorithm_alpha(offer_full_message, rl_prod, buy_p, sell_p, pop_size, genz, r_mu, tourna_z, crs_p, numb_el, obj_func, minmax)
    storage_alphas, storage_allocation, storage_cost = genetic_algorithm_alpha(storage_full_message, rl_stor, buy_p, sell_p, pop_size, genz, r_mu, tourna_z, crs_p, numb_el, obj_func, minmax)

    return demand_alphas, offer_alphas, storage_alphas



my_demands = [{"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 120, "price": 0.85, "flexibility": [12, 27, 35, 41], "interruptibility": 1, "coming_volume": 350},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 110, "price": 0.65, "flexibility": [0], "interruptibility": 0, "coming_volume": 0},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 90, "price": 0.75, "flexibility": [0, 0], "interruptibility": 0, "coming_volume": 0},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 150, "price": 0.4, "flexibility": [0, 0, 0], "interruptibility": 0, "coming_volume": 0},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 180, "price": 0.45, "flexibility": [12, 27], "interruptibility": 1, "coming_volume": 500},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 300, "price": 0.25, "flexibility": [27, 35, 41], "interruptibility": 1, "coming_volume": 1000},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 20, "price": 1.05, "flexibility": [0, 0, 0, 0], "interruptibility": 0, "coming_volume": 0},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 45, "price": 0.8, "flexibility": [12, 35, 41], "interruptibility": 1, "coming_volume": 140},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 75, "price": 0.78, "flexibility": [1], "interruptibility": 1, "coming_volume": 270},
              {"type": "standard", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 105, "price": 0.7, "flexibility": [0], "interruptibility": 0, "coming_volume": 0}]

my_offers = [{"type": "standard", "energy_minimum": - 120, "energy_nominal": 0, "energy_maximum": 0, "price": 0.5, "flexibility": [-150, -100], "interruptibility": 1, "coming_volume": - 250},
             {"type": "standard", "energy_minimum": - 110, "energy_nominal": 0, "energy_maximum": 0, "price": 0.69, "flexibility": [-120, -30], "interruptibility": 1, "coming_volume": - 150},
             {"type": "standard", "energy_minimum": - 90, "energy_nominal": 0, "energy_maximum": 0, "price": 0.89, "flexibility": [0], "interruptibility": 0, "coming_volume": 0},
             {"type": "standard", "energy_minimum": - 150, "energy_nominal": 0, "energy_maximum": 0, "price": 0.42, "flexibility": [0], "interruptibility": 0, "coming_volume": 0},
             {"type": "standard", "energy_minimum": - 180, "energy_nominal": 0, "energy_maximum": 0, "price": 0.4, "flexibility": [0, 0], "interruptibility": 0, "coming_volume": 0},
             {"type": "standard", "energy_minimum": - 380, "energy_nominal": 0, "energy_maximum": 0, "price": 0.35, "flexibility": [-1000], "interruptibility": 1, "coming_volume": - 1000},
             {"type": "standard", "energy_minimum": - 20, "energy_nominal": 0, "energy_maximum": 0, "price": 1.05, "flexibility": [0], "interruptibility": 0, "coming_volume": 0}]

my_storage = [{"type": "storage", "energy_minimum": - 120, "energy_nominal": 0, "energy_maximum": 30, "price": 0.1, "state_of_charge": 0.35, "capacity": 1000, "self_discharge_rate": 0.002, "efficiency": 0.89},
              {"type": "storage", "energy_minimum": - 110, "energy_nominal": 0, "energy_maximum": 15, "price": 0.69, "state_of_charge": 0.47, "capacity": 500, "self_discharge_rate": 0.001, "efficiency": 0.91},
              {"type": "storage", "energy_minimum": - 90, "energy_nominal": 0, "energy_maximum": 5, "price": 0.89, "state_of_charge": 0.81, "capacity": 250, "self_discharge_rate": 0.003, "efficiency": 0.73},
              {"type": "storage", "energy_minimum": -150, "energy_nominal": 0, "energy_maximum": 45, "price": 0.42, "state_of_charge": 0.68, "capacity": 1250, "self_discharge_rate": 0.006, "efficiency": 0.61}]

e_con = 850.
e_prod = - 700.
e_sto = - 150.
buy_p = 0.69
sell_p = 0.42

# print(genetic_algorithm_alpha(my_demands, e_con, buy_p, sell_p, 100, 100, 0.86, 25, 2, 10))
# print(genetic_algorithm_alpha(my_offers, e_prod, buy_p, sell_p, 100, 100, 0.86, 25, 2, 10))
# print(genetic_algorithm_alpha(my_storage, e_sto, buy_p, sell_p, 100, 100, 0.86, 25, 2, 10))


