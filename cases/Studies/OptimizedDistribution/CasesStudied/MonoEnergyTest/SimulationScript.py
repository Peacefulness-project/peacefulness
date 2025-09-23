# Test case to validate the approach using GA to optimize the distribution of energy to individual systems (devices)

# #####################################################################################################################
# Imports
from datetime import datetime
from scipy.stats import gamma

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import *
from src.common.Strategy import Strategy
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger
from src.tools.GraphAndTex import GraphOptions
from src.tools.SubclassesDictionary import get_subclasses
from src.tools.AgentGenerator import agent_generation_GA
import numpy as np



def peacefulness_simulation(name: str, seed: str, pathExport: str, start_time: datetime, timestep: float, finish_time: int, my_seed=0.0, standard_deviation=0.25):
    """
    This function will be used to run the peacefulness simulation.
    """
    # ##############################################################################################
    # Initialization of the world
    # ##############################################################################################
    # Importation of subclasses
    subclasses_dictionary = get_subclasses()

    # World creation
    world_name = name  # the name of the strategy is sufficient to differentiate all the cases since each script is a specific study case which contains its own description at the start
    world = World(world_name)

    # Exportation of results
    world.set_directory(pathExport)  # registration of the obtained results in the specified directory

    # World random seed
    world.set_random_seed(seed)

    # World time manager
    world.set_time(start_time, timestep, finish_time)

    # Optional message to all devices
    world.complete_message("CO2", 0)

    # ##############################################################################################
    # Study case construction
    # ##############################################################################################
    # Natures or energy carriers
    LVE = load_low_voltage_electricity()  # low voltage electricity for a normal dwelling
    LTH = load_low_temperature_heat()  # low temperature heat


    # ##############################################################################################
    # Daemons
    location = "Nantes"

    # Price Managers
    # This daemons fix a price for a given nature of energy
    price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("elec_price", {"buying_price": 0.6, "selling_price": 0.0})   # sets prices for TOU rate
    price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("heat_price", {"buying_price": 0.5, "selling_price": 0.2})  # sets prices for TOU rate

    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.6, "limit_selling_price": 0.0})  # sets limit price accepted
    limit_prices_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.5, "limit_selling_price": 0.2})  # sets limit price accepted

    # Outdoor temperature
    # this daemon is responsible for the value of outside temperature in the catalog
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": location}, exergy=True)
    # ground_temperature_daemon = subclasses_dictionary["Daemon"]["GroundTemperatureDaemon"]({"location": "France"})
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Nantes"})


    # ##############################################################################################
    # Creation of strategies
    # the strategy grid, which always proposes an infinite quantity to sell and to buy
    grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

    policy = subclasses_dictionary["Strategy"]["AlwaysSatisfied"]()


    # ##############################################################################################
    # Manual creation of agents

    DSO_manager = Agent("DSO_manager")  # creation of the electricity distribution agent

    DHN_manager = Agent("DHN_manager")  # creation of the district heating network agent


    # ##############################################################################################
    # Contracts

    network_contract = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_grids", LVE, price_manager_elec)   # this contract is the one between the local DHN and DSO

    contract_heat_BAU = subclasses_dictionary["Contract"]["EgoistContract"]("DHN_prices_BAU", LTH, price_manager_heat)
    contract_heat_coop = subclasses_dictionary["Contract"]["CooperativeContract"]("DHN_prices_COOP", LTH, price_manager_heat)
    # storage_contract = subclasses_dictionary["Contract"]["StorageThresholdPricesContract"]("cooperative_contract_elec", LTH, price_manager_heat, {"buying_threshold": 0.7, "selling_threshold": 0})


    # ##############################################################################################
    # Aggregators
    aggregator_name = "electricity_grid"  # external grid
    aggregator_grid_elec = Aggregator(aggregator_name, LVE, grid_strategy, DSO_manager)

    aggregator_name = "district_heating_network"  # area with industrials
    aggregator_grid_heat = Aggregator(aggregator_name, LTH, policy, DHN_manager, aggregator_grid_elec, network_contract, efficiency=0.85, capacity={"buying": 1000, "selling": 0})  # creation of an aggregator


    # ##############################################################################################
    # Devices
    # np.random.seed(seed=my_seed)
    # def rng_generator(consumption):
    #     if bool(standard_deviation) & bool(consumption):
    #         a = (1 / standard_deviation)**2
    #         b = standard_deviation ** 2 * consumption
    #         toto = gamma.rvs(a, scale=b)
    #         return toto
    #     else:
    #         return consumption


    # Consumption
    # flexible_demand = subclasses_dictionary['Device']["DummyConsumer"]("flexible_heat_demand", contract_heat_coop, DHN_manager, aggregator_grid_heat, {"device": "heat"}, {"max_power": 2400})
    # old_rigid_demand = subclasses_dictionary["Device"]["Background"]("rigid_heat_demand", contract_heat_BAU, DHN_manager, aggregator_grid_heat,
    #                                                             {"user": "old_house", "device": "old_house"}, parameters={"rng_generator": rng_generator},
    #                                                             filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    # new_rigid_demand = subclasses_dictionary["Device"]["Background"]("new_house", contract_heat_BAU, DHN_manager, aggregator_grid_heat,
    #                                                            {"user": "new_house", "device": "new_house"}, parameters={"rng_generator": rng_generator},
    #                                                            filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    # #
    # new_houses = subclasses_dictionary["Device"]["Background"]("new_houses", contract_heat_BAU, DHN_manager, aggregator_grid_heat,
    #                                                            {"user": "new_house", "device": "new_house"}, parameters={"rng_generator": rng_generator},
    #                                                            filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")
    # office_demand = subclasses_dictionary["Device"]["Background"]("office", contract_heat_BAU, DHN_manager, aggregator_grid_heat,
    #                                                            {"user": "office", "device": "new_house"}, parameters={"rng_generator": rng_generator},
    #                                                            filename="cases/Studies/ClusteringAndStrategy/CasesStudied/RampUpManagement/AdditionalData/BackgroundAlternative.json")



    # Production
    # flexible_offer = subclasses_dictionary["Device"]["DummyProducer"]("production", contract_heat_coop, DHN_manager, aggregator_grid_heat, {"device": "heat"}, {"max_power": 1500})
    # biomass_plant = subclasses_dictionary["Device"]["BiomassGasPlantAlternative"]("biomass_plant", contract_heat_coop, DHN_manager, aggregator_grid_heat, {"device": "Biomass_2_ThP"}, {"max_power": 1000, "recharge_quantity": 1800*12, "autonomy": 12, "initial_energy": 300})
    # therm_coll = subclasses_dictionary["Device"]["SolarThermalCollector"]("STC_prod", contract_heat_BAU, DHN_manager, aggregator_grid_heat,
    #                                                                       {"device": "standard_field"}, {"panels": 430, "irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})

    # Storage
    # sensible_heat_storage = subclasses_dictionary["Device"]["SensibleHeatStorage"]("sensible_storage", contract_heat_coop, DHN_manager, aggregator_grid_heat,
    #                                                                                {"device": "industrial_water_tank"}, {"capacity": 1000, "initial_SOC": 1, "initial_temperature": 75, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})
    # latent_heat_storage = subclasses_dictionary["Device"]["LatentHeatStorage"]("latent_storage", storage_contract, DHN_manager, aggregator_grid_heat, {"device": "industrial_water_tank"}, {"capacity": 250, "initial_SOC": 0.69, "initial_temperature": 10, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})
    # underwater_storage = subclasses_dictionary["Device"]["UndergroundThermalStorage"]("heat_storage", contract_heat_coop, DHN_manager, aggregator_grid_heat,
    #                                                                                   {"device": "domestic_storage"}, {"ground_temperature_daemon": ground_temperature_daemon.name, "initial_storage_temperature": 90})


    # Automated generation of agents
    agent_generation_GA("little_heat_district", 10, "cases/Studies/OptimizedDistribution/CasesStudied/MonoEnergyTest/AdditionalData/DistributionAgent.json",
                        aggregator_grid_heat, {"LTH": price_manager_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "irradiation_daemon": irradiation_daemon},
                        my_seed=my_seed,
                        standard_deviation=standard_deviation)

    # ##############################################################################################
    # Dataloggers

    # to get the coverage rate
    # subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"]()
    # performance_metrics = ["local_network.energy_bought_outside", "industrial_process.LVE.energy_bought", "storage.energy_stored"]
    # metrics_datalogger = Datalogger("metrics", "Metrics")
    # for key in performance_metrics:
    #     metrics_datalogger.add(key)
    # to get the financial performance (money spent/earned through the exchange with the main grid)
    # subclasses_dictionary["Datalogger"]["AgentBalancesDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)
    # my_device_list = ["production", "storage", "residential_dwellings", "industrial_process"]
    # energy wanted
    # subclasses_dictionary["Datalogger"]["MinimumEnergyDatalogger"]("device_min_quantity_frequency_1", "DeviceMinQuantity_frequency_1", my_device_list)
    # subclasses_dictionary["Datalogger"]["MaximumEnergyDatalogger"]("device_max_quantity_frequency_1", "DeviceMaxQuantity_frequency_1", my_device_list)
    # energy accorded
    # subclasses_dictionary["Datalogger"]["DeviceQuantityDatalogger"]("device_quantity_frequency_1", "DeviceQuantity_frequency_1", my_device_list, period=1)
    # subclasses_dictionary["Datalogger"]["AllocationDatalogger"]("energy_allocation_frequency_1", "EnergyAllocation_frequency_1", period=1)
    # subclasses_dictionary["Datalogger"]["EquityDatalogger"]("energy_unserved_frequency_1", "EnergyUnserved_frequency_1", period=1)
    # my_ESS_list = ["sensible_storage"]
    # subclasses_dictionary["Datalogger"]["StateOfChargeDatalogger"]("soc_frequency_1", "SOC_frequency_1", my_ESS_list)

    return world

#
#
def my_exogen_inst(world: "World"):
    results = {}
    for datalogger in world.catalog.dataloggers.values():
        datalogger_keys = datalogger.get_keys  # retrieving the keys to be exported by the datalogger
        results = {**results, **datalogger.request_keys(datalogger_keys)}
    print(results)

# Parameters to run the simulation
world_name = "MonoEnergyTest"
world_seed = "sunflower"
world_path = f"cases/Studies/OptimizedDistribution/Results/{world_name}/"
my_start = datetime(year=2020, month=3, day=25, hour=12, minute=0, second=0, microsecond=0)
step = 1
hours_simulated = 2
my_seed = 1
my_std = 0.25

world = peacefulness_simulation(world_name, world_seed, world_path, my_start, step, hours_simulated, my_seed, my_std)
world.start(exogen_instruction=my_exogen_inst, verbose=False)



