# Exchange strategy: autarky
# Contract: 100 Normal, 0 DLC, 0 Curtailment
# renewable sizing: mean


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.FigureRuns.WeekConsumptionFinal.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "no_DSM"
sizing = "mean"
panels_and_LCOE = {"elec": {"panels": 8617,
                            "LCOE": 0.108},
                   "heat": {"panels": 4016,
                            "LCOE": {"ST": 0.535,
                                     "HP": 0.106,
                                     "average": 0.174},
                            }
                   }
# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)




