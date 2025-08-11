# In this file, a Hybrid Genetic Algorithm Particle Swarm Optimization function is defined to allocate energy resources determined
# at the level of energy areas (aggregators) by the DRL agent to the level of the individual energy systems (devices).
# Aivaliotis-Apostolopoulos P, Loukidis D. Swarming genetic algorithm: A nested fully coupled hybrid of genetic algorithm and particle swarm optimization. PLoS One. 2022
# Hussain et al., 2024, "Crossover-BPSO driven multi-agent technology for managing local energy systems"

# Imports
import numpy as np
from copy import deepcopy
import random
from typing import List, Dict, Tuple
from math import inf


# #####################################################################################################################
# Particle-Swarm Optimization Utilities
#######################################################################################################################
class Particle:
    def __init__(self, sorted_demands: List[Dict]=[], sorted_offers: List[Dict]=[], sorted_storage: List[Dict]=[]
                 , lower_bounds: List=[], upper_bounds: List=[], total_demand: float=0.0, total_offer: float=0.0, total_storage: float=0.0
                 , GA_individual: Tuple=()):
        """
        This class is used to instantiate a particle object.
        Each particle has a position vector which represents a candidate setting of the decision variables of the energy distribution optimization problem.
        """
        # Initializing the position and velocity of the particle
        self.position: tuple
        self.velocity: tuple
        if len(sorted_demands) > 0:  # if PSO is used alone
            self.initialize_particles_from_raw_data(sorted_demands, sorted_offers, sorted_storage, lower_bounds, upper_bounds, total_demand, total_offer, total_storage)
        else:  # if PSO is used in a hybrid manner with GA
            self.position = GA_individual
            self.velocity = tuple(np.zeros(len(self.position)).astype(float))
        # Initializing the best performance/position
        self.best_position = deepcopy(self.position)
        self.best_score = inf

    def initialize_particles_from_raw_data(self, sorted_demands: List[Dict], sorted_offers: List[Dict], sorted_storage: List[Dict], lb: List, ub: List, E_con: float, E_prod: float, E_stor: float):
        position = []
        velocity = []
        for element in [sorted_demands, sorted_offers, sorted_storage]:
            for index in range(len(element)):
                position.append(random.uniform(element[index]["quantity_min"], element[index]["quantity"]))
                velocity.append(random.uniform(element[index]["quantity_min"] - element[index]["quantity"],
                                               element[index]["quantity"] - element[index]["quantity_min"]))

        self.position = tuple(ensure_constraints_pso(np.array(position), lb, ub, E_con, E_prod, E_stor, len(sorted_demands), len(sorted_offers), len(sorted_storage)))
        self.velocity = tuple(velocity)


def bounds_and_weights_and_global(sorted_demands: List[Dict], sorted_offers: List[Dict], sorted_storage: List[Dict]) -> Tuple[List, List, List, Tuple]:
    """
    This function is used to store the energy prices as weights for the cost function (specific to distribution to individual energy systems).
    """
    optimization_prices = []
    Emin = []
    Emax = []
    global_best_position = []
    for element in [sorted_demands, sorted_offers, sorted_storage]:
        for device in element:
            Emin.append(device["quantity_min"])
            Emax.append(device["quantity"])
            optimization_prices.append(device["price"])
            global_best_position.append(random.uniform(device["quantity_min"], device["quantity"]))

    return Emin, Emax, optimization_prices, tuple(global_best_position)


def compute_cost_pso(params: Tuple, prices: List) -> float:
    """
    This function computes the cost based on the energy flow and prices values (specific to distribution to individual energy systems).
    """
    individual = np.array(params)
    weights = np.array(prices)

    return abs(np.dot(individual, weights))


