# This script checks that exchanges strategies work

# ##############################################################################################
# Importations
from datetime import datetime
from math import inf

from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.World import World
from src.common.Strategy import *

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
name_world = "exchange_strategy"
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
start_date = datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)  # a start date in the datetime format
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
strategy_light_autarky = subclasses_dictionary["Strategy"]["LightAutarkyFullButFew"](get_emergency)
strategy_autarky = subclasses_dictionary["Strategy"]["AutarkyFullButFew"](get_emergency)
strategy_always_satisfied = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()
strategy_max_exchanges = subclasses_dictionary["Strategy"]["ExchangesFullButFew"](get_emergency)
strategy_max_buy = subclasses_dictionary["Strategy"]["MaxBuyFullButFew"](get_emergency)
strategy_max_sell = subclasses_dictionary["Strategy"]["MaxSellFullButFew"](get_emergency)

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
light_autarky_owner = Agent("light_autarky_owner")

autarky_owner = Agent("autarky_owner")

always_satisfied_owner = Agent("always_satisfied_owner")

exchanges_owner = Agent("exchanges_owner")

buy_owner = Agent("buy_owner")

sell_owner = Agent("sell_owner")

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
aggregator_max_exchanges = Aggregator("local_grid_exchanges", LVE, strategy_max_exchanges, aggregators_manager, aggregator_grid, BAU_contract, capacity={"buying": 12, "selling": inf})
aggregator_max_buy = Aggregator("local_grid_buy", LVE, strategy_max_buy, aggregators_manager, aggregator_grid, BAU_contract, capacity={"buying": inf, "selling": inf})
aggregator_max_sell = Aggregator("local_grid_sell", LVE, strategy_max_sell, aggregators_manager, aggregator_grid, BAU_contract, capacity={"buying": inf, "selling": inf})


# ##############################################################################################
# Manual creation of devices

# Each device is created 4 times
# light autarky strategy
device_BAU_light_autarky = subclasses_dictionary["Device"]["Background"]("device_BAU_light_autarky", BAU_contract, light_autarky_owner, aggregator_light_autarky, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_light_autarky = subclasses_dictionary["Device"]["Background"]("device_curtailment_light_autarky", curtailment_contract, light_autarky_owner, aggregator_light_autarky, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_light_autarky = subclasses_dictionary["Device"]["DummyProducer"]("production_light_autarky", cooperative_contract, light_autarky_owner, aggregator_light_autarky, {"device": "dummy_usage"}, {"max_power": 12}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# autarky strategy
device_BAU_autarky = subclasses_dictionary["Device"]["Background"]("device_BAU_autarky", BAU_contract, autarky_owner, aggregator_autarky, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_autarky = subclasses_dictionary["Device"]["Background"]("device_curtailment_autarky", curtailment_contract, autarky_owner, aggregator_autarky, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_autarky = subclasses_dictionary["Device"]["DummyProducer"]("production_autarky", cooperative_contract, autarky_owner, aggregator_autarky, {"device": "dummy_usage"}, {"max_power": 12}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# always satisfied strategy
device_BAU_always_satisfied = subclasses_dictionary["Device"]["Background"]("device_BAU_always_satisfied", BAU_contract, always_satisfied_owner, aggregator_always_satisfied, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_always_satisfied = subclasses_dictionary["Device"]["Background"]("device_curtailment_always_satisfied", curtailment_contract, always_satisfied_owner, aggregator_always_satisfied, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_always_satisfied = subclasses_dictionary["Device"]["DummyProducer"]("production_always_satisfied", cooperative_contract, always_satisfied_owner, aggregator_always_satisfied, {"device": "dummy_usage"}, {"max_power": 12}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# exchanges strategy
device_BAU_exchanges = subclasses_dictionary["Device"]["Background"]("device_BAU_exchanges", BAU_contract, exchanges_owner, aggregator_max_exchanges, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_exchanges = subclasses_dictionary["Device"]["Background"]("device_curtailment_exchanges", curtailment_contract, exchanges_owner, aggregator_max_exchanges, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_exchanges = subclasses_dictionary["Device"]["DummyProducer"]("production_exchanges", cooperative_contract, exchanges_owner, aggregator_max_exchanges, {"device": "dummy_usage"}, {"max_power": 12}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# max buy strategy
device_BAU_buy = subclasses_dictionary["Device"]["Background"]("device_BAU_buy", BAU_contract, buy_owner, aggregator_max_buy, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_buy = subclasses_dictionary["Device"]["Background"]("device_curtailment_buy", curtailment_contract, buy_owner, aggregator_max_buy, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_buy = subclasses_dictionary["Device"]["DummyProducer"]("production_buy", cooperative_contract, buy_owner, aggregator_max_buy, {"device": "dummy_usage"}, {"max_power": 12}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# max sell strategy
device_BAU_sell = subclasses_dictionary["Device"]["Background"]("device_BAU_sell", BAU_contract, sell_owner, aggregator_max_sell, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
device_curtailment_sell = subclasses_dictionary["Device"]["Background"]("device_curtailment_sell", curtailment_contract, sell_owner, aggregator_max_sell, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
production_sell = subclasses_dictionary["Device"]["DummyProducer"]("production_sell", cooperative_contract, sell_owner, aggregator_max_sell, {"device": "dummy_usage"}, {"max_power": 12}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that exchange strategies work"

filename = "exchange_strategy_validation"

reference_values = {"light_autarky_owner.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 12, 12, 12, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    "light_autarky_owner.LVE.energy_sold": [0, 2, 4, 6, 8, 10, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],

                    "autarky_owner.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 12, 12, 12, 12, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "autarky_owner.LVE.energy_sold": [0, 2, 4, 6, 8, 10, 12, 12, 12, 12, 12, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

                    "always_satisfied_owner.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46],
                    "always_satisfied_owner.LVE.energy_sold": [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],

                    "exchanges_owner.LVE.energy_bought": [0, 1, 2, 3, 4, 10, 12, 12, 12, 12, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    "exchanges_owner.LVE.energy_sold": [12, 12, 12, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],

                    "buy_owner.LVE.energy_bought": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46],
                    "buy_owner.LVE.energy_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

                    "sell_owner.LVE.energy_bought": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    "sell_owner.LVE.energy_sold": [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
                    }

name = "LVE_light_autarky"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "iteration", "label": r"$t \, [\si{\hour}]$"},
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
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "iteration", "label": r"$t \, [\si{\hour}]$"},
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
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "iteration", "label": r"$t \, [\si{\hour}]$"},
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
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "iteration", "label": r"$t \, [\si{\hour}]$"},
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
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "iteration", "label": r"$t \, [\si{\hour}]$"},
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
