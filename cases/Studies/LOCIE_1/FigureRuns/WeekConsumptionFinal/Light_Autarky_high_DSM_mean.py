# Exchange strategy: autarky
# Contract: 33 Normal, 40 DLC, 27 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.FigureRuns.WeekConsumptionFinal.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "high_DSM"
sizing = "mean"
panels_and_LCOE = {"elec": {"panels": 6396,
                            "LCOE": 0.102},
                   "heat": {"panels": 2631,
                            "LCOE": {"ST": 0.296,
                                     "HP": 0.159,
                                     "average": 0.198},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)








