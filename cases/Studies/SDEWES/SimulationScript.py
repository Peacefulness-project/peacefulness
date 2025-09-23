# This script is the one deconstructed in the tuto to create a case on the wiki.
from typing import Callable
from scipy.stats import gamma
import numpy as np

# ##############################################################################################
# Importations
from datetime import datetime, timedelta
from src.common.World import World
# pre-defined natures
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity
from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger
# all the subclasses are imported in the following dictionary
from src.tools.SubclassesDictionary import get_subclasses

from cases.Studies.SDEWES.OptionsManagementFunctions import options_consumption, options_production


def create_simulation(hours_simulated: int, priorities_conso: Callable, priorities_prod: Callable, step_name: str, metrics: list = [], delay_days: int = 0, random_seed: int = 0, standard_deviation: int = 0, exogen_instruction: Callable = None):
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
    pathExport = "cases/Studies/SDEWES/Results/" + step_name
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed(random_seed)

    # ##############################################################################################
    # Time parameters
    # it needs a start date, the value of an iteration in hours and the total number of iterations
    start_date = datetime(year=2023, month=7, day=15, hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=delay_days)
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
    price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices", {"buying_price": 0.6, "selling_price": 0.3})  # sets prices for TOU rate
    price_manager_fuel = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("fuel_prices", {"buying_price": 0.0, "selling_price": 0.45})  # sets prices for fuel
    price_manager_inside = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("insider_prices", {"buying_price": 0.0, "selling_price": 0.0})  # sets prices for TOU rate
    # TOU_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("coop_prices", {"buying_price": 0.6, "selling_price": 0.3})
    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_elec_grid = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.6, "limit_selling_price": 0.3})  # sets limit price accepted

    # Data-related Daemons
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": location})  # Irradiation

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
    aggregator_manager = Agent("Enedis")  # representative of the grid
    house_manager = Agent("Dwelling")  # representative of the dwelling

    # ##############################################################################################
    # Manual creation of contracts
    BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec)
    BAU_elec_PV = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec_PV", LVE, price_manager_inside)
    COOP_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("COOP_elec", LVE, price_manager_elec)
    # curtailment_contract = subclasses_dictionary["Contract"]["LimitedCurtailmentContract"]("curtail_contract", LVE, price_manager_elec, {"curtailment_hours": 5, "rotation_duration": 168})  # a contract
    COOP_elec_DG = subclasses_dictionary["Contract"]["CooperativeContract"]("COOP_elec_DG", LVE, price_manager_fuel)
    COOP_elec_BESS = subclasses_dictionary["Contract"]["CooperativeContract"]("COOP_elec_BESS", LVE, price_manager_inside)

    # ##############################################################################################
    # Creation of aggregators

    aggregator_name = "grid_aggregator"  # external grid
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, aggregator_manager)

    aggregator_name = "mirror_home_aggregator"  # area with industrials
    aggregator_elec = Aggregator(aggregator_name, LVE, strategy, house_manager, aggregator_grid, COOP_elec, efficiency=1, capacity={"buying": 3.5, "selling": 2})  # creation of an aggregator

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

    # base plant
    subclasses_dictionary["Device"]["ResidentialDwelling"]("mirror_first_floor", BAU_elec, house_manager, aggregator_elec, {"user": "yearly_consumer", "device": "representative_dwelling"}, parameters={"number": 1, "rng_generator": rng_generator})
    subclasses_dictionary["Device"]["ResidentialDwelling"]("mirror_second_floor", BAU_elec, house_manager, aggregator_elec, {"user": "yearly_consumer", "device": "representative_dwelling"}, parameters={"number": 1, "rng_generator": rng_generator})
    subclasses_dictionary["Device"]["ResidentialDwelling"]("mirror_third_floor", BAU_elec, house_manager, aggregator_elec, {"user": "yearly_consumer", "device": "representative_dwelling"}, parameters={"number": 1, "rng_generator": rng_generator})
    subclasses_dictionary["Device"]["Photovoltaics"]("mirror_roof_PV", BAU_elec_PV, house_manager, aggregator_elec, {"device": "standard"}, {"panels": 12, "irradiation_daemon": irradiation_daemon.name, "location": "Nantes"})
    subclasses_dictionary["Device"]["DummyProducer"]("mirror_localDieselGenerator", COOP_elec_DG, house_manager, aggregator_elec, {"device": "elec"}, {"max_power": 1.25})
    subclasses_dictionary["Device"]["ElectricalBattery"]("mirror_BESS", COOP_elec_BESS, house_manager, aggregator_elec, {"device": "ECOS2025"}, {"capacity": 3, "initial_SOC": 0.3}, filename="cases/Studies/SDEWES/AdditionalData/ElectricalBattery.json")

    # ##############################################################################################
    # Creation of dataloggers
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()
    subclasses_dictionary['Datalogger']["SelfSufficiencyDatalogger"]()
    # subclasses_dictionary["Datalogger"]["AgentBalancesDatalogger"]()

    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    exhaustive_datalogger = Datalogger("exhaustive_datalogger", "logs")
    exhaustive_datalogger.add_all()  # add all keys

    my_device_list = ["mirror_first_floor", "mirror_second_floor", "mirror_third_floor", "mirror_roof_PV", "mirror_localDieselGenerator", "mirror_BESS"]
    subclasses_dictionary["Datalogger"]["DeviceQuantityDatalogger"]("device_quantity_frequency_1", "DeviceQuantity_frequency_1", my_device_list, period=1)
    subclasses_dictionary["Datalogger"]["MinimumEnergyDatalogger"]("device_min_quantity_frequency_1", "DeviceMinQuantity_frequency_1", my_device_list, period=1)
    subclasses_dictionary["Datalogger"]["MaximumEnergyDatalogger"]("device_max_quantity_frequency_1", "DeviceMaxQuantity_frequency_1", my_device_list, period=1)
    my_ESS_list = ["mirror_BESS"]
    subclasses_dictionary["Datalogger"]["StateOfChargeDatalogger"]("soc_frequency_1", "SOC_frequency_1", my_ESS_list)
    subclasses_dictionary["Datalogger"]["MEGstateDatalogger"]("mirror_state_frequency_1", "MEG_state_frequency_1", my_device_list, aggregator_name)
    subclasses_dictionary["Datalogger"]["ExpertStrategyDatalogger"]("mirror_expert_action_frequency_1", "Expert_data_frequency_1", my_device_list, aggregator_name)

    # datalogger used to export chosen metrics
    metrics_datalogger = Datalogger("metrics", "Metrics")
    for key in metrics:
        metrics_datalogger.add(key)
    metrics_datalogger.add("mirror_first_floor.LVE.energy_bought")
    metrics_datalogger.add("mirror_second_floor.LVE.energy_bought")
    metrics_datalogger.add("mirror_third_floor.LVE.energy_bought")
    metrics_datalogger.add("mirror_roof_PV.LVE.energy_sold")
    metrics_datalogger.add("mirror_localDieselGenerator.LVE.energy_sold")
    metrics_datalogger.add("mirror_BESS.LVE.energy_bought")
    metrics_datalogger.add("mirror_BESS.LVE.energy_sold")
    metrics_datalogger.add("mirror_BESS.energy_stored")
    metrics_datalogger.add("mirror_home_aggregator.energy_bought_outside")
    metrics_datalogger.add("mirror_home_aggregator.energy_sold_outside")

    world.start(exogen_instruction=exogen_instruction, verbose=False)

    return metrics_datalogger