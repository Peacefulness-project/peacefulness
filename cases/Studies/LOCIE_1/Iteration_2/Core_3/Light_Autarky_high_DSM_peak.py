# Exchange strategy: autarky
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.Iteration_2.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "high_DSM"
sizing = "peak"
panels_and_LCOE = {"elec": {"panels": 22711,
                            "LCOE": 0.215},
                   "heat": {"panels": 9170,
                            "LCOE": {"ST": 0.810,
                                     "HP": 0.206,
                                     "average": 0.416},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)



