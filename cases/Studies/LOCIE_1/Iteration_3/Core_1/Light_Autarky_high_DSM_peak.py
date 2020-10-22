# Exchange strategy: autarky
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_3.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "high_DSM"
sizing = "peak"
panels_and_LCOE = {"elec": {"panels": 9170,
                            "LCOE": 0.232},
                   "heat": {"panels": 22395,
                            "LCOE": {"ST": 0.851,
                                     "HP": 0.213,
                                     "average": 0.430},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)



