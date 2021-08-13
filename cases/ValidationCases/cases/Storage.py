# This script checks that storage devices are working well.

# ##############################################################################################
# Importations
from datetime import datetime

from os import chdir

from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger
from src.common.Nature import Nature
from src.common.World import World

from src.tools.GraphAndTex import GraphOptions
from src.tools.SubclassesDictionary import get_subclasses


# ##############################################################################################
# Minimum
# the following objects are necessary for the simulation to be performed
# you need exactly one object of each type
# ##############################################################################################

# ##############################################################################################
# Importation of subclasses
# all the subclasses are imported in the following dictionary
subclasses_dictionary = get_subclasses()

# ##############################################################################################
# Creation of the world
# a world contains all the other elements of the model
# a world needs just a name
name_world = "validation"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
world.set_directory("cases/ValidationCases/Results/Storage")  # here, you have to put the path to your results directory


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("seed")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24)  # number of time steps simulated


# ##############################################################################################
# Model
# ##############################################################################################

# ##############################################################################################
# Creation of nature
# low voltage electricity
LVE = load_low_voltage_electricity()

# low temperature heat
LTH = load_low_temperature_heat()

# ##############################################################################################
# Creation of daemons
price_manager_TOU_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.1, 0.2], "selling_price": [0.1, 0.2], "on-peak_hours": [[12, 24]]})  # sets prices for TOU rate
price_manager_TOU_heat = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_heat", {"nature": LTH.name, "buying_price": [0.1, 0.2], "selling_price": [0.1, 0.2], "on-peak_hours": [[12, 24]]})  # sets prices for TOU rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator
subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "validation"}, filename="cases/ValidationCases/AdditionalData/Meteo/TemperatureProfiles.json")

# ##############################################################################################
# Creation of strategies

# BAU strategy
BAU_strategy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
battery_owner_no_degradation = Agent("battery_owner_no_degradation")
battery_owner_degradation = Agent("battery_owner_degradation")

sensible_owner_no_degradation = Agent("sensible_owner_no_degradation")
sensible_owner_degradation = Agent("sensible_owner_degradation")

latent_owner_no_degradation = Agent("latent_owner_no_degradation")
latent_owner_degradation = Agent("latent_owner_degradation")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
threshold_contract_elec = subclasses_dictionary["Contract"]["StorageThresholdPricesContract"]("threshold_contract_elec", LVE, price_manager_TOU_elec, {"buying_threshold": 0.1, "selling_threshold": 0.2})
threshold_contract_heat = subclasses_dictionary["Contract"]["StorageThresholdPricesContract"]("threshold_contract_heat", LTH, price_manager_TOU_heat, {"buying_threshold": 0.1, "selling_threshold": 0.2})


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_elec = Aggregator("aggregator_elec", LVE, BAU_strategy, aggregators_manager, aggregator_grid, threshold_contract_elec)

aggregator_heat = Aggregator("aggregator_heat", LTH, BAU_strategy, aggregators_manager, aggregator_grid, threshold_contract_heat)


