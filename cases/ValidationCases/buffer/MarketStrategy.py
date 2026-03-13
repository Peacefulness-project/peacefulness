# This script checks that strategies simulating markets work as expected

# ##############################################################################################
# Importations
from datetime import datetime
from math import inf

from lib.DefaultNatures.DefaultNatures import *

from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.World import World
from src.common.Strategy import *
from src.common.Contract import Contract

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
name_world = "market_strategy"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
world.set_directory("cases/ValidationCases/Results/MarketStrategy")  # here, you have to put the path to your results directory


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
market_strategy = subclasses_dictionary["Strategy"]["EquilibriumPriceMarket"]()
bidding_strategy = subclasses_dictionary["Strategy"]["NaiveBidStrategy"]("coco l'asticot", get_emergency)

# strategy grid, which always proposes an infinite quantity to sell and to buy
grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()


# ##############################################################################################
# Manual creation of agents
aggregators_manager = Agent("aggregators_manager")
consumers = Agent("consumers")
producers = Agent("producers")


# ##############################################################################################
# Manual creation of contracts
transparent_contract = Contract("dummy_contract", LVE, price_manager_elec)  # a contract that does nothing

BAU_contract = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_contract", LVE, price_manager_elec)
curtailment_contract = subclasses_dictionary["Contract"]["CurtailmentContract"]("curtailment_contract", LVE, price_manager_elec)
cooperative_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_elec)


# ##############################################################################################
# Creation of aggregators
marketplace = Aggregator("marketplace", LVE, market_strategy, aggregators_manager)
aggregator_consumer = Aggregator("consumer_side", LVE, bidding_strategy, aggregators_manager, marketplace, transparent_contract)
aggregator_producer = Aggregator("producer_side", LVE, bidding_strategy, aggregators_manager, marketplace, transparent_contract)

# ##############################################################################################
# Manual creation of devices

# consumer side
mandatory_consumption = subclasses_dictionary["Device"]["Background"]("mandatory_consumption", BAU_contract, consumers, aggregator_consumer, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")
optional_consumption = subclasses_dictionary["Device"]["Background"]("optional_consumption", curtailment_contract, consumers, aggregator_consumer, {"user": "dummy_user", "device": "dummy_usage"}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/Background.json")

# producer side
production = subclasses_dictionary["Device"]["DummyProducer"]("producer", cooperative_contract, producers, aggregator_producer, {"device": "dummy_usage"}, {"max_power": 24}, filename="cases/ValidationCases/AdditionalData/DevicesProfiles/DummyProducer.json")

# ##############################################################################################
# Creation of the validation daemon
description = "This script checks that exchange strategies work"

filename = "exchange_strategy_validation"

reference_values = {"mandatory_consumption.LVE.energy_bought": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    "optional_consumption.LVE.energy_bought": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    "producer.LVE.energy_sold": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                    }

name = "Coco l'asticot"
export_plot1 = {
    "name": name,
    "filename": "export_"+name,
    "options": GraphOptions(f"{name}_graph_options", ["csv", "LaTeX"], "multiple_series"),
    "X": {"catalog_name_entry": "iteration", "label": r"$t \, [\si{\hour}]$"},
    "Y": {"label": r"$\mathcal{P}_{\textrm{bought}} \, [kWh]$",
          "graphs": [ {"catalog_name_entry": "mandatory_consumption.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "mandatory_consumption.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."}
                    ]
          },
    "Y2": {"label": r"$\mathcal{P}_{\textrm{bought}} \, [kWh]$",
          "graphs": [ {"catalog_name_entry": "optional_consumption.LVE.energy_bought_reference", "style": "points", "legend": r"ref."},
                      {"catalog_name_entry": "optional_consumption.LVE.energy_bought_simulation", "style": "lines", "legend": r"num."}
                    ]
          },
    "Y3": {"label": r"$\mathcal{P}_{\textrm{sold}} \, [kWh]$",
           "graphs": [{"catalog_name_entry": "producer.LVE.energy_sold_reference", "style": "points",
                       "legend": r"ref."},
                      {"catalog_name_entry": "producer.LVE.energy_sold_simulation", "style": "lines",
                       "legend": r"num."}
                      ]
           },
}


parameters = {"description": description, "filename": filename, "reference_values": reference_values, "tolerance": 1E-6, "export_plots": [export_plot1]}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("exchange_strategy_test", parameters)


# ##############################################################################################
# Simulation start
world.start()
