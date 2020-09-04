# This script checks that distribution strategies work

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

from src.tools.GraphAndTex import graph_options
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
world.set_directory("cases/ValidationCases/Results/DistributionStrategy")  # here, you have to put the path to your results directory


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


# ##############################################################################################
# Creation of daemons
price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices", {"nature": LVE.name, "buying_price": 0, "selling_price": 0})  # sets prices for flat rate
price_manager_elec_expensive = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("expensive_prices", {"nature": LVE.name, "buying_price": 1, "selling_price": 0})  # sets prices for flat rate

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 1})  # sets prices for the system operator

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "Pau"}, "cases/ValidationCases/AdditionalData/Meteo/ColdWaterTemperatureProfiles.json")

# ##############################################################################################
# Creation of strategies
# the different distribution strategies
strategy_emergency = subclasses_dictionary["Strategy"]["AutarkyEmergency"]()
strategy_price = subclasses_dictionary["Strategy"]["AutarkyPrice"]()
strategy_quantity = subclasses_dictionary["Strategy"]["AutarkyQuantity"]()
strategy_partial = subclasses_dictionary["Strategy"]["AutarkyPartial"]()

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
early_emergency_owner = Agent("early_emergency_owner")
expensive_emergency_owner = Agent("expensive_emergency_owner")
consuming_emergency_owner = Agent("consuming_emergency_owner")

early_price_owner = Agent("early_price_owner")
expensive_price_owner = Agent("expensive_price_owner")
consuming_price_owner = Agent("consuming_price_owner")

early_quantity_owner = Agent("early_quantity_owner")
expensive_quantity_owner = Agent("expensive_quantity_owner")
consuming_quantity_owner = Agent("consuming_quantity_owner")

