# Exchange strategy: autarky
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_2.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "low_DSM"
sizing = "peak"
panels_and_LCOE = {"elec": {"panels": 22375,
                            "LCOE": 0.213},
                   "heat": {"panels": 9174,
                            "LCOE": {"ST": 0.893,
                                     "HP": 0.165,
                                     "average": 0.349},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)




