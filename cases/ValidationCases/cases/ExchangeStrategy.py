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
world.set_directory("cases/ValidationCases/Results/ExchangeStrategy")  # here, you have to put the path to your results directory


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

subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": -1})  # sets prices for the system operator


# ##############################################################################################
# Creation of strategies
# the different distribution strategies
strategy_light_autarky = subclasses_dictionary["Strategy"]["LightAutarkyEmergency"]()
strategy_autarky = subclasses_dictionary["Strategy"]["AutarkyEmergency"]()
strategy_always_satisfied = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()


# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
light_autarky_owner = Agent("light_autarky_owner")

autarky_owner = Agent("autarky_owner")

always_satisfied_owner = Agent("always_satisfied_owner")

aggregators_manager = Agent("aggregators_manager")


# ##############################################################################################
# Manual creation of contracts
BAU_contract = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_contract", LVE, price_manager_elec)

curtailment_contract = subclasses_dictionary["Contract"]["CurtailmentContract"]("curtailment_contract", LVE, price_manager_elec)

cooperative_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_elec)


# ##############################################################################################
# Creation of aggregators
aggregator_grid = Aggregator("national_grid", LVE, grid_strategy, aggregators_manager)

aggregator_light_autarky = Aggregator("local_grid_emergency", LVE, strategy_light_autarky, aggregators_manager, aggregator_grid, BAU_contract)
aggregator_autarky = Aggregator("local_grid_price", LVE, strategy_autarky, aggregators_manager, aggregator_grid, BAU_contract)
aggregator_always_satisfied = Aggregator("local_grid_quantity", LVE, strategy_always_satisfied, aggregators_manager, aggregator_grid, BAU_contract)


# ##############################################################################################
# Manual creation of devices

# Each device is created 3 times
# light autarky strategy
device_BAU_light_autarky = subclasses_dictionary["Device"]["Background"]("device_BAU_light_autarky", BAU_contract, light_autarky_owner, aggregator_light_autarky, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_light_autarky = subclasses_dictionary["Device"]["Background"]("device_curtailment_light_autarky", curtailment_contract, light_autarky_owner, aggregator_light_autarky, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_light_autarky = subclasses_dictionary["Device"]["DummyProducer"]("production_light_autarky", cooperative_contract, light_autarky_owner, aggregator_light_autarky, {"device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# autarky strategy
device_BAU_autarky = subclasses_dictionary["Device"]["Background"]("device_BAU_autarky", BAU_contract, autarky_owner, aggregator_autarky, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_autarky = subclasses_dictionary["Device"]["Background"]("device_curtailment_autarky", curtailment_contract, autarky_owner, aggregator_autarky, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_autarky = subclasses_dictionary["Device"]["DummyProducer"]("production_autarky", cooperative_contract, autarky_owner, aggregator_autarky, {"device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# always satisfied strategy
device_BAU_always_satisfied = subclasses_dictionary["Device"]["Background"]("device_BAU_always_satisfied", BAU_contract, always_satisfied_owner, aggregator_always_satisfied, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_always_satisfied = subclasses_dictionary["Device"]["Background"]("device_curtailment_always_satisfied", curtailment_contract, always_satisfied_owner, aggregator_always_satisfied, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_always_satisfied = subclasses_dictionary["Device"]["DummyProducer"]("production_always_satisfied", cooperative_contract, always_satisfied_owner, aggregator_always_satisfied, {"device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")


# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that exchange strategies work"

filename = "exchange_strategy_validation"

reference_values = {"light_autarky_owner.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 12, 12, 12, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    "light_autarky_owner.LVE.energy_sold": [0, 2, 4, 6, 8, 10, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],

                    "autarky_owner.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 12, 12, 12, 12, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "autarky_owner.LVE.energy_sold": [0, 2, 4, 6, 8, 10, 12, 12, 12, 12, 12, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

                    "always_satisfied_owner.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46],
                    "always_satisfied_owner.LVE.energy_sold": [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]
                    }

name = "LVE_light_autarky"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{\textrm{bought}} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "light_autarky_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "light_autarky_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."}
                    ]
          },
    "Y2": {"label": r"$\mathcal{P}_{\textrm{sold}} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "light_autarky_owner.LVE.energy_sold_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "light_autarky_owner.LVE.energy_sold_simulation", "style": "lines", "legend": r"num."}
                    ]
          },
}

name = "LVE_autarky"
export_plot2 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{\textrm{bought}} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "autarky_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "autarky_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."}
                    ]
          },
    "Y2": {"label": r"$\mathcal{P}_{\textrm{sold}} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "autarky_owner.LVE.energy_sold_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "autarky_owner.LVE.energy_sold_simulation", "style": "lines", "legend": r"num."}
                    ]
          },
}

name = "LVE_always_satisfied"
export_plot3 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{\textrm{bought}} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "always_satisfied_owner.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "always_satisfied_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."}
                    ]
          },
    "Y2": {"label": r"$\mathcal{P}_{\textrm{sold}} \, [$\euro{}$]$",
          "graphs": [ {"catalog_name_entry": "always_satisfied_owner.LVE.energy_sold_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "always_satisfied_owner.LVE.energy_sold_simulation", "style": "lines", "legend": r"num."}
                    ]
          },
}

name = "Bought_Energy_Alltogether"
export_plot4 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{ref.} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "light_autarky_owner.LVE.energy_bought_reference", "style": "points", "legend": r"light autarky ref."},
                      {"catalog_name_entry": "autarky_owner.LVE.energy_bought_reference", "style": "points", "legend": r"autarky ref."},
                      {"catalog_name_entry": "always_satisfied_owner.LVE.energy_bought_reference", "style": "points", "legend": r"always satisfied ref."}
                      ]
          },
    "Y2": {"label": r"$\mathcal{P}_{num.} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "light_autarky_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"light autarky num."},
                      {"catalog_name_entry": "autarky_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"autarky num."},
                      {"catalog_name_entry": "always_satisfied_owner.LVE.energy_bought_simulation", "style": "lines", "legend": r"always satisfied num."}
                      ]
          }
}

name = "Sold_Energy_Alltogether"
export_plot5 = {
    "name": name,
    "filename": "export_"+name,
    "options": graph_options(["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "physical_time", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{ref.} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "light_autarky_owner.LVE.energy_sold_reference", "style": "points", "legend": r"lgt autark."},
                      {"catalog_name_entry": "autarky_owner.LVE.energy_sold_reference", "style": "points", "legend": r"autark."},
                      {"catalog_name_entry": "always_satisfied_owner.LVE.energy_sold_reference", "style": "points", "legend": r"alws satis."}
                      ]
          },
    "Y2": {"label": r"$\mathcal{P}_{num.} \, [\si{\watt}]$",
          "graphs": [ {"catalog_name_entry": "light_autarky_owner.LVE.energy_sold_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "autarky_owner.LVE.energy_sold_simulation", "style": "lines", "legend": r""},
                      {"catalog_name_entry": "always_satisfied_owner.LVE.energy_sold_simulation", "style": "lines", "legend": r""}
                      ]
          }
}

parameters = {"description": description, "filename": filename, "reference_values": reference_values, "tolerance": 1E-6, "export_plots": [export_plot1, export_plot2, export_plot3, export_plot4, export_plot5]}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("exchange_strategy_test", parameters)


# ##############################################################################################
# Simulation start
world.start()