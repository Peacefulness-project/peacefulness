# Exchange strategy: profitable
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.FigureRuns.WeekConsumptionFinal.Script import simulation

# parameters
chosen_strategy = "Profitable"
DSM_proportion = "high_DSM"
sizing = "peak"
panels_and_LCOE = {"elec": {"panels": 24383,
                            "LCOE": 0.233},
                   "heat": {"panels": 9170,
                            "LCOE": {"ST": 0.851,
                                     "HP": 0.213,
                                     "average": 0.430},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)



