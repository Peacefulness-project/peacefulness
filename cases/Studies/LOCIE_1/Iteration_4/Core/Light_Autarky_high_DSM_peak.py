# Exchange strategy: autarky
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_4.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "high_DSM"
sizing = "peak"
panels_and_LCOE = {"elec": {"panels": 22553,
                            "LCOE": 0.224},
                   "heat": {"panels": 9170,
                            "LCOE": {"ST": 0.835,
                                     "HP": 0.210,
                                     "average": 0.425},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)