def ensure_constraints_pso(position: np.ndarray, lower_bounds: List, upper_bounds: List,
                           total_demand: float, total_offer: float, total_storage: float,
                           number_of_demands: int, number_of_offers: int, number_of_storage: int,
                           tolerance:float=1e-6, max_iter:int=10) -> np.ndarray:
    """
    This function ensures that each decision variable is inside the feasible interval.
    """
    position -= sum(position) / position.size

    # Individual energy systems upper/lower bounds constraint
    position = np.clip(position, np.array(lower_bounds), np.array(upper_bounds))

    # Energy conservation constraint
    offset = sum(position)

    # DRL energy dispatch constraint
    cons_offset = sum(position[: number_of_demands]) - total_demand
    prod_offset = sum(position[number_of_demands : number_of_demands + number_of_offers]) - total_offer
    stor_offset = sum(position[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage]) - total_storage

    iteration = 0

    while abs(offset) > tolerance and iteration < max_iter:
        # flexible demand units
        free_demands = np.where((position[: number_of_demands] > np.array(lower_bounds[: number_of_demands])) & (position[: number_of_demands] < np.array(upper_bounds[: number_of_demands])))[0]
        if free_demands.size != 0 and abs(cons_offset) > tolerance:
            position[free_demands] -= cons_offset / free_demands.size
        # flexible offer units
        free_offers = np.where((position[number_of_demands : number_of_demands + number_of_offers] > np.array(lower_bounds[number_of_demands : number_of_demands + number_of_offers])) & (position[number_of_demands : number_of_demands + number_of_offers] < np.array(upper_bounds[number_of_demands : number_of_demands + number_of_offers])))[0]
        if free_offers.size != 0 and abs(prod_offset) > tolerance:
            position[free_offers + number_of_demands] -= prod_offset / free_offers.size
        # flexible storage units
        free_storage = np.where((position[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage] > np.array(lower_bounds[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage])) & (position[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage] < np.array(upper_bounds[number_of_demands + number_of_offers : number_of_demands + number_of_offers + number_of_storage])))[0]
        if free_storage.size != 0 and abs(stor_offset) > tolerance:
            position[free_storage + number_of_demands + number_of_offers] -= stor_offset / free_storage.size

        # indices that are not at bounds (free to change)
        free = np.where((position > np.array(lower_bounds)) & (position < np.array(upper_bounds)))[0]
        if free.size == 0:
            break  # can't redistribute further
        offset = sum(position)
        position[free] -= offset / free.size
        position = np.clip(position, np.array(lower_bounds), np.array(upper_bounds))

        # checking for the next iteration
        offset = sum(position)
        cons_offset = sum(position[: number_of_demands]) - total_demand
        prod_offset = sum(position[number_of_demands: number_of_demands + number_of_offers]) - total_offer
        stor_offset = sum(position[number_of_demands + number_of_offers: number_of_demands + number_of_offers + number_of_storage]) - total_storage
        iteration += 1

    # If still outside tolerance, try to absorb residual into a single variable if possible
    if abs(cons_offset) > tolerance:
        # look for any index where moving it by -residual keeps it within bounds
        for index in range(number_of_demands):
            new_val = position[index] - cons_offset
            if np.array(lower_bounds)[index] <= new_val <= np.array(upper_bounds)[index]:
                position[index] = new_val
                break

    if abs(prod_offset) > tolerance:
        # look for any index where moving it by -residual keeps it within bounds
        for index in range(number_of_offers):
            new_val = position[index + number_of_demands] - prod_offset
            if np.array(lower_bounds)[index + number_of_demands] <= new_val <= np.array(upper_bounds)[index + number_of_demands]:
                position[index + number_of_demands] = new_val
                break

    if abs(stor_offset) > tolerance:
        # look for any index where moving it by -residual keeps it within bounds
        for index in range(number_of_storage):
            new_val = position[index + number_of_demands + number_of_offers] - stor_offset
            if np.array(lower_bounds)[index + number_of_demands + number_of_offers] <= new_val <= np.array(upper_bounds)[index + number_of_demands + number_of_offers]:
                position[index + number_of_demands + number_of_offers] = new_val
                break

    if abs(offset) > tolerance:
        # look for any index where moving it by -residual keeps it within bounds
        for index in range(position.size):
            new_val = position[index] - offset
            if np.array(lower_bounds)[index] <= new_val <= np.array(upper_bounds)[index]:
                position[index] = new_val
                break

    return position


def update_particles(particles: List[Particle], global_best_position: Tuple, w: float, c1: float, c2: float,
                     Emin: List[float], Emax: List[float], prices: List[float],
                     E_con: float, E_prod: float, E_stor: float, len_con: int, len_prod: int, len_stor: int
                     , crossover_alpha: float=0.0, crossover_prob: float=0.0):
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
        # particle.position = np.clip(particle.position, 0, 1)
        particle.position = tuple(ensure_constraints_pso(particle.position, Emin, Emax, E_con, E_prod, E_stor, len_con, len_prod, len_stor))
        particle.velocity = tuple(particle.velocity)

        # Evaluate the new position
        score = compute_cost_pso(particle.position, prices)

        # Update the particle's best known position and score
        if score < particle.best_score:
            particle.best_position = deepcopy(particle.position)
            particle.best_score = deepcopy(score)


def apply_linear_damping(w_start: float, w_end: float, current_iter: int, max_iter: int) -> float:
    """
    This function applies linear decay to the inertia coefficient w.r.t number of optimization iterations.
    """
    return w_start - (w_start - w_end) * (current_iter / max_iter)


def apply_geometric_decay(w_start: float, w_end: float, current_iter: int, max_iter: int) -> float:
    """
    This function applies geometric decay (power-law schedule) to the inertia coefficient w.r.t number of optimization iterations.
    """
    return w_start * (w_end / w_start) ** (current_iter / max_iter)



# #####################################################################################################################
# Main Particle-Swarm Optimization loop
#######################################################################################################################
def particle_swarm_optimization(sorted_demands: List[Dict], sorted_offers: List[Dict], sorted_storage: List[Dict],
                                number_of_particles: int, optimization_iterations: int, personal_coefficient: float, social_coefficient: float,
                                inertia_coefficient: float, energy_demand: float, energy_generation: float, energy_storage: float,
                                min_inertia: float=0.0, geometric_or_linear:int=0) -> Tuple:
    """
    The main loop of the particle swarm optimization.
    """
    # Initialize particles
    lower_bounds, upper_bounds, weights, global_best_position = bounds_and_weights_and_global(sorted_demands, sorted_offers, sorted_storage)
    particles = [Particle(sorted_demands, sorted_offers, sorted_storage, lower_bounds, upper_bounds, energy_demand, energy_generation, energy_storage) for _ in range(number_of_particles)]
    global_best_score = inf


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
        update_particles(particles, global_best_position, w, personal_coefficient, social_coefficient, lower_bounds, upper_bounds, weights,
                         energy_demand, energy_generation, energy_storage, len(sorted_demands), len(sorted_offers), len(sorted_storage))

        # Updating the global score and position
        for particle in particles:
            score = compute_cost_pso(particle.position, weights)
            if score < global_best_score:
                global_best_position = deepcopy(particle.position)
                global_best_score = score

    return global_best_position


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
# print(particle_swarm_optimization(my_demands, my_offers, my_storage, 100, 100,
#                                   0.35, 0.45, 0.55,
#                                   e_con, e_prod, e_sto,
#                                   # 0.21, 1
#                                   ))

