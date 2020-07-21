# The correction_1_settings on the tutorial 1 bearing on settings
from src.tools.GlobalWorld import get_world
from datetime import datetime
from os import remove, rmdir


def correction_1_settings():
    world = get_world()

    # creation of world
    if world == None:
        print("The world has not been created successfully.")
        exit()

    # name of world
    if world.name != "tuto_world":
        print("The world does not bear the correct name.")
        exit()

    # creation of path
    if "path" not in world.catalog.keys:
        print("The path has not been successfully defined.")
        exit()

    # path itself
    if world.catalog.get("path") != "cases/Tutorial/BasicTutorial/Results/Settings/Case_" + str(datetime.now().strftime("%Y_%m_%d-%H_%M_%S")):
        print("The path is not the good one.")
        exit()

    # creation of the seed
    if "float" not in world.catalog.keys:
        print("The random seed has not been successfully defined.")
        exit()

    # name of the seed
    if world._random_seed != "sunflower":
        print("The random seed is not the good one.")
        exit()

    # time settings
    if "physical_time" not in world.catalog.keys:
        print("The time settings have not been successfully defined.")
        exit()

    # start date
    if world._catalog.get("physical_time") != datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0):
        print("The start date is not the good one.")
        exit()

    # time step value
    if world._catalog.get("time_step") != 2:
        print("The time step value is not the good one.")
        exit()

    # length
    if world._catalog.get("time_limit") != 84:
        print("The time limit is not the good one.")
        exit()

    print("Congratulations, everything is working well.")


def correction_2_natures():
    world = get_world()

    # loading of LVE nature
    if "LVE" not in world.catalog.natures:
        print("The nature LVE has not been loaded successfully.")
        exit()

    # loading of LTH nature
    if "LTH" not in world.catalog.natures:
        print("The nature LTH has not been loaded successfully.")
        exit()

    # creation of PW nature
    if "PW" not in world.catalog.natures:
        print("The nature PW has not been created successfully.")
        exit()

    # description of PW nature
    if world.catalog.natures["PW"].description != "Pressurized Water":
        print("The description of PW nature is not the good one.")
        exit()

    print("Congratulations, everything is working well.")


