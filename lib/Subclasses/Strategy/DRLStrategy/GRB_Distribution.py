# In this file, a Gurobi-based optimization function is defined to allocate energy resources determined at the level of
# energy areas (aggregators) by the DRL agent to the level of the individual energy systems (devices).


# Imports
from typing import List
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import scipy.sparse as sp

def optimization_distribution(sorted_demands: List, sorted_offers: List, sorted_storage: List,
                              E_con: float, E_prod: float, E_sto: float) -> List:
    """
    Optimization of the distribution of energy to devices.
    """
    # Initialization
    Emax = []
    Emin = []
    optimization_prices = []
    for element in [sorted_demands, sorted_offers, sorted_storage]:
        for device in element:
            Emax.append(device["quantity"])
            optimization_prices.append(device["price"])
            if device["type"] == "storage" or device["type"] == "offer":
                Emin.append(device["quantity_min"])
            else:
                Emin.append(0.0)
    lower_bounds = np.array(Emin)
    upper_bounds = np.array(Emax)
    obj_coef = np.array(optimization_prices)

    # Solving
    try:
        # Creating the GRB optimization model object
        distribution = gp.Model()
        # distribution.setParam('TimeLimit', 60)

        # Adding decision variables to the model
        decision_variables = distribution.addMVar(shape=len(sorted_demands) + len(sorted_offers) + len(sorted_storage),
                                 lb=lower_bounds, ub=upper_bounds,
                                 vtype=GRB.CONTINUOUS,
                                 name="DV")

        # Adding constraints to the model
        equal_val = np.ones(len(sorted_demands) + len(sorted_offers) + len(sorted_storage))
        equal_row = ([0] * len(sorted_demands) + [1] * len(sorted_offers) + [2] * len(sorted_storage))
        equal_col = (list(range(0,len(sorted_demands)))
                     + list(range(len(sorted_demands), len(sorted_demands) + len(sorted_offers)))
                     + list(range(len(sorted_demands) + len(sorted_offers), len(sorted_demands) + len(sorted_offers) + len(sorted_storage))))
        equal_shape = (3, len(sorted_demands) + len(sorted_offers) + len(sorted_storage))
        equal_coef = sp.csr_matrix((equal_val, (equal_row, equal_col)), shape=equal_shape)  # sparse constraint matrix
        equal_rhs = np.array([E_con, E_prod, E_sto])  # right-hand side of the equality constraints
        distribution.addConstr(equal_coef @ decision_variables == equal_rhs, name="equalities")

        # Setting the optimization objective
        distribution.setObjective(obj_coef @ decision_variables, GRB.MINIMIZE)  # the energy cost of consumers, producers and storage

        # Optimizing
        distribution.optimize()

    except gp.GurobiError as e:
        print(f"Error code {e.errno}: {e}")

    return decision_variables.X

#
# my_demands = [{"type": "demand", "quantity": 120, "price": 0.85}, {"type": "demand", "quantity": 110, "price": 0.65},
#               {"type": "demand", "quantity": 90, "price": 0.75},
#               {"type": "demand", "quantity": 150, "price": 0.4}, {"type": "demand", "quantity": 180, "price": 0.45},
#               {"type": "demand", "quantity": 300, "price": 0.25}, {"type": "demand", "quantity": 20, "price": 1.05},
#               {"type": "demand", "quantity": 45, "price": 0.8}, {"type": "demand", "quantity": 75, "price": 0.78},
#               {"type": "demand", "quantity": 105, "price": 0.7}]
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
# print(optimization_distribution(my_demands, my_offers, my_storage, e_con, e_prod, e_sto))


