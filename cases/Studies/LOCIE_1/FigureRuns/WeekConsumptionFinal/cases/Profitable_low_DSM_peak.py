# Exchange strategy: profitable
# Contract: 50 Normal, 33 DLC, 17 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.FigureRuns.WeekConsumptionFinal.Script import simulation

# parameters
chosen_strategy = "Profitable"
DSM_proportion = "low_DSM"
sizing = "peak"
panels_and_LCOE = {"elec": {"panels": 24725,
                            "LCOE": 0.234},
                   "heat": {"panels": 9174,
                            "LCOE": {"ST": 0.852,
                                     "HP": 0.213,
                                     "average": 0.43},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)



