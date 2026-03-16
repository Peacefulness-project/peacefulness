# This script is the one deconstructed in the tuto to create a case on the wiki.
from typing import Callable, List
from scipy.stats import gamma
import numpy as np

# ##############################################################################################
# Importations
from datetime import datetime, timedelta
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Gym_World import GymWorld
# from src.common.World import World
# pre-defined natures
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity
from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger
# all the subclasses are imported in the following dictionary
from src.tools.SubclassesDictionary import get_subclasses

from cases.Studies.MultiAgent_RL.OptionsManagementFunctions import options_consumption_1, options_production_1, options_consumption_2, options_production_2


def create_simulation(hours_simulated: int, priorities_conso: List, priorities_prod: List, step_name: str, metrics: list = [], delay_days: int = 0, random_seed: int = 0, standard_deviation: int = 0, exogen_instruction: Callable = None):
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
    world = GymWorld(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/MultiAgent_RL/Results/RBS" + step_name
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed(random_seed)

    # ##############################################################################################
    # Time parameters
    # it needs a start date, the value of an iteration in hours and the total number of iterations
    start_date = datetime(year=2023, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=delay_days)
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
    strategy_1 = MLStrategy(priorities_conso[0], priorities_prod[0], "strategy_1")
    strategy_1.add_consumption_options(options_consumption_1)
    strategy_1.add_production_options(options_production_1)

    strategy_2 = MLStrategy(priorities_conso[1], priorities_prod[1],  "strategy_2")
    strategy_2.add_consumption_options(options_consumption_2)
    strategy_2.add_production_options(options_production_2)

    # the strategy grid, which always proposes an infinite quantity to sell and to buy
    grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Manual creation of agents

    grid_manager = Agent("Enedis")  # creation of an agent

    community_1 = Agent("community_1")

    community_2 = Agent("community_2")

    elec_inter = Agent("electric_interconnection")

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
    subclasses_dictionary["Device"]["DummyConverter"]("cable_elec_1", [COOP_elec, COOP_elec_residential], elec_inter, aggregator_elec_2, aggregator_elec_1, {"device": "electricity_cable"}, parameters={"max_power": 4000})
    subclasses_dictionary["Device"]["DummyConverter"]("cable_elec_2", [COOP_elec_residential, COOP_elec], elec_inter, aggregator_elec_1, aggregator_elec_2, {"device": "electricity_cable"}, parameters={"max_power": 4000})

    # ##############################################################################################
    # Creation of dataloggers
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()
    # subclasses_dictionary['Datalogger']["SelfSufficiencyDatalogger"]()
    # subclasses_dictionary["Datalogger"]["AgentBalancesDatalogger"]()

    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    # exhaustive_datalogger = Datalogger("exhaustive_datalogger", "logs")
    # exhaustive_datalogger.add_all()  # add all keys
    device_list = ["PV_field_1", "WT_field_1", "Diesel_generator", "storage", "residential_dwellings", "cable_elec_1", "cable_elec_2", "Step", "industrial_process"]
    subclasses_dictionary["Datalogger"]["DeviceQuantityDatalogger"]("device_quantity_frequency_1", "DeviceQuantity_frequency_1", device_list, period=1)
    #
    # my_device_list = ["mirror_first_floor", "mirror_second_floor", "mirror_third_floor", "mirror_roof_PV", "mirror_localDieselGenerator", "mirror_BESS"]
    # subclasses_dictionary["Datalogger"]["DeviceQuantityDatalogger"]("device_quantity_frequency_1", "DeviceQuantity_frequency_1", my_device_list, period=1)
    # subclasses_dictionary["Datalogger"]["MinimumEnergyDatalogger"]("device_min_quantity_frequency_1", "DeviceMinQuantity_frequency_1", my_device_list, period=1)
    # subclasses_dictionary["Datalogger"]["MaximumEnergyDatalogger"]("device_max_quantity_frequency_1", "DeviceMaxQuantity_frequency_1", my_device_list, period=1)
    # my_ESS_list = ["mirror_BESS"]
    # subclasses_dictionary["Datalogger"]["StateOfChargeDatalogger"]("soc_frequency_1", "SOC_frequency_1", my_ESS_list)
    # subclasses_dictionary["Datalogger"]["MEGstateDatalogger"]("mirror_state_frequency_1", "MEG_state_frequency_1", my_device_list, aggregator_name)
    # subclasses_dictionary["Datalogger"]["ExpertStrategyDatalogger"]("mirror_expert_action_frequency_1", "Expert_data_frequency_1", my_device_list, aggregator_name)

    # datalogger used to export chosen metrics
    metrics_datalogger = Datalogger("metrics", "Metrics")
    for key in metrics:
        metrics_datalogger.add(key)
    metrics_datalogger.add("residential_dwellings.LVE.money_spent")
    metrics_datalogger.add("residential_dwellings.LVE.energy_bought")
    metrics_datalogger.add("industrial_process.LVE.money_spent")
    metrics_datalogger.add("industrial_process.LVE.energy_bought")
    # metrics_datalogger.add("mirror_first_floor.LVE.energy_bought")
    # metrics_datalogger.add("mirror_second_floor.LVE.energy_bought")
    # metrics_datalogger.add("mirror_third_floor.LVE.energy_bought")
    # metrics_datalogger.add("mirror_roof_PV.LVE.energy_sold")
    # metrics_datalogger.add("mirror_localDieselGenerator.LVE.energy_sold")
    # metrics_datalogger.add("mirror_BESS.LVE.energy_bought")
    # metrics_datalogger.add("mirror_BESS.LVE.energy_sold")
    # metrics_datalogger.add("mirror_BESS.energy_stored")
    # metrics_datalogger.add("mirror_home_aggregator.energy_bought_outside")
    # metrics_datalogger.add("mirror_home_aggregator.energy_sold_outside")

    world.start(exogen_instruction=exogen_instruction, verbose=True)

    return metrics_datalogger