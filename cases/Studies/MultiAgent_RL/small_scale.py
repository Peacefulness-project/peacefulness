# This script is the one deconstructed in the tuto to create a case on the wiki.
from scipy.stats import gamma
import numpy as np

# ##############################################################################################
# Importations
from datetime import datetime

from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Gym_World import GymWorld
# from src.common.World import World
# pre-defined natures
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity
from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger
# all the subclasses are imported in the following dictionary
from lib.Subclasses.Strategy.MultiAgentDRLStrategy.SubclassesDictionary import get_subclasses


def create_simulation(world_name: str, start_date: datetime, hours_simulated: int, path_name: str, metrics: list = [], random_seed: int = 0, standard_deviation: float = 0.25, red_dof_flag=False):
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
    name_world = world_name + f"_{random_seed}"
    world = GymWorld(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    world.set_directory(path_name)  # registration

    # ##############################################################################################
    # Definition of the random seed
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed(random_seed)

    # ##############################################################################################
    # Time parameters
    # it needs a start date, the value of an iteration in hours and the total number of iterations
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

    # Price Managers
    ################
    price_manager_grid = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("EDN_prices", {"buying_coefficient": 1.1, "selling_coefficient": 0.9, "location": "France"})  # sets prices for EDN
    price_manager_TOU_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("MG1_prices", {"nature": LVE.name, "buying_price": [0.2, 0.15], "selling_price": [0.12, 0.06], "on-peak_hours": [[5, 9], [17, 21]]})
    price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("MG2_prices", {"buying_price": 0.14, "selling_price": 0.08})   # sets prices for TOU rate

    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_elec_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.25, "limit_selling_price": 0.05})  # sets limit price accepted


    # Data-related Daemons
    ######################
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Nantes"})  # Irradiation
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Nantes"})  # Outdoor temperature
    wind_speed_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Nantes"})  # Wind speed
    water_flow_daemon = subclasses_dictionary["Daemon"]["WaterFlowDaemon"]({"location": "GavedePau_Pau"})
    indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # ##############################################################################################
    # Creation of strategies

    # the training strategy
    # strategy_1 = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()
    strategy_1 = subclasses_dictionary["Strategy"]["SingleAgentDRLStrategy"]("agent_1", red_dof_flag=red_dof_flag)
    strategy_2 = subclasses_dictionary["Strategy"]["SingleAgentDRLStrategy"]("agent_2", red_dof_flag=red_dof_flag)

    # the strategy grid, which always proposes an infinite quantity to sell and to buy
    grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Manual creation of agents

    grid_manager = Agent("Enedis")  # creation of an agent

    community_1 = Agent("community_1")

    community_2 = Agent("community_2")

    # ##############################################################################################
    # Manual creation of contracts

    BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec)  # contract for electricity rigid consumers and producers

    COOP_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("COOP_elec", LVE, price_manager_elec)  # contract for electric devices that accept to be shifted/flexible

    COOP_elec_residential = subclasses_dictionary["Contract"]["CooperativeContract"]("COOP_elec_residential", LVE, price_manager_TOU_elec)  # contract for electric devices that accept to be shifted/flexible

    curtailment_contract_residential = subclasses_dictionary["Contract"]["LimitedCurtailmentContract"]("residential_contract", LVE, price_manager_TOU_elec, {"curtailment_hours": 168, "rotation_duration": 168})  # a contract

    curtailment_contract_industrial = subclasses_dictionary["Contract"]["LimitedCurtailmentContract"]("industrial_contract", LVE, price_manager_elec, {"curtailment_hours": 168, "rotation_duration": 168})  # a contract

    grid_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("grid_elec", LVE, price_manager_grid)  # contract between the microgrid and electricity distribution network

    # ##############################################################################################
    # Creation of aggregators

    aggregator_name = "national_electricity_distribution_network"  # external electricity grid
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, grid_manager)

    aggregator_name = "local_community_1"
    aggregator_elec_1 = Aggregator(aggregator_name, LVE, strategy_1, community_1, aggregator_grid, grid_contract, capacity={"buying": 4000, "selling": 2500})  # creation of an aggregator

    aggregator_name = "local_community_2"
    aggregator_elec_2 = Aggregator(aggregator_name, LVE, strategy_2, community_2, aggregator_grid, grid_contract, capacity={"buying": 8000, "selling": 9000})  # creation of an aggregator

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

    # Local_community_1 : residential with DER & distributed BESS
    subclasses_dictionary["Device"]["PhotovoltaicsAdvanced"]("PV_field_1", BAU_elec, community_1, aggregator_elec_1, {"device": "standard"}, parameters={"panels": 2500, "irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})
    subclasses_dictionary["Device"]["WindTurbineAdvanced"]("WT_field_1", BAU_elec, community_1, aggregator_elec_1, {"device": "standard"}, parameters={"wind_speed_daemon": wind_speed_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "rugosity": "flat"})
    subclasses_dictionary["Device"]["DummyProducer"]("Diesel_generator", COOP_elec_residential, community_1, aggregator_elec_1, {"device": "elec"}, {"max_power": 1000})
    subclasses_dictionary["Device"]["ElectricalBattery"]("storage", COOP_elec_residential, community_1, aggregator_elec_1, {"device": "ECOS2025"}, {"capacity": 10000, "initial_SOC": 0.5}, filename="cases/Studies/ClusteringAndStrategy/CasesStudied/LimitedResourceManagement/AdditionalData/ElectricalBattery.json")
    subclasses_dictionary["Device"]["ResidentialDwelling"]("residential_dwellings", curtailment_contract_residential, community_1, aggregator_elec_1, {"user": "yearly_consumer", "device": "representative_dwelling"}, parameters={"number": 2250, "rng_generator": rng_generator})

    # Local_community_2 : industrial size loads, hydro-electricity supply unit
    subclasses_dictionary["Device"]["ElectricDam"]("Step", COOP_elec, community_2, aggregator_elec_2, {"device": "Pelton"}, {"height": 60, "max_power": 12000, "water_flow_daemon": water_flow_daemon.name})
    subclasses_dictionary["Device"]["Background"]("industrial_process", curtailment_contract_industrial, community_2, aggregator_elec_2, {"user": "yearly_consumer", "device": "industrial_mini_case"}, parameters={"rng_generator": rng_generator}, filename="cases/Studies/MultiAgent_RL/AdditionalData/Background.json")

    # Interconnection between the two communities
    # subclasses_dictionary["Device"]["DummyConverter"]("interconnection", COOP_elec, community_2, aggregator_elec_2, aggregator_elec_1, {"device": "electricity_cable"}, parameters={"max_power": 4000})

    # ##############################################################################################
    # Creation of dataloggers
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()

    # list_of_devices = ["PV_field_1", "WT_field_1", "Diesel_generator", "storage", "residential_dwellings", "Step", "industrial_process"]
    # subclasses_dictionary["Datalogger"]["DeviceQuantityDatalogger"]("device_quantity_frequency_1", "DeviceQuantity_frequency_1", list_of_devices)

    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    # exhaustive_datalogger = Datalogger("exhaustive_datalogger", "logs")
    # exhaustive_datalogger.add_all()  # add all keys

    # datalogger used to export chosen metrics
    metrics_datalogger = Datalogger("metrics", "Metrics")
    for key in metrics:
        metrics_datalogger.add(key)

    return world


