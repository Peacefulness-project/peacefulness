
from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def simulation(DSM_proportion, storage_sizing):
    # ##############################################################################################
    # Settings
    # ##############################################################################################

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = "CISBAT_storage_and_DSM_2021"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/CISBAT_storage_and_DSM_2021/Results/" + DSM_proportion + "_" + storage_sizing  # directory where results are written
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed to be used
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed("sunflower")

    # ##############################################################################################
    # Time Manager
    # it needs a start date, the value of an iteration in hours and the total number of iterations
    start_date = datetime.now()  # a start date in the datetime format
    start_date = start_date.replace(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    world.set_time(start_date,  # time management: start date
                   1,  # value of a time step (in hours)
                   24 * 365)  # number of time steps simulated

    # ##############################################################################################
    # Model creation
    # ##############################################################################################

    # ##############################################################################################
    # Natures
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # low temperature heat
    LTH = load_low_temperature_heat()

    # ##############################################################################################
    # Daemons
    # Price Managers
    # these daemons fix a price for a given nature of energy

    price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_elec", {"nature": LVE.name, "buying_price": , "selling_price": })  # sets prices for the system operator
    price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": , "selling_price": })  # sets prices for the system operator
    price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price": , "selling_price": 0})  # price manager for the local electrical grid
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": , "limit_selling_price": 0})  # sets prices for the system operator


    price_managing_daemon_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_grid", {"nature": LVE.name, "buying_price": , "selling_price": })  # price manager for the local electrical grid
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 0.2, "limit_selling_price": 0.1})  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "France"})

    # Irradiation
    # this daemon is responsible for updating the value of raw solar irradiation
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

    # Wind
    # this daemon is responsible for updating the value of raw solar Wind
    wind_daemon = subclasses_dictionary["Daemon"]["WindSpeedDaemon"]({"location": "Pau"})

    # ##############################################################################################
    # Strategies
    supervisor_elec = subclasses_dictionary["Strategy"][f"LightAutarkyEmergency"]()

    # the national grid strategy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Agents
    PV_producer = Agent("PV_producer")  # the owner of the Photovoltaics panels

    wind_turbine_producer = Agent("wind_turbine_producer")  # the owner of the solar thermal collectors

    national_grid = Agent("national_grid")

    local_electrical_grid_manager = Agent("local_electrical_grid_producer")  # the owner of the Photovoltaics panels

    # ##############################################################################################
    # Contracts
    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_daemon_grid)

    contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_managing_elec)

    contract_ = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_managing_elec)

    # ##############################################################################################
    # Aggregators
    # and then we create a third who represents the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name, LVE, supervisor_elec, local_electrical_grid_manager, aggregator_grid, contract_grid)  # creation of a aggregator

    # ##############################################################################################
    # Devices
    BAU = int((1 - DSM_proportion) * )
    DSM = int(DSM_proportion * )

    subclasses_dictionary["Device"]["PhotovoltaicsAdvanced"]("PV_field", contract_elec, PV_producer, aggregator_elec, {"device": "standard_field"}, {"panels": , "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "irradiation_daemon": irradiation_daemon.name})  # creation of a photovoltaic panel field

    subclasses_dictionary["Device"]["WindTurbine"]("", contract_elec, wind_turbine_producer, aggregator_elec, {"device": "standard"}, {"rugosity": "flat", "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "wind_speed_daemon": wind_daemon.name})  # creation of a wind turbine

    subclasses_dictionary["Device"][""]("energy_storage", contract_elec, PV_producer, aggregator_elec, {"device": "standard_field"}, {"panels": , "outdoor_temperature_daemon": outdoor_temperature_daemon.name, "irradiation_daemon": irradiation_daemon.name})  # creation of the batteries

    # BAU contracts
    world.agent_generation("AgentECOS_1_BAU", , "cases/Studies/CISBAT_storage_and_DSM_2021/AgentTemplates/AgentECOS_1_BAU.json", aggregator_elec, {"LVE": price_managing_elec, "LTH": price_managing_heat})
    world.agent_generation("AgentECOS_2_BAU",  * 2, "cases/Studies/CISBAT_storage_and_DSM_2021/AgentTemplates/AgentECOS_2_BAU.json", aggregator_elec, {"LVE": price_managing_elec, "LTH": price_managing_heat})
    world.agent_generation("AgentECOS_5_BAU", , "cases/Studies/CISBAT_storage_and_DSM_2021/AgentTemplates/Agent_5_p_BAU_no_PV.json", aggregator_elec, {"LVE": price_managing_elec, "LTH": price_managing_heat})

    # Curtailment contracts
    world.agent_generation("AgentECOS_1_curtailment", , "cases/Studies/CISBAT_storage_and_DSM_2021/AgentTemplates/AgentECOS_1_curtailment.json", aggregator_elec, {"LVE": price_managing_elec, "LTH": price_managing_heat})
    world.agent_generation("AgentECOS_2_curtailment", * 2, "cases/Studies/CISBAT_storage_and_DSM_2021/AgentTemplates/AgentECOS_2_curtailment.json", aggregator_elec, {"LVE": price_managing_elec, "LTH": price_managing_heat})
    world.agent_generation("AgentECOS_5_curtailment", , "cases/Studies/CISBAT_storage_and_DSM_2021/AgentTemplates/Agent_5_curtailment_no_PV.json", aggregator_elec, {"LVE": price_managing_elec, "LTH": price_managing_heat})

    # ##############################################################################################
    # Dataloggers
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"]()
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]()

    subclasses_dictionary["Datalogger"]["ECOSAggregatorDatalogger"]()
    subclasses_dictionary["Datalogger"]["MismatchDatalogger"]()

    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")

    producer_datalogger.add(f"PV_producer.LVE.energy_erased")
    producer_datalogger.add(f"solar_thermal_producer.LTH.energy_erased")
    producer_datalogger.add(f"PV_producer.LVE.energy_sold")
    producer_datalogger.add(f"solar_thermal_producer.LTH.energy_sold")

    producer_datalogger.add(f"PV_field_exergy_in")
    producer_datalogger.add(f"solar_thermal_collector_field_exergy_in")
    producer_datalogger.add(f"PV_field_exergy_out")
    producer_datalogger.add(f"solar_thermal_collector_field_exergy_out")

    # ##############################################################################################
    # Simulation
    # ##############################################################################################
    world.start()


