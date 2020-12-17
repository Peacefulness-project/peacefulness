
from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def simulation(strategy, DSM_proportion, sizing):
    # ##############################################################################################
    # Settings
    # ##############################################################################################

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = "ECOS_collab_2020"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/LOCIE_1/Iteration_1/Results/" + strategy + "_" + DSM_proportion + "_" + sizing  # directory where results are written
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed to be used
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed("tournesol")

    # ##############################################################################################
    # Time Manager
    # it needs a start date, the value of an iteration in hours and the total number of iterations
    start_date = datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
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

    if sizing == "peak":
        price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [0.281, 0.393], "selling_price": [0.223, 0.223], "on-peak_hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate

        price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.313, "selling_price": 0.993*0.9})  # sets prices for the system operator

        price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price": (0.107+0.223/3.6)/0.9, "selling_price": 0})  # price manager for the local electrical grid regarding the devices

    elif sizing == "mean":
        price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("flat_prices_elec", {"nature": LVE.name, "buying_price": [0.137, 0.192], "selling_price": [0.109, 0.109], "on-peak_hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate

        price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": 0.213, "selling_price": 0.483*0.9})  # sets prices for the system operator

        price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price": (0.104+0.109/3.6)/0.9, "selling_price": 0})  # price manager for the local electrical grid regarding the DHN

    price_managing_daemon_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_grid", {"nature": LVE.name, "buying_price": 0.2, "selling_price": 0.1})  # price manager for the local electrical grid

    # limit prices
    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator

    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": 1, "limit_selling_price": 0})  # sets prices for the system operator

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

    # ##############################################################################################
    # Strategies
    if strategy == "BAU":
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"AlwaysSatisfied"]()
    elif strategy == "Profitable":
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"WhenProfitableEmergency"]()
    elif strategy == "Autarky":
        # the local electrical grid strategy
        supervisor_elec = subclasses_dictionary["Strategy"][f"LightAutarkyEmergency"]()

    # the DHN strategy
    supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

    # the national grid strategy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()

    # ##############################################################################################
    # Agents
    PV_producer = Agent("PV_producer")  # the owner of the Photovoltaics panels

    solar_thermal_producer = Agent("solar_thermal_producer")  # the owner of the solar thermal collectors

    national_grid = Agent("national_grid")

    local_electrical_grid_manager = Agent("local_electrical_grid_producer")  # the owner of the Photovoltaics panels

    DHN_manager = Agent("DHN_producer")  # the owner of the district heating network

    # ##############################################################################################
    # Contracts
    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_daemon_grid)

    contract_DHN = subclasses_dictionary["Contract"]["CooperativeContract"]("DHN_grid", LVE, price_managing_daemon_DHN)

    contract_elec = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_elec", LVE, price_managing_elec)

    contract_heat = subclasses_dictionary["Contract"]["CooperativeContract"]("BAU_heat", LTH, price_managing_heat)

    # ##############################################################################################
    # Aggregators
    # and then we create a third who represents the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

    # here we create a second one put under the orders of the first
    aggregator_name = "general_aggregator"
    aggregator_elec = Aggregator(aggregator_name, LVE, supervisor_elec, local_electrical_grid_manager, aggregator_grid, contract_grid)  # creation of a aggregator

    # here we create another aggregator dedicated to heat
    aggregator_name = "Local_DHN"
    aggregator_heat = Aggregator(aggregator_name, LTH, supervisor_heat, DHN_manager, aggregator_elec, contract_DHN, 3.6, 3800)  # creation of a aggregator

    # ##############################################################################################
    # Devices
    if sizing == "mean":
        panels_elec = 9100
        panels_heat = 4250
    elif sizing == "peak":
        panels_elec = 24300
        panels_heat = 11500

    subclasses_dictionary["Device"]["Photovoltaics"]("PV_field", contract_elec, PV_producer, aggregator_elec, {"device": "standard_field"}, {"panels": panels_elec, "irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})  # creation of a photovoltaic panel field

    subclasses_dictionary["Device"]["SolarThermalCollector"]("solar_thermal_collector_field", contract_heat, solar_thermal_producer, aggregator_heat, {"device": "standard_field"}, {"panels": panels_heat, "irradiation_daemon": irradiation_daemon.name, "outdoor_temperature_daemon": outdoor_temperature_daemon.name})  # creation of a solar thermal collector

    # repartition of contracts according to the chosen proportion
    if DSM_proportion == "high_DSM":
        BAU = 165
        DLC = 200
        curtailment = 135
    elif DSM_proportion == "low_DSM":
        BAU = 335
        DLC = 100
        curtailment = 65
    elif DSM_proportion == "no_DSM":
        BAU = 500
        DLC = 0
        curtailment = 0

    # BAU contracts
    world.agent_generation(BAU, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_1_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation(BAU * 2, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_2_BAU.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation(BAU, "cases/Studies/LOCIE_1/AgentTemplates/Agent_5_p_BAU_no_PV.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # DLC contracts
    world.agent_generation(DLC, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_1_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation(DLC * 2, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_2_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation(DLC, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_5_DLC.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # Curtailment contracts
    world.agent_generation(curtailment, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_1_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation(curtailment * 2, "cases/Studies/LOCIE_1/AgentTemplates/AgentECOS_2_curtailment.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation(curtailment, "cases/Studies/LOCIE_1/AgentTemplates/Agent_5_curtailment_no_PV.json", [aggregator_elec, aggregator_heat], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # ##############################################################################################
    # Dataloggers
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"](period="global")

    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"](period="global")

    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"](period="global")

    subclasses_dictionary["Datalogger"]["PeakToAverageDatalogger"]()

    subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["MismatchDatalogger"](period="global")

    subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period=1)
    subclasses_dictionary["Datalogger"]["SelfSufficiencyDatalogger"](period="global")

    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances")

    producer_datalogger.add(f"simulation_time")
    producer_datalogger.add(f"physical_time")

    producer_datalogger.add(f"PV_producer.LVE.energy_erased")
    producer_datalogger.add(f"solar_thermal_producer.LTH.energy_erased")
    producer_datalogger.add(f"PV_producer.LVE.energy_sold")
    producer_datalogger.add(f"solar_thermal_producer.LTH.energy_sold")

    producer_datalogger.add(f"PV_field_exergy_in")
    producer_datalogger.add(f"solar_thermal_collector_field_exergy_in")
    producer_datalogger.add(f"PV_field_exergy_out")
    producer_datalogger.add(f"solar_thermal_collector_field_exergy_out")

    subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("Heating")
    subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("Heating", "global")

    subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("HotWaterTank")
    subclasses_dictionary["Datalogger"]["DeviceSubclassBalancesDatalogger"]("HotWaterTank", "global")

    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("producer_datalogger_global", "ProducerBalances_global", "global")

    producer_datalogger.add(f"simulation_time")

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


