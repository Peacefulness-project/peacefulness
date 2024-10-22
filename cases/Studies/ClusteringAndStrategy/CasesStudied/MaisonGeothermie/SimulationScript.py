# case whose challenge is to balance energy sale, short-term storage and long-term storage
from typing import Callable

# ##############################################################################################
# Importations
from datetime import datetime, timedelta
from src.common.World import World
from src.tools.AgentGenerator import agent_generation
# pre-defined natures
from src.common.Strategy import *
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

    # domestic heat
    LTH = load_low_temperature_heat()

    # ##############################################################################################
    # Creation of daemons
    location = "Nantes"

    # Price Managers
    # this daemons fix a price for a given nature of energy
    price_manager_elec_RTP = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("prices_elec", {"location": "France", "buying_coefficient": 3, "selling_coefficient": 1}, "cases/Studies/ClusteringAndStrategy/CasesStudied/MaisonGeothermie/AdditionalData/prices.json")  # sets prices for TOU rate
    price_manager_elec_sell = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("selling_rate", {"buying_price": 0, "selling_price": 0})   # sets prices for TOU rate

    price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("heat_price", {"buying_price": 0, "selling_price": 0})  # sets prices for TOU rate

    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_elec_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.05})  # sets limit price accepted
    limit_prices_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0, "limit_selling_price": 0})  # sets limit price accepted

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

    # the BAU strategy
    strategy_heat = MLStrategy(priorities_conso, priorities_prod)
    strategy_heat.add_consumption_options(options_consumption)
    strategy_heat.add_production_options(options_production)

    # the elec strategy
    # strategy_elec = subclasses_dictionary["Strategy"]["LightAutarkyFullButFew"](get_emergency)
    strategy_elec = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()

    # the strategy grid, which always proposes an infinite quantity to sell and to buy
    grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Manual creation of agents

    house_owner = Agent("house_owner")  # creation of an agent
    # aggregators = Agent("aggregators")  # creation of an agent

    grid_manager = Agent("grid_manager")  #

    # ##############################################################################################
    # Manual creation of contracts

    # producers
    BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec_sell)

    cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_elec_RTP)  # a contract

    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("grid_prices_manager", LVE, price_manager_elec_RTP)  # this contract is the one between the local electrical grid and the national one

    heat_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("contract_heat", LTH, price_manager_heat)  # a contract

    # ##############################################################################################
    # Creation of aggregators

    aggregator_name = "grid"  # external grid
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, grid_manager)

    aggregator_name = "house_thermal"  # thermal part of the house
    aggregator_heat = Aggregator(aggregator_name, LTH, strategy_heat, house_owner)  # creation of a aggregator

    aggregator_name = "house_elec"  # elec part of the house
    aggregator_elec = Aggregator(aggregator_name, LVE, strategy_elec, house_owner, aggregator_grid, contract_grid, capacity={"buying": 10, "selling": 10})  # creation of a aggregator

    # ##############################################################################################
    # Manual creation of devices

    storage = subclasses_dictionary["Device"]["UndergroundThermalStorage"]("heat_storage", heat_contract, house_owner, aggregator_heat, {"device": "domestic_storage"}, {"ground_temperature_daemon": ground_temperature_daemon.name, "initial_storage_temperature": 70, "initial_SOC": 0.5})
    heating = subclasses_dictionary["Device"]["Heating"]("heating", heat_contract, house_owner, aggregator_heat, {"user": "residential", "device": "house_heat"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name, "initial_temperature": 5},
                                                         "cases/Studies/ClusteringAndStrategy/CasesStudied/MaisonGeothermie/AdditionalData/Heating.json")
    heatpump = subclasses_dictionary["Device"]["AdvancedHeatPump"]("heat_pump", [heat_contract, BAU_elec], house_owner, aggregator_elec, aggregator_heat,
                                                                   {"device": "dummy_heat_pump"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name, "ground_temperature_daemon": ground_temperature_daemon.name, "max_power": 1.5})
    PV = subclasses_dictionary["Device"]["PhotovoltaicsAdvanced"]("PV", BAU_elec, house_owner, aggregator_elec, {"device": "standard_field"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name, "irradiation_daemon": irradiation_daemon.name, "panels": 20})

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


