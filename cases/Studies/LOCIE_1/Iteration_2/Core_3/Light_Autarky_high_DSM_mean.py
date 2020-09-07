# Exchange strategy: autarky
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_2.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "high_DSM"
sizing = "mean"
panels_and_LCOE = {"elec": {"panels": 6623,
                            "LCOE": 0.095},
                   "heat": {"panels": 2628,
                            "LCOE": {"ST": 0.312,
                                     "HP": 0.155,
                                     "average": 0.197},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)