def correction_3_daemons():
    world = get_world()

    # creation and name of the price manager elec
    if "elec_prices" not in world.catalog.daemons:
        print("The elec price manager has not been created successfully or does not bear the correct name.")
        exit()

    # elec buying prices
    if world.catalog.daemons["elec_prices"]._buying_price != [0.17, 0.12]:
        print("Electricity buying prices are not the correct ones.")
        exit()

    # elec selling prices
    if world.catalog.daemons["elec_prices"]._selling_price != [0.15, 0.15]:
        print("Electricity selling prices are not the correct ones.")
        exit()

    # elec on-peak hours
    if world.catalog.daemons["elec_prices"]._hours != [6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]:
        print("Electricity on-peak hours are not the correct ones.")
        exit()

    # creation and name of the price manager heat
    if "heat_prices" not in world.catalog.daemons:
        print("The heat price manager has not been created successfully or does not bear the correct name.")
        exit()

    # heat buying prices
    if world.catalog.daemons["heat_prices"]._buying_price != 0.12:
        print("Heat buying prices are not the correct ones.")
        exit()

    # heat selling prices
    if world.catalog.daemons["heat_prices"]._selling_price != 0.10:
        print("Heat selling prices are not the correct ones.")
        exit()

    # creation of limit prices manager elec
    if "grid_prices_manager_for_nature_LVE" not in world.catalog.daemons:
        print("The elec limit prices manager has not been created successfully.")
        exit()

    # limit elec buying price
    if world.catalog.daemons["grid_prices_manager_for_nature_LVE"]._buying_price != 0.20:
        print("Electricity limit buying price is not the correct one.")
        exit()

    # limit elec selling price
    if world.catalog.daemons["grid_prices_manager_for_nature_LVE"]._selling_price != 0.10:
        print("Electricity limit selling price is not the correct one.")
        exit()

    # creation of limit prices manager heat
    if "grid_prices_manager_for_nature_LTH" not in world.catalog.daemons:
        print("The heat limit prices manager has not been created successfully.")
        exit()

    # limit heat buying price
    if world.catalog.daemons["grid_prices_manager_for_nature_LTH"]._buying_price != 0.14:
        print("Heat limit buying price is not the correct one.")
        exit()

    # limit heat selling price
    if world.catalog.daemons["grid_prices_manager_for_nature_LTH"]._selling_price != 0.08:
        print("Heat limit selling price is not the correct one.")
        exit()

    # creation of indoor temperature manager
    if "indoor_temperature_manager" not in world.catalog.daemons:
        print("The indoor temperature manager has not been created successfully.")
        exit()

    # creation of outdoor temperature manager
    exist = False
    for daemon_name in world.catalog.daemons:
        if daemon_name.startswith("outdoor_temperature_in_"):  # the string is the beginning of the name of all outdoor temperature manager
            exist = True
    if not exist:  # if no outdoor temperature manager is found
        print("The outdoor temperature manager has not been created successfully.")
        exit()

    # location of outdoor temperature manager
    if "outdoor_temperature_in_Pau" not in world.catalog.daemons:
        print("The outdoor temperature manager is not placed in the correct location.")
        exit()

    # creation of irradiation manager
    exist = False
    for daemon_name in world.catalog.daemons:
        if daemon_name.startswith("solar_irradiation_in_"):  # the string is the beginning of the name of all irradiation manager
            exist = True
    if not exist:  # if no irradiation manager is found
        print("The irradiation manager has not been created successfully.")
        exit()

    # location of irradiation manager
    if "solar_irradiation_in_Pau" not in world.catalog.daemons:
        print("The irradiation manager is not placed in the correct location.")
        exit()
        
    # creation of wind manager
    exist = False
    for daemon_name in world.catalog.daemons:
        if daemon_name.startswith("wind_speed_in_"):  # the string is the beginning of the name of all wind manager
            exist = True
    if not exist:  # if no wind manager is found
        print("The wind manager has not been created successfully.")
        exit()

    # location of wind manager
    if "wind_speed_in_Pau" not in world.catalog.daemons:
        print("The wind manager is not placed in the correct location.")
        exit()

    print("Congratulations, everything is working well.")


def correction_4_strategies():
    world = get_world()

    # grid strategy
    if "grid_strategy" not in world.catalog.strategies:
        print("The Grid strategy has not been created successfully.")
        exit()

    # always satisfied strategy
    if "always_satisfied_strategy" not in world.catalog.strategies:
        print("The AlwaysSatisfied strategy has not been created successfully.")
        exit()

    # light autarky emergency strategy
    if "light_autarky_emergency_strategy" not in world.catalog.strategies:
        print("The LightAutarkyEmergency strategy has not been created successfully.")
        exit()

    print("Congratulations, everything is working well.")


def correction_5_agents():
    world = get_world()

    # creation of the agent called "PV_producer"
    if "PV_producer" not in world.catalog.agents:
        print("The agent called \"PV_producer\" has not been created successfully or does not bear the correct name.")
        exit()

    # creation of the agent called "aggregators_owner"
    if "aggregators_owner" not in world.catalog.agents:
        print("The agent called \"aggregators_owner\" has not been created successfully or does not bear the correct name.")
        exit()

    # creation of the agent called "random_consumer"
    if "random_consumer" not in world.catalog.agents:
        print("The agent called \"random_consumer\" has not been created successfully or does not bear the correct name.")
        exit()

    print("Congratulations, everything is working well.")


def correction_6_contracts():
    world = get_world()

    # creation of the egoist elec contract
    if "elec_contract_egoist" not in world.catalog.contracts:
        print("The egoist contract for electricity has not been created successfully or does not bear the correct name.")
        exit()

    # nature of egoist elec contract
    if world.catalog.contracts["elec_contract_egoist"].nature.name != "LVE":
        print("Electricity on-peak hours are not the correct ones.")
        exit()

    # price manager of egoist elec contract
    if world.catalog.contracts["elec_contract_egoist"]._daemon_name != "":
        print("Electricity on-peak hours are not the correct ones.")
        exit()

    # name of the agent
    if "PV_producer" not in world.catalog.agents:
        print("The name of your agent is not the good one.")
        exit()

    print("Congratulations, everything is working well.")








