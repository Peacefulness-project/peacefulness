# This script is the one deconstructed in the tuto to create a case on the wiki.
from typing import Callable

# ##############################################################################################
# Importations
from datetime import datetime, timedelta
from src.common.World import World
from src.tools.AgentGenerator import agent_generation
# pre-defined natures
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat
from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger
# all the subclasses are imported in the following dictionary
from src.tools.SubclassesDictionary import get_subclasses

from cases.Studies.ClusteringAndStrategy.CasesStudied.MaisonGeothermie.OptionsManagementFunctions import options_consumption, options_production


def create_simulation(hours_simulated: int, priorities_conso: Callable, priorities_prod: Callable, step_name: str, metrics: list = [], delay_days: int = 0):
    # ##############################################################################################
    # Minimum
    # the following objects are necessary for the simulation to be performed
    # you need exactly one object of each type
    # ##############################################################################################

    # ##############################################################################################
    # Importation of subclasses
    # all the subclasses are imported in the following dictionary
    subclasses_dictionary = get_subclasses()
    from cases.Studies.ClusteringAndStrategy.MLStrategy import MLStrategy

    # ##############################################################################################
    # Creation of the world
    # a world contains all the other elements of the model
    # a world needs just a name
    name_world = f"clustering_case_day_{delay_days}"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/ClusteringAndStrategy/Results/MaisonGeothermie/" + step_name
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed("sunflower")

    # ##############################################################################################
    # Time parameters
    # it needs a start date, the value of an iteration in hours and the total number of iterations
    start_date = datetime(year=2018, month=1, day=1, hour=1, minute=0, second=0, microsecond=0) + timedelta(hours=delay_days)
    # a start date in the datetime format
    world.set_time(start_date,  # time management: start date
                   1,  # value of a time step (in hours)
                   hours_simulated)  # number of time steps simulated

    # ##############################################################################################
    # Model
    # ##############################################################################################

    # ##############################################################################################
    # Creation of nature

    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # ##############################################################################################
    # Creation of daemons
    location = "Nantes"

    # Price Managers
    # this daemons fix a price for a given nature of energy
    price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices", {"buying_price": 0.2, "selling_price": 0.1})   # sets prices for TOU rate

    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_elec_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.05})  # sets limit price accepted

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Outdoor temperature
    # this daemon is responsible for the value of outside temperature in the catalog
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": location}, exergy=False)

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    ground_temperature_daemon = subclasses_dictionary["Daemon"]["GroundTemperatureDaemon"]({"location": "France"})

    # Irradiation
    # this daemon is responsible for updating the value of raw solar irradiation
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": location}, direct_normal_irradiation=False)

    # ##############################################################################################
    # Creation of strategies

    # the training strategy
    strategy = MLStrategy(priorities_conso, priorities_prod)
    strategy.add_consumption_options(options_consumption)
    strategy.add_production_options(options_production)

    # the strategy grid, which always proposes an infinite quantity to sell and to buy
    grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Manual creation of agents

    grid_manager = Agent("grid_manager")  # creation of an agent

    industrial_consumers = Agent("industrial_consumers")

    other_consumers = Agent("other_consumers")

    TSO = Agent("TSO")  #

    # ##############################################################################################
    # Manual creation of contracts

    # producers
    BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec)

    curtailment_contract = subclasses_dictionary["Contract"]["LimitedCurtailmentContract"]("industrial_contract", LVE, price_manager_elec)  # a contract

    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("grid_prices_manager", LVE, price_manager_elec)  # this contract is the one between the local electrical grid and the national one

    cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_elec)

    # ##############################################################################################
    # Creation of aggregators

    aggregator_name = "grid"  # external grid
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, grid_manager)

    aggregator_name = "industrial_area"  # area with industrials
    aggregator_elec = Aggregator(aggregator_name, LVE, strategy, grid_manager, aggregator_grid, contract_grid, capacity={"buying": XXX, "selling": XXX})  # creation of an aggregator

    # ##############################################################################################
    # Manual creation of devices

    # base plant
    subclasses_dictionary["Device"]["DummyProducer"]("production", cooperative_contract_elec, grid_manager, aggregator_elec, {"device": "elec"}, {"max_power": XXX})  # creation of a heat production unit

    # storage
    subclasses_dictionary["Device"]["ElectricalBattery"]("storage", cooperative_contract_elec, grid_manager, aggregator_elec, {"device": "industrial_battery"}, {"capacity": XXX, "initial_SOC": XXX})

    # consumption

    # ##############################################################################################
    # Creation of dataloggers

    # datalogger used to get back producer outputs
    # producer_datalogger = Datalogger("performances_evaluation", "PerformancesEvaluation.txt")

    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    # subclasses_dictionary["Datalogger"]["ClusteringMetricsDatalogger"](period=1)
    exhaustive_datalogger = Datalogger("exhaustive_datalogger", "logs")
    exhaustive_datalogger.add_all()  # add all keys

    # datalogger used to export chosen metrics
    metrics_datalogger = Datalogger("metrics", "Metrics")
    for key in metrics:
        metrics_datalogger.add(key)

    world.start(False)

    return metrics_datalogger


