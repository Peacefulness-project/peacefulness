# Exchange strategy: autarky
# Contract: 100 Normal, 0 DLC, 0 Curtailment
# renewable sizing: peak


# ##############################################################################################
# Initialization
# ##############################################################################################
# Importation
from cases.Studies.LOCIE_1.FigureRuns.WeekConsumptionFinal.Script import simulation

# parameters
chosen_strategy = "Autarky"
DSM_proportion = "no_DSM"
sizing = "peak"
panels_and_LCOE = {"elec": {"panels": 24536,
                            "LCOE": 0.232},
                   "heat": {"panels": 9170,
                            "LCOE": {"ST": 1.056,
                                     "HP": 0.150,
                                     "average": 0.315},
                            }
                   }

# simulation
world = simulation(chosen_strategy, DSM_proportion, sizing, panels_and_LCOE)