early_partial_owner = Agent("early_partial_owner")
expensive_partial_owner = Agent("expensive_partial_owner")
consuming_partial_owner = Agent("consuming_partial_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
elec_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("elec_contract", LVE, price_manager_elec)

elec_expensive_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("elec_expensive_contract", LVE, price_manager_elec_expensive)

producer_elec_contract = subclasses_dictionary["Contract"]["CurtailmentContract"]("producer_elec_contract", LVE, price_manager_elec)

# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_elec_emergency = Aggregator("local_grid_emergency", LVE, strategy_emergency, aggregators_manager, aggregator_grid, elec_contract)
aggregator_elec_price = Aggregator("local_grid_price", LVE, strategy_price, aggregators_manager, aggregator_grid, elec_contract)
aggregator_elec_quantity = Aggregator("local_grid_quantity", LVE, strategy_quantity, aggregators_manager, aggregator_grid, elec_contract)
aggregator_elec_partial = Aggregator("local_grid_partial", LVE, strategy_partial, aggregators_manager, aggregator_grid, elec_contract)


# ##############################################################################################
# Manual creation of devices

# Each device is created 4 times
# emergency strategy
device_early_emergency = subclasses_dictionary["Device"]["HotWaterTank"]("device_early_emergency", elec_contract, early_emergency_owner, aggregator_elec_emergency, {"user": "dummy_user_early", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
device_expensive_emergency = subclasses_dictionary["Device"]["HotWaterTank"]("device_expensive_emergency", elec_expensive_contract, expensive_emergency_owner, aggregator_elec_emergency, {"user": "dummy_user", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
device_consuming_emergency = subclasses_dictionary["Device"]["HotWaterTank"]("device_consuming_emergency", elec_contract, consuming_emergency_owner, aggregator_elec_emergency, {"user": "dummy_user", "device": "dummy_usage_consuming"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")

production_emergency = subclasses_dictionary["Device"]["Background"]("production_emergency", producer_elec_contract, aggregators_manager, aggregator_elec_emergency, {"user": "dummy_user", "device": "dummy_producer_distribution_test"}, {"cold_water_temperature_daemon": water_temperature_daemon}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# price strategy
device_early_price = subclasses_dictionary["Device"]["HotWaterTank"]("device_early_price", elec_contract, early_price_owner, aggregator_elec_price, {"user": "dummy_user_early", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
device_expensive_price = subclasses_dictionary["Device"]["HotWaterTank"]("device_expensive_price", elec_expensive_contract, expensive_price_owner, aggregator_elec_price, {"user": "dummy_user", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
device_consuming_price = subclasses_dictionary["Device"]["HotWaterTank"]("device_consuming_price", elec_contract, consuming_price_owner, aggregator_elec_price, {"user": "dummy_user", "device": "dummy_usage_consuming"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")

production_price = subclasses_dictionary["Device"]["Background"]("production_price", producer_elec_contract, aggregators_manager, aggregator_elec_price, {"user": "dummy_user", "device": "dummy_producer_distribution_test"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# quantity strategy
device_early_quantity = subclasses_dictionary["Device"]["HotWaterTank"]("device_early_quantity", elec_contract, early_quantity_owner, aggregator_elec_quantity, {"user": "dummy_user_early", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
device_expensive_quantity = subclasses_dictionary["Device"]["HotWaterTank"]("device_expensive_quantity", elec_expensive_contract, expensive_quantity_owner, aggregator_elec_quantity, {"user": "dummy_user", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
device_consuming_quantity = subclasses_dictionary["Device"]["HotWaterTank"]("device_consuming_quantity", elec_contract, consuming_quantity_owner, aggregator_elec_quantity, {"user": "dummy_user", "device": "dummy_usage_consuming"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")

production_quantity = subclasses_dictionary["Device"]["Background"]("production_quantity", producer_elec_contract, aggregators_manager, aggregator_elec_quantity, {"user": "dummy_user", "device": "dummy_producer_distribution_test"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# partial strategy
device_early_partial = subclasses_dictionary["Device"]["HotWaterTank"]("device_early_partial", elec_contract, early_partial_owner, aggregator_elec_partial, {"user": "dummy_user_early", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
device_expensive_partial = subclasses_dictionary["Device"]["HotWaterTank"]("device_expensive_partial", elec_expensive_contract, expensive_partial_owner, aggregator_elec_partial, {"user": "dummy_user", "device": "dummy_usage"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")
device_consuming_partial = subclasses_dictionary["Device"]["HotWaterTank"]("device_consuming_partial", elec_contract, consuming_partial_owner, aggregator_elec_partial, {"user": "dummy_user", "device": "dummy_usage_consuming"}, {"cold_water_temperature_daemon": water_temperature_daemon}, "cases/ValidationCases/AdditionalData/DevicesProfiles/HotWaterTank.json")

production_partial = subclasses_dictionary["Device"]["Background"]("production_partial", producer_elec_contract, aggregators_manager, aggregator_elec_partial, {"user": "dummy_user", "device": "dummy_producer_distribution_test"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that distribution strategies work"

filename = "distribution_strategy_validation"

reference_values = {"early_emergency_owner.LVE.energy_bought": [418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "expensive_emergency_owner.LVE.energy_bought": [0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "consuming_emergency_owner.LVE.energy_bought": [0, 418/3.6/10000*2, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

                    "early_price_owner.LVE.energy_bought": [0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "expensive_price_owner.LVE.energy_bought": [418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "consuming_price_owner.LVE.energy_bought": [0, 418/3.6/10000*2, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000*2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

                    "early_quantity_owner.LVE.energy_bought": [0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "expensive_quantity_owner.LVE.energy_bought": [0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "consuming_quantity_owner.LVE.energy_bought": [418/3.6/10000, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 418/3.6/10000, 418/3.6/10000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

                    "early_partial_owner.LVE.energy_bought": [418/3.6/10000/4, 418/3.6/10000*3/4, 0, 0, 0, 0, 0, 0, 418/3.6/10000/4, 418/3.6/10000*3/4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "expensive_partial_owner.LVE.energy_bought": [418/3.6/10000/4, 418/3.6/10000*3/4, 0, 0, 0, 0, 0, 0, 418/3.6/10000/4, 418/3.6/10000*3/4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "consuming_partial_owner.LVE.energy_bought": [418/3.6/10000/2, 418/3.6/10000*3/2, 0, 0, 0, 0, 0, 0, 418/3.6/10000/2, 418/3.6/10000*3/2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    }

name = "LVE_emergency_energy_bought"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C}_{ref.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "early_emergency_owner.LVE.energy_bought_reference", "style": "points", "legend": r"early"},
                      {"catalog_name_entry": "expensive_emergency_owner.LVE.energy_bought_reference", "style": "points", "legend": r"expens."},
                      {"catalog_name_entry": "consuming_emergency_owner.LVE.energy_bought_reference", "style": "points", "legend": r"consum."}
                    ]
          },
    "Y2": {"label": r"$\mathcal{C}_{num.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "early_emergency_owner.LVE.energy_bought_simulation", "style": "lines",  "legend": r""},
                      {"catalog_name_entry": "expensive_emergency_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "consuming_emergency_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""}
                      ]
          }
}

name = "LVE_price_energy_bought"
export_plot2 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathsf{P}_{ref.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "early_price_owner.LVE.energy_bought_reference", "style": "points", "legend": r"early"},
                      {"catalog_name_entry": "expensive_price_owner.LVE.energy_bought_reference", "style": "points", "legend": r"expens."},
                      {"catalog_name_entry": "consuming_price_owner.LVE.energy_bought_reference", "style": "points", "legend": r"consum."}
                    ]
          },
    "Y2": {"label": r"$\mathsf{P}_{num.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "early_price_owner.LVE.energy_bought_simulation", "style": "lines",  "legend": r""},
                      {"catalog_name_entry": "expensive_price_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "consuming_price_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""}
                      ]
          }
}

name = "LVE_early_emergency_energy_bought"
export_plot3 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C}_{ref.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "early_emergency_owner.LVE.energy_bought_reference", "style": "points", "legend": r"emerg."},
                      {"catalog_name_entry": "early_price_owner.LVE.energy_bought_reference", "style": "points", "legend": r"price"},
                      {"catalog_name_entry": "early_quantity_owner.LVE.energy_bought_reference", "style": "points", "legend": r"qty"},
                      {"catalog_name_entry": "early_partial_owner.LVE.energy_bought_reference", "style": "points", "legend": r"part."}
                    ]
          },
    "Y2": {"label": r"$\mathcal{C}_{num.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "early_emergency_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "early_price_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "early_quantity_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "early_partial_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""}
                    ]
           }
}

name = "LVE_expensive_emergency_energy_bought"
export_plot4 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C}_{ref.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "expensive_emergency_owner.LVE.energy_bought_reference", "style": "points", "legend": r"emerg."},
                      {"catalog_name_entry": "expensive_price_owner.LVE.energy_bought_reference", "style": "points", "legend": r"price"},
                      {"catalog_name_entry": "expensive_quantity_owner.LVE.energy_bought_reference", "style": "points", "legend": r"qty"},
                      {"catalog_name_entry": "expensive_partial_owner.LVE.energy_bought_reference", "style": "points", "legend": r"part."}
                    ]
          },
    "Y2": {"label": r"$\mathcal{C}_{num.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "expensive_emergency_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "expensive_price_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "expensive_quantity_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "expensive_partial_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""}
                    ]
           }
}

name = "LVE_consuming_emergency_energy_bought"
export_plot5 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{C}_{ref.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "consuming_emergency_owner.LVE.energy_bought_reference", "style": "points", "legend": r"emerg."},
                      {"catalog_name_entry": "consuming_price_owner.LVE.energy_bought_reference", "style": "points", "legend": r"price"},
                      {"catalog_name_entry": "consuming_quantity_owner.LVE.energy_bought_reference", "style": "points", "legend": r"qty"},
                      {"catalog_name_entry": "consuming_partial_owner.LVE.energy_bought_reference", "style": "points", "legend": r"part."}
                    ]
          },
    "Y2": {"label": r"$\mathcal{C}_{num.} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "consuming_emergency_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "consuming_price_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "consuming_quantity_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "consuming_partial_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r""}
                    ]
           }
}

parameters = {"description": description, "filename": filename, "reference_values": reference_values, "tolerance": 1E-6, "export_plots": [export_plot1, export_plot2, export_plot3, export_plot4, export_plot5]}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("distribution_strategy_test", parameters)


# ##############################################################################################
# Simulation start
world.start()



