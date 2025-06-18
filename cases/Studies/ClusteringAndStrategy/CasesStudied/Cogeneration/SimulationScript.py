# case whose challenge is the management of power ramp-up to reduce energy cost and also CO2 emissions
# an energy producer has access to two energy generation system ; a biomass plant used to manage the base load, and a gas plant to manage peak load
# the biomass plant is more environmentally friendly but less flexible while the gas plant emits more CO2 and is flexible


# ##############################################################################################
# Imports
from typing import Callable
from scipy.stats import gamma
import numpy as np

from datetime import datetime, timedelta
from lib.Subclasses.Strategy.AlwaysSatisfied.AlwaysSatisfied import AlwaysSatisfied
from src.common.World import World
from src.tools.AgentGenerator import agent_generation
from src.common.Strategy import *
from lib.DefaultNatures.DefaultNatures import *
from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses

from cases.Studies.ClusteringAndStrategy.CasesStudied.RampUpManagement.OptionsManagementFunctions import options_consumption, options_production


def create_simulation(hours_simulated: int, priorities_conso: Callable, priorities_prod: Callable, step_name: str, metrics: list = [], delay_days: int = 0, random_seed: int = 0, standard_deviation: int = 0):
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
    pathExport = "cases/Studies/ClusteringAndStrategy/Results/Cogeneration/" + step_name
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed(random_seed)

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

    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # gas
    LPG = load_low_pressure_gas()

    # ##############################################################################################
    # Creation of daemons
    location = "Nantes"

    # Price Managers
    price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("heat_price", {"buying_price": 0.5, "selling_price": 0.2})  # sets prices for TOU rate
    price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("elec_price", {"buying_price": 0.2, "selling_price": 0.1})   # sets prices for TOU rate
    price_manager_gas = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("gas_price", {"buying_price": 0.2, "selling_price": 0.1})   # sets prices for TOU rate

    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.8, "limit_selling_price": 0.1})  # sets limit price accepted
    limit_prices_elec_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.05})  # sets limit price accepted
    limit_prices_elec_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LPG.name, "limit_buying_price": 0.2, "limit_selling_price": 0.05})  # sets limit price accepted

    # Outdoor temperature
    # this daemon is responsible for the value of outside temperature in the catalog
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": location}, exergy=False)

    # ##############################################################################################
    # Creation of strategies
    # the Clustering strategy
    strategy_grid = subclasses_dictionary["Strategy"]["Grid"]()
    strategy_optimized = subclasses_dictionary["Strategy"]["SubaggregatorHeatPartialButAll"]()

    # strategy_optimized = MLStrategy(priorities_conso, priorities_prod)
    # strategy_optimized.add_consumption_options(options_consumption)
    # strategy_optimized.add_production_options(options_production)

    # ##############################################################################################
    # Manual creation of agents
    DHN_manager = Agent("DHN_manager")  # creation of an agent
    consumers = Agent("consumers")
    CHP_owner = Agent("cogeneration_owner")
    other = Agent("other")

    # ##############################################################################################
    # Manual creation of contracts
    BAU_gas = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_gas", LPG, price_manager_gas)
    BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec)
    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("grid_prices_manager", LVE, price_manager_elec)  # this contract is the one between the local electrical grid and the national one
    heat_contract_BAU = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_manager_heat)

    cooperative_contract_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_elec", LVE, price_manager_elec)
    cooperative_contract_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("cooperative_contract_heat", LTH, price_manager_heat)

    # ##############################################################################################
    # Creation of aggregators
    aggregator_name = "peakload_gas_plant"  # external grid
    aggregator_grid = Aggregator(aggregator_name, LTH, strategy_grid, DHN_manager)

    aggregator_name = "district_heating_microgrid"
    aggregator_heat = Aggregator(aggregator_name, LTH, strategy_optimized, DHN_manager, aggregator_grid, contract_grid, efficiency=1, capacity={"buying": 2000000, "selling": 0})

    aggregator_name = "local_network"  # area with industrials
    aggregator_elec = Aggregator(aggregator_name, LVE, strategy_optimized, DHN_manager, aggregator_grid, contract_grid, capacity={"buying": 100000, "selling": 0})  # creation of an aggregator

    aggregator_name = "GasNetwork"
    aggregator_gas = Aggregator(aggregator_name, LPG, strategy_grid, other)

    # ##############################################################################################
    # Manual creation of devices
    np.random.seed(seed=random_seed)
    def rng_generator(consumption):
        if bool(standard_deviation) & bool(consumption):
            a = (1 / standard_deviation)**2
            b = standard_deviation ** 2 * consumption
            toto = gamma.rvs(a, scale=b)
            return toto
        else:
            return consumption

    def identity(consumption):
        return consumption

    CHP_max_power = 2000  # kW
    subclasses_dictionary["Device"]["AdvancedCombinedHeatAndPower"]("CHP_unit", [BAU_gas, cooperative_contract_heat,
                                                                                 cooperative_contract_elec], CHP_owner,
                                                                    aggregator_gas, [aggregator_heat, aggregator_elec],
                                                                    {"device": "test_system"},
                                                                    {"max_power": CHP_max_power})

    # elec loads
    subclasses_dictionary["Device"]["ResidentialDwelling"]("residential_dwellings", BAU_elec, consumers, aggregator_elec, {"user": "yearly_consumer", "device": "representative_dwelling"}, parameters={"number": 750, "rng_generator": rng_generator})

    subclasses_dictionary["Device"]["Background"]("industrial_process", BAU_elec, consumers, aggregator_elec, {"user": "yearly_consumer", "device": "industrial_ELMAS_dataset"}, parameters={"rng_generator": rng_generator},
                                                  filename="cases/Studies/ClusteringAndStrategy/CasesStudied/LimitedResourceManagement/AdditionalData/Background.json")

    # Thermal loads
    old_houses = subclasses_dictionary["Device"]["Background"]("old_house", heat_contract_BAU, consumers, aggregator_heat,
                                                                {"user": "old_house", "device": "old_house"}, parameters={"rng_generator": rng_generator},
                                                                filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    new_houses = subclasses_dictionary["Device"]["Background"]("new_house", heat_contract_BAU, consumers, aggregator_heat,
                                                               {"user": "new_house", "device": "new_house"}, parameters={"rng_generator": rng_generator},
                                                               filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    offices = subclasses_dictionary["Device"]["Background"]("office", heat_contract_BAU, consumers, aggregator_heat,
                                                            {"user": "office", "device": "office"}, parameters={"rng_generator": rng_generator},
                                                            filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")

    # ##############################################################################################
    # Creation of dataloggers

    # datalogger used to get back producer outputs
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()

    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    # subclasses_dictionary["Datalogger"]["ClusteringMetricsDatalogger"](period=1)
    exhaustive_datalogger = Datalogger("exhaustive_datalogger", "logs")
    exhaustive_datalogger.add_all()  # add all keys

    # datalogger used to export chosen metrics
    metrics_datalogger = Datalogger("metrics", "Metrics")
    for key in metrics:
        metrics_datalogger.add(key)

    world.start(verbose=False)

    return metrics_datalogger
