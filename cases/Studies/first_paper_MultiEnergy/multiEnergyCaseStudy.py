# This script is the one deconstructed in the tuto to create a case on the wiki.
from scipy.stats import gamma
import numpy as np

# ##############################################################################################
# Importations
from datetime import datetime
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Gym_World import GymWorld
# from src.common.World import World
# pre-defined natures
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat, load_low_pressure_gas
from src.common.Agent import Agent
from src.common.Aggregator import Aggregator
from src.common.Datalogger import Datalogger
# all the subclasses are imported in the following dictionary
from src.tools.SubclassesDictionary import get_subclasses


def create_simulation(world_name: str, start_date: datetime, hours_simulated: int, path_name: str, metrics: list = [], random_seed: list = [], standard_deviation: float = 0.25, red_dof_flag=False):
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
    world_name = world_name + f"_{random_seed[0]}"
    world = GymWorld(world_name)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    world.set_directory(path_name)  # registration

    # ##############################################################################################
    # Definition of the random seed
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed(random_seed[0])

    # ##############################################################################################
    # Time parameters
    # it needs a start date, the value of an iteration in hours and the total number of iterations
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
    # low temperature heat
    LTH = load_low_temperature_heat()
    # low pressure gas
    LPG = load_low_pressure_gas()

    # ##############################################################################################
    # Creation of daemons

    # Price Managers
    ################
    price_manager_grid = subclasses_dictionary["Daemon"]["PriceManagerRTPDaemon"]("EDN_prices", {"buying_coefficient": 1.1, "selling_coefficient": 0.9, "location": "France"})  # sets prices for EDN
    price_manager_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("MG_prices", {"nature": LVE.name, "buying_price": [0.2, 0.18], "selling_price": [0.06, 0.04], "on-peak_hours": [[5, 9], [17, 21]]})
    price_manager_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("DHN_prices", {"buying_price": 0.08, "selling_price": 0.05})  # sets prices for DHN
    price_manager_gas = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("GDN_prices", {"buying_price": 0.16, "selling_price": 0.0})  # sets prices for GDN
    price_manager_waste = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("waste_prices", {"buying_price": 0.0, "selling_price": 0.04})  # sets prices for waste-to-heat
    # limit prices
    # the following daemons fix the maximum and minimum price at which energy can be exchanged
    limit_prices_elec = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.25, "limit_selling_price": 0.04})  # sets limit price accepted for elecricity
    limit_prices_heat = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 0.08, "limit_selling_price": 0.04})  # sets limit price accepted for heat
    limit_prices_gas = subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LPG.name, "limit_buying_price": 0.16, "limit_selling_price": 0.0})  # sets limit price accepted for gas

    # Data-related Daemons
    ######################
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Nantes"})  # Irradiation
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Nantes"})  # Outdoor temperature
    ground_temperature_daemon = subclasses_dictionary["Daemon"]["GroundTemperatureDaemon"]({"location": "France"})  # Ground temperature
    wind_speed_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Nantes"})  # Wind speed
    cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})  # Cold water temperature
    indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # ##############################################################################################
    # Creation of strategies

    # the training strategy
    strategy_1 = subclasses_dictionary["Strategy"]["SingleAgentDRLStrategy"]("agent_1", red_dof_flag=red_dof_flag)
    strategy_2 = subclasses_dictionary["Strategy"]["SingleAgentDRLStrategy"]("agent_2", red_dof_flag=red_dof_flag)

    # the strategy grid, which always proposes an infinite quantity to sell and to buy
    grid_strategy = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Manual creation of agents
    grid_electricity = Agent("Enedis")  # representative of the electricity distribution network
    grid_gas = Agent("GDF")  # representative of the gas distribution network
    chp_owner = Agent("CHP")  # representative of the owner of the CHP facility
    hp_owner = Agent("HP")  # representative of the owner of the HP
    dhn_proxy = Agent("proxyDHN")
    microgrid_manager = Agent("MG")  # representative of the electricity microgrid manager
    heat_network_manager = Agent("DHN")  # representative of the district heating network manager

    # ##############################################################################################
    # Manual creation of contracts
    BAU_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_manager_elec)  # contract for electricity rigid consumers and producers
    COOP_elec = subclasses_dictionary["Contract"]["CooperativeContract"]("COOP_elec", LVE, price_manager_elec)  # contract for electric devices that accept to be shifted/flexible
    BAU_heat = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_manager_heat)  # contract for heat rigid consumers
    COOP_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("COOP_heat", LTH, price_manager_heat)  # contract for heat storage
    COOP_waste = subclasses_dictionary["Contract"]["CooperativeContract"]("COOP_waste", LTH, price_manager_waste)  # contract for waste-to-heat
    grid_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("grid_elec", LVE, price_manager_grid)  # contract between the microgrid and electricity distribution network
    gas_contract = subclasses_dictionary["Contract"]["CooperativeContract"]("grid_gas", LPG, price_manager_gas)  # contract between the gas distribution network and CHP owner

    # ##############################################################################################
    # Creation of aggregators

    aggregator_name = "national_electricity_distribution_network"  # external electricity grid
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_strategy, grid_electricity)

    aggregator_name = "national_gas_distribution_network"  # external gas grid
    aggregator_gas = Aggregator(aggregator_name, LPG, grid_strategy, grid_gas)

    aggregator_name = "electric_microgrid"  # electric microgrid
    aggregator_elec = Aggregator(aggregator_name, LVE, strategy_1, microgrid_manager, aggregator_grid, grid_contract, efficiency=1, capacity={"buying": 11000, "selling": 18000})

    aggregator_name = "district_heating_network"  # district heating network
    aggregator_heat = Aggregator(aggregator_name, LTH, strategy_2, heat_network_manager, aggregator_elec, grid_contract, efficiency=1, capacity={"buying": 0, "selling": 0})

    # ##############################################################################################
    # Manual creation of devices
    def rng_generator(consumption):
        if bool(standard_deviation) & bool(consumption):
            a = (1 / standard_deviation) ** 2
            b = standard_deviation ** 2 * consumption
            toto = gamma.rvs(a, scale=b, random_state=random_seed[1])
            return toto
        else:
            return consumption

    # Energy conversion systems
    subclasses_dictionary["Device"]["ModifiedHeatPump"]("heat_pump", [COOP_elec, COOP_heat], hp_owner, aggregator_elec, aggregator_heat, {"device": "dual_source_heat_pump_air_mode"},
                                                        parameters={"max_power": 1500, "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "ground_temperature_daemon": ground_temperature_daemon.name})
    subclasses_dictionary["Device"]["ModifiedCombinedHeatAndPower"]("combined_heat_power", [gas_contract, COOP_elec, COOP_heat], chp_owner, aggregator_gas, [aggregator_elec, aggregator_heat],
                                                                    {"device": "test_system"}, parameters={"max_power": 16000})

    # Electricity microgrid devices
    subclasses_dictionary["Device"]["Charger"]("flexible_loads", COOP_elec, microgrid_manager, aggregator_elec, {"user": "family", "device": "flexible_chargers"},
                                               filename="cases/Studies/first_paper_MultiEnergy/AdditionalData/flexibleLoads.json")
    subclasses_dictionary["Device"]["PhotovoltaicsAdvanced"]("PV_field_1", BAU_elec, microgrid_manager, aggregator_elec, {"device": "standard"},
                                                             parameters={"panels": 25000, "irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})
    subclasses_dictionary["Device"]["PhotovoltaicsAdvanced"]("PV_field_2", BAU_elec, microgrid_manager, aggregator_elec, {"device": "standard"},
                                                             parameters={"panels": 25000, "irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})
    subclasses_dictionary["Device"]["WindTurbineAdvanced"]("WT_field_1", BAU_elec, microgrid_manager, aggregator_elec, {"device": "ECOS_high"},
                                                           parameters={"wind_speed_daemon": wind_speed_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "rugosity": "flat"})
    subclasses_dictionary["Device"]["WindTurbineAdvanced"]("WT_field_2", BAU_elec, microgrid_manager, aggregator_elec, {"device": "ECOS_high"},
                                                           parameters={"wind_speed_daemon": wind_speed_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "rugosity": "flat"})
    subclasses_dictionary["Device"]["ResidentialDwelling"]("rigid_electricity_consumption", BAU_elec, microgrid_manager,aggregator_elec,
                                                           {"user": "yearly_consumer","device": "representative_dwelling"},
                                                           parameters={"number": 8000, "rng_generator": rng_generator})

    # District heating network devices
    subclasses_dictionary["Device"]["DummyProducer"]("Waste_to_heat", COOP_waste, heat_network_manager, aggregator_heat, {"device": "heat"}, {"max_power": 12000})
    subclasses_dictionary["Device"]["SensibleHeatStorage"]("Heat_storage", COOP_heat, heat_network_manager, aggregator_heat, {"device": "district_heating_network_TES"},
                                                           parameters={"capacity": 0, "initial_SOC": 0, "initial_temperature": 60, "outdoor_temperature_daemon": outdoor_temperature_daemon.name},
                                                           filename="cases/Studies/first_paper_MultiEnergy/AdditionalData/TES.json")
    subclasses_dictionary["Device"]["Background"]("space_heating", BAU_heat, heat_network_manager, aggregator_heat, {"user": "space_heating", "device": "space_heating"},
                                                  parameters={"rng_generator": rng_generator},
                                                  filename="cases/Studies/first_paper_MultiEnergy/AdditionalData/SpaceHeating.json")

    # Proxy model of the DHN
    subclasses_dictionary["Device"]["DummyHeatNetwork"]("artificial_DHN", COOP_elec, dhn_proxy,aggregator_elec, {"device": "artificial_network"},
                                                        parameters={"pipe_diameter": 0.6, "network_length": 10000, "switch": 2, "nominal_power": 30465.39088, "rng_generator": rng_generator})

    # ##############################################################################################
    # Creation of dataloggers

    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()  # to verify energy conservation constraint
    # for computing the rewards
    list_of_devices = ["flexible_loads", "rigid_electricity_consumption",
                       "PV_field_1", "WT_field_1", "PV_field_2", "WT_field_2",
                       "heat_pump", "combined_heat_power",
                       "Waste_to_heat", "Heat_storage", "space_heating"
                       ]
    subclasses_dictionary["Datalogger"]["DeviceQuantityDatalogger"]("device_quantity_frequency_1", "DeviceQuantity_frequency_1", list_of_devices)

    # datalogger used to export chosen metrics
    metrics_datalogger = Datalogger("metrics", "Metrics")
    for key in metrics:
        metrics_datalogger.add(key)

    # exhaustive_datalogger = Datalogger("exhaustive_datalogger", "logs")
    # exhaustive_datalogger.add_all()  # add all keys

    return world