# ##############################################################################################
# Manual creation of devices
subclasses_dictionary["Device"]["ElectricalBattery"]("battery_charge_and_discharge", threshold_contract_elec, battery_owner_no_degradation, aggregator_elec, {"device": "battery_no_degradation"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/ElectricalBattery.json")
subclasses_dictionary["Device"]["ElectricalBattery"]("battery_degradation", threshold_contract_elec, battery_owner_degradation, aggregator_elec, {"device": "battery_degradation"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/ElectricalBattery.json")

subclasses_dictionary["Device"]["SensibleHeatStorage"]("sensible_charge_and_discharge", threshold_contract_heat, sensible_owner_no_degradation, aggregator_heat, {"device": "water_tank_no_degradation"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/SensibleHeatStorage.json")
subclasses_dictionary["Device"]["SensibleHeatStorage"]("sensible_degradation", threshold_contract_heat, sensible_owner_degradation, aggregator_heat, {"device": "water_tank_degradation"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/SensibleHeatStorage.json")

subclasses_dictionary["Device"]["LatentHeatStorage"]("latent_charge_and_discharge", threshold_contract_heat, latent_owner_no_degradation, aggregator_heat, {"device": "tank_no_degradation"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/LatentHeatStorage.json")
subclasses_dictionary["Device"]["LatentHeatStorage"]("latent_degradation", threshold_contract_heat, latent_owner_degradation, aggregator_heat, {"device": "tank_degradation"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/LatentHeatStorage.json")

# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that storage devices are working well."

filename = "storage_validation"

reference_values = {"battery_owner_no_degradation.LVE.energy_bought": [1, 1, 1, 1, 1, 1, 2/3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "battery_owner_no_degradation.LVE.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "battery_charge_and_discharge.energy_stored": [5.75, 6.5, 7.25, 8, 8.75, 9.5, 10, 10, 10, 10, 10, 10, 6, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],

                    "battery_owner_degradation.LVE.energy_bought": [2, 2, 2, 1.477, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "battery_owner_degradation.LVE.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0.87, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "battery_degradation.energy_stored": [6.3, 7.47, 8.523, 9, 9, 9, 9, 9, 9, 9, 9, 9, 6.3, 3.87, 2.7, 2.43, 2.187, 1.9683, 1.77147, 1.594323, 1.4348907, 1.29140163, 1.162261467, 1.0460353203],

                    "sensible_owner_no_degradation.LTH.energy_bought": [2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "sensible_owner_no_degradation.LTH.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 2, 0, 0, 0, 0, 0],
                    "sensible_charge_and_discharge.energy_stored": [325.15, 327.15, 329.15, 331.15, 333.15, 333.15, 333.15, 333.15, 333.15, 333.15, 333.15, 333.15, 330.15, 327.15, 324.15, 321.15, 318.15, 315.15, 313.15, 313.15, 313.15, 313.15, 313.15, 313.15],

                    "sensible_owner_degradation.LTH.energy_bought": [4, 4, 4, 4, 3.322225, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "sensible_owner_degradation.LTH.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 1.640284375, 0, 0, 0, 0, 0, 0, 0],
                    "sensible_degradation.energy_stored": [324.95, 326.66, 328.2845, 329.827775, 330.65, 330.65, 330.65, 330.65, 330.65, 330.65, 330.65, 330.65, 326.375, 322.31375, 318.4555625, 314.790284375, 311.65, 310.225, 308.87125, 307.5851875, 306.363428125, 305.20275671875, 304.10011888281247, 303.0526129386718],

                    # "latent_owner_no_degradation.LTH.energy_bought": [1, 1, 1, 1, 1, 1, 2/3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    # "latent_owner_no_degradation.LTH.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    # "latent_charge_and_discharge.energy_stored": [5.75, 6.5, 7.25, 8, 8.75, 9.5, 10, 10, 10, 10, 10, 10, 6, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                    #
                    # "latent_owner_degradation.LTH.energy_bought": [2, 2, 2, 1.477, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    # "latent_owner_degradation.LTH.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0.87, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    # "latent_degradation.energy_stored": [6.3, 7.47, 8.523, 9, 9, 9, 9, 9, 9, 9, 9, 9, 6.3, 3.87, 2.7, 2.43, 2.187, 1.9683, 1.77147, 1.594323, 1.4348907, 1.29140163, 1.162261467, 1.0460353203],
                    }

name = "battery_behavior_without_degradation"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "battery_owner_no_degradation.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "battery_owner_no_degradation.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."},
                      {"catalog_name_entry": "battery_owner_no_degradation.LVE.energy_sold_simulation", "style": "points", "legend": r"num."},
                      {"catalog_name_entry": "battery_owner_no_degradation.LVE.energy_sold_simulation", "style": "lines", "legend": r"num."}]
}
}

# name = "Bought_Energy_LVE-Converter-Owner"
# export_plot2 = {
#     "name": name,
#     "filename": "export_"+name,
#     "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
#     "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
#     "Y": {"label": r"$\mathcal{C} \, [$\euro{}$]$",
#           "graphs": [ {"catalog_name_entry": "converter_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
#                       {"catalog_name_entry": "converter_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."} ]
#           }
# }
#
# name = "Sold_Energy_LTH-Converter-Owner"
# export_plot3 = {
#     "name": name,
#     "filename": "export_"+name,
#     "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
#     "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
#     "Y": {"label": r"$\mathcal{C} \, [$\euro{}$]$",
#           "graphs": [ {"catalog_name_entry": "converter_owner.LTH.energy_sold_reference", "style": "points", "legend": r"ref."},
#                       {"catalog_name_entry": "converter_owner.LTH.energy_sold_simulation", "style": "lines", "legend": r"num"},
#                       ]
#           }
# }
#
# name = "Balance_Bought_Sold_Energy_Alltogether"
# export_plot4 = {
#     "name": name,
#     "filename": "export_"+name,
#     "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
#     "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
#     "Y": {"label": r"$\mathcal{C}_{ref.} \, [$\euro{}$]$",
#           "graphs": [ {"catalog_name_entry": "background_owner.LTH.energy_bought_reference", "style": "points", "legend": r"$\textrm{LTH}_\textrm{bckgd}^{\textrm{bought}}$"},
#                       {"catalog_name_entry": "converter_owner.LVE.energy_bought_reference", "style": "points", "legend": r"$\textrm{LVE}_\textrm{conv}^{\textrm{bought}}$"},
#                       {"catalog_name_entry": "converter_owner.LTH.energy_sold_reference", "style": "points", "legend": r"$\textrm{LTH}_\textrm{conv}^{\textrm{sold}}$"}
#                       ]
#           },
#     "Y2": {"label": r"$\mathcal{C}_{num.} \, [$\euro{}$]$",
#           "graphs": [ {"catalog_name_entry": "background_owner.LTH.energy_bought_simulation", "style": "lines", "legend": r""},
#                       {"catalog_name_entry": "converter_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
#                       {"catalog_name_entry": "converter_owner.LTH.energy_sold_simulation", "style": "lines", "legend": r""}
#                       ]
#           }
# }

parameters = {"description": description, "filename": filename, "reference_values": reference_values, "tolerance": 1E-6, "export_plots": [export_plot1]}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("storage_test", parameters)


# ##############################################################################################
# Simulation start
world.start()






