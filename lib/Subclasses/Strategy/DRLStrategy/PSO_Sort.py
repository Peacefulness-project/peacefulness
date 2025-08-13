# Here we are optimizing the coefficients alpha_i of a sorting function based on the particle swarm optimization algorithm.


# Imports
from typing import Callable, Optional, Any
from PSO_Distribution import *
from GA_Sort import find_largest_horizon, normalize_my_input, compute_and_order_output, serve_and_execute_order, compute_cost


# initialize particles - positions and velocities
# compute new velocities
# update positions
# find best performance


# #####################################################################################################################
# Particle-Swarm Optimization Utilities
#######################################################################################################################
class alpha_Particle:
    def __init__(self, normalized_input: List[Tuple]=[], lower_bound:float= - 1.0, upper_bound:float= 1.0, GA_individual: Tuple=()):
        """
        This class is used to instantiate a particle object (alpha_i).
        Each particle has a position vector which represents a candidate setting of the decision variables of the energy distribution optimization problem.
        In here the position is constituted by the alpha_i of the sorting functions.
        """
        # Initializing the position and velocity of the particle
        self.position: tuple
        self.velocity: tuple
        if GA_individual:  # if PSO is used in a hybrid manner with GA
            self.position = GA_individual
            self.velocity = tuple(np.zeros(len(self.position)).astype(float))
        else:  # if PSO is used alone
            self.initialize_alpha_particles(normalized_input, lower_bound, upper_bound)
        # Initializing the best performance/position
        self.best_position = deepcopy(self.position)
        self.best_score = inf

    def initialize_alpha_particles(self, processed_message: List[Tuple], lower_bound:float= - 1.0, upper_bound:float= 1.0):
        position = []
        velocity = []
        for _ in range(len(processed_message[0])):
            position.append(random.uniform(lower_bound, upper_bound))
            velocity.append(random.uniform(lower_bound - upper_bound, upper_bound - lower_bound))

        self.position = tuple(position)
        self.velocity = tuple(velocity)



def update_position_and_velocity(full_message: List[Dict], dispatch_RL: float, normalized_input: List[Tuple], particles: List[alpha_Particle], global_best_position: Tuple,
                                 w: float, c1: float, c2: float,
                                 minmax_flag: bool, crossover_alpha: float=0.0, crossover_prob: float=0.0,
                                 objective_func:Optional[Callable]=None):
    """
    Updating the position and velocity of each particle according to the PSO formula.
    """
    for particle in particles:
        r1, r2 = np.random.rand(len(particle.position)), np.random.rand(len(particle.position))

        # Compute velocity
        if crossover_alpha == 0:  # normal PSO
            particle.velocity = (w * np.array(particle.velocity)
                                + c1 * r1 * (np.array(particle.best_position) - np.array(particle.position))
                                + c2 * r2 * (np.array(global_best_position) - np.array(particle.position)))
        else:  # cr-PSO update
            coin_flip = np.random.binomial(n=1, p=crossover_prob)  # Bernoulli trial
            if coin_flip == 1:
                crossover_velocity = r1 * (np.array(particle.best_position) - np.array(particle.position))
            else:
                crossover_velocity = r2 * (np.array(global_best_position) - np.array(particle.position))
            particle.velocity =  np.array(particle.velocity) + crossover_alpha * crossover_velocity

        # Compute position
        particle.position = np.array(particle.position) + particle.velocity
        particle.position = tuple(particle.position)
        particle.velocity = tuple(particle.velocity)

        # Evaluate the new position
        sorted_output = compute_and_order_output(normalized_input, particle.position)
        my_allocation = serve_and_execute_order(full_message, dispatch_RL, sorted_output)
        score = compute_cost(my_allocation[0], my_allocation[1], objective_func)

        # Update the particle's best known position and score
        if minmax_flag:  # the best solution from this particle (minimization problem by default)
            if score < particle.best_score:
                particle.best_position = deepcopy(particle.position)
                particle.best_score = deepcopy(score)
        else:  # the best solution from this particle (maximization problem)
            if score > particle.best_score:
                particle.best_position = deepcopy(particle.position)
                particle.best_score = deepcopy(score)


