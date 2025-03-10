# case whose challenge is the management of power ramp-up to reduce energy cost and also CO2 emissions
# an energy producer has access to two energy generation system ; a biomass plant used to manage the base load, and a gas plant to manage peak load
# the biomass plant is more environmentally friendly but less flexible while the gas plant emits more CO2 and is flexible


# ##############################################################################################
# Imports
from typing import Callable
from datetime import datetime, timedelta

from lib.Subclasses.Strategy.AlwaysSatisfied.AlwaysSatisfied import AlwaysSatisfied
from src.common.World import World
from src.tools.AgentGenerator import agent_generation
from src.common.Strategy import *
from lib.DefaultNatures.DefaultNatures import load_low_temperature_heat
from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses

from cases.Studies.ClusteringAndStrategy.CasesStudied.RampUpManagement.OptionsManagementFunctions import options_consumption, options_production
# from os import chdir
# chdir("D:/dossier_y23hallo/PycharmProjects/peacefulness")

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
    pathExport = "cases/Studies/ClusteringAndStrategy/Results/RampUpManagement/" + step_name
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
    # domestic heat
    LTH = load_low_temperature_heat()

    # ##############################################################################################
    # Creation of daemons
    location = "Nantes"

    # Price Managers
    price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("heat_price", {"buying_price": 0.5, "selling_price": 0.2})  # sets prices for TOU rate
    # price_manager_heat_TOU = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_heat", {"nature": LTH.name, "buying_price": [0.4, 0.65], "selling_price": [0.25, 0.35], "on-peak_hours": [[12, 24]]})

    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.8, "limit_selling_price": 0.1})  # sets limit price accepted

    # Outdoor temperature
    # this daemon is responsible for the value of outside temperature in the catalog
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": location}, exergy=False)

    # ##############################################################################################
    # Creation of strategies
    # the Clustering strategy
    strategy_grid = subclasses_dictionary["Strategy"]["Grid"]()
    strategy_heat = MLStrategy(priorities_conso, priorities_prod)
    strategy_heat.add_consumption_options(options_consumption)
    strategy_heat.add_production_options(options_production)

    # ##############################################################################################
    # Manual creation of agents
    DHN_manager = Agent("DHN_manager")  # creation of an agent

    # ##############################################################################################
    # Manual creation of contracts
    # heat_contract_curtailment = subclasses_dictionary["Contract"]["LimitedCurtailmentContract"]("heat_well", LTH, price_manager_heat, {"curtailment_hours": 10, "rotation_duration": 168})
    heat_contract_curtailment = subclasses_dictionary["Contract"]["CurtailmentContract"]("heat_well", LTH, price_manager_heat)
    heat_contract_BAU = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_manager_heat)
    heat_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("contract_heat", LTH, price_manager_heat)
    # heat_contract_TOU = subclasses_dictionary["Contract"]["CooperativeContract"]("contract_heat_TOU", LTH, price_manager_heat_TOU)

    # ##############################################################################################
    # Creation of aggregators
    aggregator_name = "peakload_gas_plant"  # external grid
    aggregator_grid = Aggregator(aggregator_name, LTH, strategy_grid, DHN_manager)
    aggregator_name = "district_heating_microgrid"
    aggregator_district = Aggregator(aggregator_name, LTH, strategy_heat, DHN_manager, aggregator_grid, heat_contract, efficiency=1, capacity={"buying": 1100, "selling": 0})

    # ##############################################################################################
    # Manual creation of devices
    # dissipation
    heat_sink = subclasses_dictionary["Device"]["Background"]("heat_sink", heat_contract_curtailment, DHN_manager, aggregator_district,
                                                              {"user": "artificial_sink", "device": "artificial_sink"},
                                                              filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    # Thermal loads
    old_houses = subclasses_dictionary["Device"]["Background"]("old_house", heat_contract_BAU, DHN_manager, aggregator_district,
                                                                {"user": "old_house", "device": "old_house"},
                                                                filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    new_houses = subclasses_dictionary["Device"]["Background"]("new_house", heat_contract_BAU, DHN_manager, aggregator_district,
                                                               {"user": "new_house", "device": "new_house"},
                                                               filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    offices = subclasses_dictionary["Device"]["Background"]("office", heat_contract_BAU, DHN_manager, aggregator_district,
                                                            {"user": "office", "device": "office"},
                                                            filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    # Thermal energy producers
    base_load = subclasses_dictionary["Device"]["BiomassGasPlantAlternative"]("biomass_plant", heat_contract, DHN_manager, aggregator_district, {"device": "Biomass_2_ThP"}, {"max_power": 1300, "recharge_quantity": 1500, "autonomy": 12, "initial_energy": 300})
    # peak_load = subclasses_dictionary["Device"]["DummyProducer"]("fast_gas_boiler", heat_contract_TOU, DHN_manager, aggregator_grid, {"device": "heat"}, {"max_power": 1100})
    # Thermal energy storage
    # network_pipes = subclasses_dictionary["Device"]["LatentHeatStorage"]("DHN_pipelines", heat_contract_TOU, DHN_manager, aggregator_grid, {"device": "industrial_water_tank"}, {"outdoor_temperature_daemon": outdoor_temperature_daemon.name})

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
