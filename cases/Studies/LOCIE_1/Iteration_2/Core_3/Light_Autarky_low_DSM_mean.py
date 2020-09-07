# Exchange strategy: autarky
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_2.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "low_DSM"
sizing = "mean"
panels_and_LCOE = {"elec": {"panels": 7707,
                            "LCOE": 0.101},
                   "heat": {"panels": 3351,
                            "LCOE": {"ST": 0.402,
                                     "HP": 0.123,
                                     "average": 0.181},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)