def compute_scores(full_message: List[Dict], dispatch_RL: float, normalized_input: List[Tuple], particles: List[alpha_Particle], objective_func:Optional[Callable]=None) -> Tuple[List, Any]:
    """
    Computing the scores obtained by the particles.
    """
    # 1 - the sorting output of each sorting function is determined
    sorted_output = [compute_and_order_output(normalized_input, particle.position) for particle in particles]

    # 2 - then energy allocation is executed following this order
    my_allocation = [serve_and_execute_order(full_message, dispatch_RL, my_output) for my_output in sorted_output]

    # 3 - the cost is then determined as function of the energy allocated
    scores = [compute_cost(tup[0], tup[1], objective_func) for tup in my_allocation]

    return scores, my_allocation[0]


def evaluate_position(particles: List[alpha_Particle], performance: List[float], minmax_flag: bool) -> Tuple[Tuple, float, int]:
    """
    This function is used to evaluate the performance of the positions attained by the particles.
    """
    if minmax_flag:  # the best solution from the current population (minimization problem by default)
        best_idx = np.argmin(performance)
    else:  # the best solution from the current population (maximization problem by default)
        best_idx = np.argmax(performance)

    return particles[best_idx].position, performance[best_idx], int(best_idx)



# #####################################################################################################################
# Main Particle-Swarm Optimization loop
#######################################################################################################################
def alpha_particle_swarm_optimization(full_message: List[Dict], rl_dispatch: float, buying_price: float, selling_price: float,
                                number_of_particles: int, optimization_iterations: int,
                                inertia_coefficient: float, personal_coefficient: float, social_coefficient: float,
                                min_inertia: float=0.0, geometric_or_linear:int=0,
                                objective_func: Optional[Callable] = None, min_or_max_flag: bool = True) -> Tuple:
    """
    The main loop of the particle swarm optimization.
    """
    # Initialization of the particles for the three sorting functions (consumption, production, storage)
    ####################################################################################################
    # 1 - the demand and offer horizons are determined (forecast, flexibility)
    my_horizon = find_largest_horizon(full_message)

    # 2 - the input is normalized
    input_vector = normalize_my_input(full_message, rl_dispatch, buying_price, selling_price, my_horizon)

    # 3 - finally we generate the particles (individuals consisting of tuples of alpha_i)
    my_particles = [alpha_Particle(input_vector) for _ in range(number_of_particles)]

    # 4 - initializing the global best position and global best score
    my_scores, my_distributions = compute_scores(full_message, rl_dispatch, input_vector, my_particles, objective_func)
    global_best_position, global_best_score, best_idx = evaluate_position(my_particles, my_scores, min_or_max_flag)


    # Optimization loop
    for i in range(optimization_iterations):
        # Computing the inertia coefficient
        if geometric_or_linear == 0:
            w = inertia_coefficient
        elif geometric_or_linear == 1:  # linear damping is used to compute the inertia coefficient
            w = apply_linear_damping(inertia_coefficient, min_inertia, i, optimization_iterations)
        else:  # geometric damping is used to compute the inertia coefficient
            w = apply_geometric_decay(inertia_coefficient, min_inertia, i, optimization_iterations)

        # Updating each particle position and velocity
        update_position_and_velocity(full_message, rl_dispatch, input_vector, my_particles, global_best_position,
                                     w, personal_coefficient, social_coefficient, min_or_max_flag,
                                     crossover_prob=0, crossover_alpha=0, objective_func=objective_func)

        # Updating the global score and position
        my_scores, my_distributions = compute_scores(full_message, rl_dispatch, input_vector, my_particles, objective_func)
        global_best_position, global_best_score, best_idx = evaluate_position(my_particles, my_scores, min_or_max_flag)


    return global_best_position, my_distributions[best_idx], global_best_score





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


# print(alpha_particle_swarm_optimization(my_demands, e_con, buy_p, sell_p,100, 100, 0.81, 0.69, 0.42))
# print(alpha_particle_swarm_optimization(my_offers, e_prod, buy_p, sell_p,100, 100, 0.81, 0.69, 0.42))
# print(alpha_particle_swarm_optimization(my_storage, e_sto, buy_p, sell_p,100, 100, 0.81, 0.69, 0.42))

