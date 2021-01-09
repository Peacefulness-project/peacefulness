
from datetime import datetime

from src.common.World import World
from lib.DefaultNatures.DefaultNatures import load_low_voltage_electricity, load_low_temperature_heat
from src.common.Aggregator import Aggregator
from src.common.Agent import Agent
from src.common.Datalogger import Datalogger

from src.tools.SubclassesDictionary import get_subclasses
subclasses_dictionary = get_subclasses()


def simulation(DSM_proportion):
    # ##############################################################################################
    # Settings
    # ##############################################################################################

    # ##############################################################################################
    # Creation of the world
    # a world <=> a case, it contains all the model
    # a world needs just a name
    name_world = "ECOS_collab_2021"
    world = World(name_world)  # creation

    # ##############################################################################################
    # Definition of the path to the files
    pathExport = "cases/Studies/ECOS_collab_2021/Results/"+ DSM_proportion # directory where results are written
    world.set_directory(pathExport)  # registration

    # ##############################################################################################
    # Definition of the random seed to be used
    # The default seed is the current time (the value returned by datetime.now())
    world.set_random_seed("tournesol")

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

    # old grid prices
    price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [, ], "selling_price": [0., 0.], "hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
    price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price": , "selling_price": })  # sets prices for the system operator

    price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price": , "selling_price": 0})  # price manager for the local electrical grid

    # new grid prices
    price_managing_elec = subclasses_dictionary["Daemon"]["PriceManagerTOUDaemon"]("TOU_prices_elec", {"nature": LVE.name, "buying_price": [, ], "selling_price": [0., 0.], "hours": [[6, 12], [14, 23]]})  # sets prices for TOU rate
    price_managing_heat = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("flat_prices_heat", {"nature": LTH.name, "buying_price":, "selling_price":})  # sets prices for the system operator

    price_managing_daemon_DHN = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_DHN", {"nature": LTH.name, "buying_price":, "selling_price": 0})  # price manager for the local electrical grid


    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LTH.name, "limit_buying_price": , "limit_selling_price": 0})  # sets prices for the system operator

    price_managing_daemon_grid = subclasses_dictionary["Daemon"]["PriceManagerDaemon"]("prices_grid", {"nature": LVE.name, "buying_price": , "selling_price": })  # price manager for the local electrical grid

    subclasses_dictionary["Daemon"]["LimitPricesDaemon"]({"nature": LVE.name, "limit_buying_price": , "limit_selling_price": })  # sets prices for the system operator

    # Outdoor temperature
    # this daemon is responsible for the value of outdoor temperature in the catalog
    outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

    # Indoor temperature
    # this daemon is responsible for the value of indoor temperatures in the catalog
    subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

    # Water temperature
    # this daemon is responsible for the value of the water temperature in the catalog
    cold_water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterTemperatureDaemon"]({"location": "Pau"})

    # Irradiation
    # this daemon is responsible for updating the value of raw solar irradiation
    irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})


    # ##############################################################################################
    # Strategies
    # the local electrical grid strategy
    supervisor_elec = subclasses_dictionary["Strategy"][f"LightAutarkyEmergency"]()

    # the DHN strategy
    supervisor_heat = subclasses_dictionary["Strategy"][f"SubaggregatorHeatEmergency"]()

    # the national grid strategy
    grid_supervisor = subclasses_dictionary["Strategy"]["Grid"]()


    # ##############################################################################################
    # Agents
    national_grid = Agent("national_grid")

    local_electrical_grid_manager = Agent("local_electrical_grid_manager")  # the owner of the Photovoltaics panels

    old_DHN_manager = Agent("old_DHN_manager")  # the owner of the old district heating network

    new_DHN_manager = Agent("new_DHN_manager")  # the owner of the new district heating network

    solar_thermal_producer = Agent("solar_thermal_producer")  # the producer of solar thermal collectors 

    biomass_plant_producer = Agent("biomass_plant_producer")  # the producer of the biomass plant
    

    # ##############################################################################################
    # Contracts
    contract_grid = subclasses_dictionary["Contract"]["EgoistContract"]("elec_grid", LVE, price_managing_daemon_grid)

    contract_DHN = subclasses_dictionary["Contract"]["EgoistContract"]("DHN_grid", LTH, price_managing_daemon_DHN)

    contract_heat = subclasses_dictionary["Contract"]["EgoistContract"]("BAU_heat", LTH, price_managing_heat)


    # ##############################################################################################
    # Aggregators
    # ##############################################################################################
    # Aggregators
    
    # the grid
    aggregator_name = "Enedis"
    aggregator_grid = Aggregator(aggregator_name, LVE, grid_supervisor, national_grid)

    # local electrical grid
    aggregator_name = "electrical_aggregator"
    aggregator_elec = Aggregator(aggregator_name, LVE, supervisor_elec, local_electrical_grid_manager, aggregator_grid, contract_grid)  # creation of a aggregator

    # old aggregator dedicated to heat
    aggregator_name = "Local_DHN_old"
    aggregator_heat_old = Aggregator(aggregator_name, LTH, supervisor_heat, old_DHN_manager, aggregator_elec, contract_DHN, 3.6, )  # creation of a aggregator

    # new aggregator dedicated to heat
    aggregator_name = "Local_DHN_new"
    aggregator_heat_new = Aggregator(aggregator_name, LTH, supervisor_heat, new_DHN_manager, aggregator_heat_old, contract_DHN, 1, )  # creation of a aggregator


    # ##############################################################################################
    # Devices

    # repartition of contracts according to the chosen proportion
    if DSM_proportion == "no_DSM":
        BAU = 500
        DLC = 0
        curtailment = 0
        biomass_capacity =
        ST_surface =
    elif DSM_proportion == "DSM":
        BAU = 250
        DLC = 150
        curtailment = 100
        biomass_capacity =
        ST_surface =

    subclasses_dictionary["Device"]["SolarThermalCollector"]("solar_thermal_collector_field", contract_heat, solar_thermal_producer, aggregator_heat_new, {"device": "standard_field"}, {"surface": ST_surface, "irradiation_daemon": irradiation_daemon.name})  # creation of a solar thermal collector

    subclasses_dictionary["Device"]["BiomassPlant"]("biomass_plant", contract_heat, biomass_plant_producer, aggregator_heat_new, {"device": "standard"}, {"max_power": biomass_capacity})  # creation of a solar thermal collector

    # old DHN
    # BAU contracts
    world.agent_generation("old_DHN_BAU_1", BAU, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_BAU.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("old_DHN_BAU_2", BAU * 2, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_BAU.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("old_DHN_BAU_5", BAU, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_5_BAU_no_PV.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # DLC contracts
    world.agent_generation("old_DHN_DLC_1", DLC, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_DLC.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("old_DHN_DLC_2", DLC * 2, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_DLC.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("old_DHN_DLC_5", DLC, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_5_DLC.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # Curtailment contracts
    world.agent_generation("old_DHN_curtailment_1", curtailment, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_curtailment.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("old_DHN_curtailment_2", curtailment * 2, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_curtailment.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("old_DHN_curtailment_5", curtailment, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_5_curtailment_no_PV.json", [aggregator_elec, aggregator_heat_old], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # new DHN
    # BAU contracts
    world.agent_generation("new_DHN_BAU_1", int(BAU*0.3), "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_BAU.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("new_DHN_BAU_2", int(BAU*0.3)*2, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_BAU.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("new_DHN_BAU_5", int(BAU*0.3) , "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_5_BAU_no_PV.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # DLC contracts
    world.agent_generation("new_DHN_DLC_1", int(DLC*0.3), "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_DLC.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("new_DHN_DLC_2", int(DLC*0.3) * 2, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_DLC.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("new_DHN_DLC_5", int(DLC*0.3), "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_5_DLC.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})

    # Curtailment contracts
    world.agent_generation("new_DHN_DLC_1", int(curtailment*0.3), "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_1_curtailment.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("new_DHN_DLC_2", int(curtailment*0.3) * 2, "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_2_curtailment.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})
    world.agent_generation("new_DHN_DLC_5", int(curtailment*0.3), "cases/Studies/ECOS_collab_2021/AgentTemplates/AgentECOS_5_curtailment_no_PV.json", [aggregator_elec, aggregator_heat_new], {"LVE": price_managing_elec, "LTH": price_managing_heat}, {"outdoor_temperature_daemon": outdoor_temperature_daemon, "cold_water_temperature_daemon": cold_water_temperature_daemon})


    # ##############################################################################################
    # Dataloggers
    # datalogger for balances
    # these dataloggers record the balances for each agent, contract, nature and  cluster
    subclasses_dictionary["Datalogger"]["ContractBalancesDatalogger"]()
    subclasses_dictionary["Datalogger"]["AggregatorBalancesDatalogger"]()
    subclasses_dictionary["Datalogger"]["NatureBalancesDatalogger"]()

    subclasses_dictionary["Datalogger"]["MismatchDatalogger"]()

    # datalogger used to get back producer outputs
    producer_datalogger = Datalogger("producer_datalogger", "ProducerBalances.txt")

    producer_datalogger.add(f"biomass_plant_producer.LTH.energy_erased")
    producer_datalogger.add(f"solar_thermal_producer.LTH.energy_erased")
    producer_datalogger.add(f"biomass_plant_producer.LTH.energy_sold")
    producer_datalogger.add(f"solar_thermal_producer.LTH.energy_sold")

    producer_datalogger.add(f"solar_thermal_collector_field.exergy_in")
    producer_datalogger.add(f"solar_thermal_collector_field.exergy_out")
    producer_datalogger.add(f"biomass_plant.exergy_in")
    producer_datalogger.add(f"biomass_plant.exergy_out")


    # ##############################################################################################
    # Simulation
    # ##############################################################################################
    world.start()


