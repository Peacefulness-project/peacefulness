# Exchange strategy: profitable
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_2.Script import simulation

# parameters
chosen_strategy = "Profitable"
DSM_proportion = "low_DSM"
sizing = "mean"
panels_and_LCOE = {"elec": {"panels": 8705,
                            "LCOE": 0.108},
                   "heat": {"panels": 4034,
                            "LCOE": {"ST": 0.529,
                                     "HP": 0.106,
                                     "average": 0.173},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)



