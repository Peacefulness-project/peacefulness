# Exchange strategy: autarky
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_3.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "low_DSM"
sizing = "mean"
panels_and_LCOE = {"elec": {"panels": 7611,
                            "LCOE": 0.105},
                   "heat": {"panels": 3356,
                            "LCOE": {"ST": 0.397,
                                     "HP": 0.125,
                                     "average": 0.182},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)




