# Exchange strategy: profitable
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_3.Script import simulation

# parameters
chosen_strategy = "Profitable"
DSM_proportion = "high_DSM"
sizing = "mean"
panels_and_LCOE = {"elec": {"panels": 6396,
                            "LCOE": 0.102},
                   "heat": {"panels": 2630,
                            "LCOE": {"ST": 0.317,
                                     "HP": 0.152,
                                     "average": 0.194},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)



