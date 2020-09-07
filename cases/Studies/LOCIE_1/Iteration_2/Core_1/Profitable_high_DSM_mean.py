# Exchange strategy: profitable
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_2.Script import simulation

# parameters
chosen_strategy = "Profitable"
DSM_proportion = "high_DSM"
sizing = "mean"
panels_and_LCOE = {"elec": {"panels": 8622,
                            "LCOE": 0.108},
                   "heat": {"panels": 4028,
                            "LCOE": {"ST": 0.530,
                                     "HP": 0.106,
                                     "average": 0.173},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)



