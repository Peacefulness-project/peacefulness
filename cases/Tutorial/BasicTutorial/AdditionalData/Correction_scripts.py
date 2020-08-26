# The correction_1_settings on the tutorial 1 bearing on settings
from src.tools.GlobalWorld import get_world
from datetime import datetime
from os import remove, rmdir
from math import inf


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
    if world._catalog.get("time_step") != 1:
        print("The time step value is not the good one.")
        exit()

    # length
    if world._catalog.get("time_limit") != 168:
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
    if "producer" not in world.catalog.agents:
        print("The agent called producer has not been created successfully or does not bear the correct name.")
        exit()

    # creation of the agent called "aggregators_owner"
    if "aggregators_owner" not in world.catalog.agents:
        print("The agent called aggregators_owner has not been created successfully or does not bear the correct name.")
        exit()

    # creation of the agent called "consumer"
    if "consumer" not in world.catalog.agents:
        print("The agent called consumer has not been created successfully or does not bear the correct name.")
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
        print("The nature of the egoist contract for electricity is not the correct one.")
        exit()

    # price manager of egoist elec contract
    if world.catalog.contracts["elec_contract_egoist"]._daemon_name != "elec_prices":
        print("The price manager of the egoist contract for electricity is not the correct one.")
        exit()

    # creation of the curtailment elec contract
    if "elec_contract_curtailment" not in world.catalog.contracts:
        print("The curtailment contract for electricity has not been created successfully or does not bear the correct name.")
        exit()

    # nature of curtailment elec contract
    if world.catalog.contracts["elec_contract_curtailment"].nature.name != "LVE":
        print("The nature of the curtailment contract for electricity is not the correct one.")
        exit()

    # price manager of curtailment elec contract
    if world.catalog.contracts["elec_contract_curtailment"]._daemon_name != "elec_prices":
        print("The price manager of the curtailment contract for electricity is not the correct one.")
        exit()

    # creation of the cooperative heat contract
    if "heat_contract_cooperative" not in world.catalog.contracts:
        print("The cooperative contract for heat has not been created successfully or does not bear the correct name.")
        exit()

    # nature of cooperative heat contract
    if world.catalog.contracts["heat_contract_cooperative"].nature.name != "LTH":
        print("The nature of the cooperative contract for heat is not the correct one.")
        exit()

    # price manager of cooperative heat contract
    if world.catalog.contracts["heat_contract_cooperative"]._daemon_name != "heat_prices":
        print("The price manager of the cooperative contract for heat is not the correct one.")
        exit()

    print("Congratulations, everything is working well.")


def correction_7_aggregators():
    world = get_world()

    # creation of the aggregator called grid
    if "grid" not in world.catalog.aggregators:
        print("The aggregator called grid has not been created successfully or does not bear the correct name.")
        exit()

    # nature of the grid
    if world.catalog.aggregators["grid"].nature.name != "LVE":
        print("The nature of the grid aggregator is not the correct one.")
        exit()

    # strategy of the grid
    if world.catalog.aggregators["grid"]._strategy.name != "grid_strategy":
        print("The strategy of the grid aggregator is not the correct one.")
        exit()

    # agent of the grid
    if world.catalog.aggregators["grid"].agent.name != "aggregators_owner":
        print("The agent of the grid aggregator is not the correct one.")
        exit()

    # creation of the aggregator called aggregator_elec
    if "aggregator_elec" not in world.catalog.aggregators:
        print("The aggregator called aggregator_elec has not been created successfully or does not bear the correct name.")
        exit()

    # nature of the aggregator_elec
    if world.catalog.aggregators["aggregator_elec"].nature.name != "LVE":
        print("The nature of the aggregator_elec aggregator is not the correct one.")
        exit()

    # strategy of the aggregator_elec
    if world.catalog.aggregators["aggregator_elec"]._strategy.name != "always_satisfied_strategy":
        print("The strategy of the aggregator_elec aggregator is not the correct one.")
        exit()

    # agent of the aggregator_elec
    if world.catalog.aggregators["aggregator_elec"].agent.name != "aggregators_owner":
        print("The agent of the aggregator_elec aggregator is not the correct one.")
        exit()

    # superior of the aggregator_elec
    if world.catalog.aggregators["aggregator_elec"].superior.name != "grid":
        print("The superior of the aggregator_elec aggregator is not the correct one.")
        exit()

    # contract of the aggregator_elec
    if world.catalog.aggregators["aggregator_elec"]._contract.name != "elec_contract_egoist":
        print("The contract of the aggregator_elec aggregator is not the correct one.")
        exit()

    # efficiency of the aggregator_elec
    if world.catalog.aggregators["aggregator_elec"].efficiency != 1:
        print("The efficiency of the aggregator_elec aggregator is not the correct one.")
        exit()

    # capacity of the aggregator_elec
    if world.catalog.aggregators["aggregator_elec"].capacity != inf:
        print("The capacity of the aggregator_elec aggregator is not the correct one.")
        exit()

    # creation of the aggregator called aggregator_heat
    if "aggregator_heat" not in world.catalog.aggregators:
        print("The aggregator called aggregator_heat has not been created successfully or does not bear the correct name.")
        exit()

    # nature of the aggregator_heat
    if world.catalog.aggregators["aggregator_heat"].nature.name != "LTH":
        print("The nature of the aggregator_heat aggregator is not the correct one.")
        exit()

    # strategy of the aggregator_heat
    if world.catalog.aggregators["aggregator_heat"]._strategy.name != "light_autarky_emergency_strategy":
        print("The strategy of the aggregator_heat aggregator is not the correct one.")
        exit()

    # agent of the aggregator_heat
    if world.catalog.aggregators["aggregator_heat"].agent.name != "aggregators_owner":
        print("The agent of the aggregator_heat aggregator is not the correct one.")
        exit()

    # superior of the aggregator_heat
    if world.catalog.aggregators["aggregator_heat"].superior.name != "aggregator_elec":
        print("The superior of the aggregator_heat aggregator is not the correct one.")
        exit()

    # contract of the aggregator_heat
    if world.catalog.aggregators["aggregator_heat"]._contract.name != "elec_contract_egoist":
        print("The contract of the aggregator_heat aggregator is not the correct one.")
        exit()

    # efficiency of the aggregator_heat
    if world.catalog.aggregators["aggregator_heat"].efficiency != 3.5:
        print("The efficiency of the aggregator_heat aggregator is not the correct one.")
        exit()

    # capacity of the aggregator_heat
    if world.catalog.aggregators["aggregator_heat"].capacity != 1000:
        print("The capacity of the aggregator_heat aggregator is not the correct one.")
        exit()

    print("Congratulations, everything is working well.")


def correction_8_devices():
    world = get_world()
    LVE = world.catalog.natures["LVE"]
    LTH = world.catalog.natures["LTH"]

    # creation of the PV field
    if "PV_field" not in world.catalog.devices:
        print("The device called PV_field has not been created successfully or does not bear the correct name.")
        exit()

    # contract of the PV field
    if world.catalog.devices["PV_field"].natures[LVE]["contract"].name != "elec_contract_egoist":
        print("The contract of the PV device is not the correct one.")
        exit()

    # agent of the PV field
    if world.catalog.devices["PV_field"].agent.name != "producer":
        print("The agent of the PV device is not the correct one.")
        exit()

    # aggregator of the PV field
    if world.catalog.devices["PV_field"].natures[LVE]["aggregator"].name != "aggregator_elec":
        print("The aggregator of the PV device is not the correct one.")
        exit()

    # technical data of the PV field
    if world.catalog.devices["PV_field"]._efficiency != 0.15:
        print("The technical data profile of the PV device is not the correct one.")
        exit()

    # surface of the PV field
    if world.catalog.devices["PV_field"]._surface != 1000:
        print("The surface of the PV device is not the correct one.")
        exit()

    # location of the PV field
    if world.catalog.devices["PV_field"]._location != "Pau":
        print("The location of the PV device is not the correct one.")
        exit()

    # creation of the wind turbine
    if "wind_turbine" not in world.catalog.devices:
        print("The device called wind_turbine has not been created successfully or does not bear the correct name.")
        exit()

    # contract of the wind turbine
    if world.catalog.devices["wind_turbine"].natures[LVE]["contract"].name != "elec_contract_curtailment":
        print("The contract of the wind turbine is not the correct one.")
        exit()

    # agent of the wind turbine
    if world.catalog.devices["wind_turbine"].agent.name != "producer":
        print("The agent of the wind turbine is not the correct one.")
        exit()

    # aggregator of the wind turbine
    if world.catalog.devices["wind_turbine"].natures[LVE]["aggregator"].name != "aggregator_elec":
        print("The aggregator of the wind turbine is not the correct one.")
        exit()

    # technical data of the wind turbine
    if world.catalog.devices["wind_turbine"]._efficiency != 0.3 and world.catalog.devices["wind_turbine"]._power != 1500:
        print("The technical data profile of the wind turbine is not the correct one.")
        exit()

    # location of the wind turbine
    if world.catalog.devices["wind_turbine"]._location != "Pau":
        print("The location of the wind turbine is not the correct one.")
        exit()

    # creation of the background
    if "background" not in world.catalog.devices:
        print("The device called background has not been created successfully or does not bear the correct name.")
        exit()

    # contract of the background
    if world.catalog.devices["background"].natures[LVE]["contract"].name != "elec_contract_egoist":
        print("The contract of the background is not the correct one.")
        exit()

    # agent of the background
    if world.catalog.devices["background"].agent.name != "consumer":
        print("The agent of the background is not the correct one.")
        exit()

    # aggregator of the background
    if world.catalog.devices["background"].natures[LVE]["aggregator"].name != "aggregator_elec":
        print("The aggregator of the background is not the correct one.")
        exit()

    # user profile of the background
    if world.catalog.devices["background"]._period != 24 and world.catalog.devices["background"]._offset != 0:
        print("The user profile of the background is not the correct one.")
        exit()

    # technical data of the background
    if world.catalog.devices["background"]._technical_profile != {'LVE': [0.059303467517459935, 0.18977109605587178, 0.17791040255237978, 0.16604970904888783, 0.09488554802793589, 0.17791040255237978, 0.13046762853841185, 0.9369947867758669, 0.33209941809777566, 1.4232832204190382, 0.22535317656634773, 2.609352570768237, 0.6641988361955513, 0.28465664408380764, 0.16604970904888783, 0.14232832204190382, 0.21349248306285573, 0.9962982542933267, 1.2216514308596746, 1.0911838023212628, 0.9607161737828509, 1.8621288800482418, 1.5300294619504662, 2.633073957775221, 0.059303467517459935, 0.18977109605587178, 0.17791040255237978, 0.16604970904888783, 0.09488554802793589, 0.17791040255237978, 0.13046762853841185, 0.9369947867758669, 0.33209941809777566, 1.4232832204190382, 0.22535317656634773, 2.609352570768237, 0.6641988361955513, 0.28465664408380764, 0.16604970904888783, 0.14232832204190382, 0.21349248306285573, 0.9962982542933267, 1.2216514308596746, 1.0911838023212628, 0.9607161737828509, 1.8621288800482418, 1.5300294619504662, 2.633073957775221, 0.059303467517459935, 0.18977109605587178, 0.17791040255237978, 0.16604970904888783, 0.09488554802793589, 0.17791040255237978, 0.13046762853841185, 0.9369947867758669, 0.33209941809777566, 1.4232832204190382, 0.22535317656634773, 2.609352570768237, 0.6641988361955513, 0.28465664408380764, 0.16604970904888783, 0.14232832204190382, 0.21349248306285573, 0.9962982542933267, 1.2216514308596746, 1.0911838023212628, 0.9607161737828509, 1.8621288800482418, 1.5300294619504662, 2.633073957775221, 0.059303467517459935, 0.18977109605587178, 0.17791040255237978, 0.16604970904888783, 0.09488554802793589, 0.17791040255237978, 0.13046762853841185, 0.9369947867758669, 0.33209941809777566, 1.4232832204190382, 0.22535317656634773, 2.609352570768237, 0.6641988361955513, 0.28465664408380764, 0.16604970904888783, 0.14232832204190382, 0.21349248306285573, 0.9962982542933267, 1.2216514308596746, 1.0911838023212628, 0.9607161737828509, 1.8621288800482418, 1.5300294619504662, 2.633073957775221, 0.059303467517459935, 0.18977109605587178, 0.17791040255237978, 0.16604970904888783, 0.09488554802793589, 0.17791040255237978, 0.13046762853841185, 0.9369947867758669, 0.33209941809777566, 1.4232832204190382, 0.22535317656634773, 2.609352570768237, 0.6641988361955513, 0.28465664408380764, 0.16604970904888783, 0.14232832204190382, 0.21349248306285573, 0.9962982542933267, 1.2216514308596746, 1.0911838023212628, 0.9607161737828509, 1.8621288800482418, 1.5300294619504662, 2.633073957775221, 0.07116416102095191, 0.18977109605587178, 0.22535317656634773, 0.11860693503491987, 0.18977109605587178, 0.15418901554539582, 0.2609352570768237, 0.22535317656634773, 0.7116416102095191, 0.4625670466361875, 0.40326357911872757, 2.0400392826006217, 1.9925965085866535, 2.0163178955936374, 0.9132733997688829, 1.4707259944330062, 0.6760595296990431, 1.743521945013322, 1.4825866879364982, 1.8265467995377658, 0.8065271582374551, 1.5181687684469742, 1.4351439139225302, 2.7279595058031565, 0.07116416102095191, 0.18977109605587178, 0.22535317656634773, 0.11860693503491987, 0.18977109605587178, 0.15418901554539582, 0.2609352570768237, 0.22535317656634773, 0.7116416102095191, 0.4625670466361875, 0.40326357911872757, 2.0400392826006217, 1.9925965085866535, 2.0163178955936374, 0.9132733997688829, 1.4707259944330062, 0.6760595296990431, 1.743521945013322, 1.4825866879364982, 1.8265467995377658, 0.8065271582374551, 1.5181687684469742, 1.4351439139225302, 2.7279595058031565]}:
        print("The technical data profile of the background is not the correct one.")
        exit()

    # creation of the dishwasher
    if "dishwasher" not in world.catalog.devices:
        print("The device called dishwasher has not been created successfully or does not bear the correct name.")
        exit()

    # contract of the dishwasher
    if world.catalog.devices["dishwasher"].natures[LVE]["contract"].name != "elec_contract_egoist":
        print("The contract of the dishwasher is not the correct one.")
        exit()

    # agent of the dishwasher
    if world.catalog.devices["dishwasher"].agent.name != "consumer":
        print("The agent of the dishwasher is not the correct one.")
        exit()

    # aggregator of the dishwasher
    if world.catalog.devices["dishwasher"].natures[LVE]["aggregator"].name != "aggregator_elec":
        print("The aggregator of the dishwasher is not the correct one.")
        exit()

    # user profile of the dishwasher
    if world.catalog.devices["dishwasher"]._user_profile != [[8, 0.05059746340151786, 8], [9, 0.16172092156353587, 8], [10, 0.2728443797255539, 8], [11, 0.38396783788757194, 8], [12, 0.49509129604958996, 8], [13, 0.606214754211608, 8], [14, 0.7173382123736259, 8], [15, 0.828461670535644, 8], [16, 0.939585128697662, 8], [17, 1, 8]]:
        print("The user profile of the dishwasher is not the correct one.")
        exit()

    # technical data of the dishwasher
    if world.catalog.devices["dishwasher"]._technical_profile != [[{'LVE': 0.6275470822777184}, 1], [{'LVE': 0.277947487436564}, 1]]:
        print("The technical data profile of the dishwasher is not the correct one.")
        exit()

    # creation of the hot water tank
    if "hot_water_tank" not in world.catalog.devices:
        print("The device called hot_water_tank has not been created successfully or does not bear the correct name.")
        exit()

    # contract of the hot water tank
    if world.catalog.devices["hot_water_tank"].natures[LTH]["contract"].name != "heat_contract_cooperative":
        print("The contract of the hot_water_tank is not the correct one.")
        exit()

    # agent of the hot water tank
    if world.catalog.devices["hot_water_tank"].agent.name != "consumer":
        print("The agent of the hot_water_tank is not the correct one.")
        exit()

    # aggregator of the hot water tank
    if world.catalog.devices["hot_water_tank"].natures[LTH]["aggregator"].name != "aggregator_heat":
        print("The aggregator of the hot_water_tank is not the correct one.")
        exit()

    # user profile of the hot water tank
    if world.catalog.devices["hot_water_tank"]._user_profile != [[5, 0.25], [17, 0.25], [18, 0.5]]:
        print("The user profile of the hot_water_tank is not the correct one.")
        exit()

    # technical data of the hot water tank
    if world.catalog.devices["hot_water_tank"]._technical_profile != {'LTH': 6.156524543516123}:
        print("The technical data profile of the hot_water_tank is not the correct one.")
        exit()

    # creation of the heating
    if "heating" not in world.catalog.devices:
        print("The device called heating has not been created successfully or does not bear the correct name.")
        exit()

    # contract of the heating
    if world.catalog.devices["heating"].natures[LTH]["contract"].name != "heat_contract_cooperative":
        print("The contract of the heating is not the correct one.")
        exit()

    # agent of the heating
    if world.catalog.devices["heating"].agent.name != "consumer":
        print("The agent of the heating is not the correct one.")
        exit()

    # aggregator of the heating
    if world.catalog.devices["heating"].natures[LTH]["aggregator"].name != "aggregator_heat":
        print("The aggregator of the heating is not the correct one.")
        exit()

    # user profile of the heating
    if world.catalog.devices["heating"]._user_profile != [[8, {'LTH': 0.2153696107088212}, [19, 20, 21]], [9, {'LTH': 1}, [19, 20, 21]], [10, {'LTH': 1}, [19, 20, 21]], [11, {'LTH': 1}, [19, 20, 21]], [12, {'LTH': 1}, [19, 20, 21]], [13, {'LTH': 0.7846303892911788}, [19, 20, 21]], [13, {'LTH': 1.0}, [19, 20, 21]], [14, {'LTH': 1}, [15, 18, 21]], [15, {'LTH': 1}, [15, 18, 21]], [16, {'LTH': 1}, [15, 18, 21]], [17, {'LTH': 1}, [15, 18, 21]], [18, {'LTH': 1}, [15, 18, 21]], [19, {'LTH': 1}, [15, 18, 21]], [20, {'LTH': 1}, [15, 18, 21]], [21, {'LTH': 1}, [15, 18, 21]], [22, {'LTH': 0.7846303892911788}, [15, 18, 21]]]:
        print("The user profile of the heating is not the correct one.")
        exit()

    # technical data of the heating
    if world.catalog.devices["heating"]._G != 1.1628023779712067 and world.catalog.devices["heating"]._thermal_inertia != 18000:
        print("The technical data profile of the heating is not the correct one.")
        exit()

    # location of the heating
    if world.catalog.devices["heating"]._location != "Pau":
        print("The location of the heating is not the correct one.")
        exit()


def correction_9_automatic_generation():
    world = get_world()
    LVE = world.catalog.natures["LVE"]
    LTH = world.catalog.natures["LTH"]

    # number of agents
    if len(world.catalog.agents) != 503:
        print("The quantity of agents is not the correct one.")
        exit()

    # template of agent
    if "complete_profile_0" not in world.catalog.agents:
        print("The template of agent is not the correct one.")
        exit()

    # aggregator elec
    if world.catalog.devices["complete_profile_0_Background_0"].natures[LVE]["aggregator"].name != "aggregator_elec":
        print("The aggregator for electricity is not the correct one.")
        exit()

    # aggregator heat
    if world.catalog.devices["complete_profile_0_Heating_0"].natures[LTH]["aggregator"].name != "aggregator_heat":
        print("The aggregator for heat is not the correct one.")
        exit()

    # price manager of egoist elec contract
    if world.catalog.contracts["complete_profile_LVE_BAU"]._daemon_name != "elec_prices":
        print("The price manager of the contract for electricity is not the correct one.")
        exit()

    # price manager of egoist heat contract
    if world.catalog.contracts["complete_profile_LTH_BAU"]._daemon_name != "heat_prices":
        print("The price manager of the contract for heat is not the correct one.")
        exit()

    print("Congratulations, everything is working well.")


def correction_10_dataloggers():
    world = get_world()

    # creation of the datalogger for self-sufficiency
    if "self_sufficiency_frequency_1" not in world.catalog.dataloggers:
        print("The datalogger of the subclass SelfSufficiencyDatalogger has not been created successfully.")
        exit()

    # period of the datalogger for self-sufficiency
    if world.catalog.dataloggers["self_sufficiency_frequency_1"]._period != 1 and world.catalog.dataloggers["self_sufficiency_frequency_1"]._global != False:
        print("The period of the datalogger of the subclass SelfSufficiencyDatalogger is not the correct one.")
        exit()

    # creation of the datalogger for nature balances
    if "nature_balances_global" not in world.catalog.dataloggers:
        print("The datalogger of the subclass NatureBalancesDatalogger has not been created successfully.")
        exit()

    # period of the datalogger for nature balances
    if world.catalog.dataloggers["nature_balances_global"]._period != 1 and world.catalog.dataloggers["nature_balances_global"]._global != True:
        print("The period of the datalogger of the subclass NatureBalancesDatalogger is not the correct one.")
        exit()
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

    # creation of the datalogger called "consumer_datalogger_1"
    if "consumer_datalogger_1" not in world.catalog.dataloggers:
        print("The datalogger called consumer_datalogger_1 has not been created successfully or does not bear the correct name.")
        exit()

    # file of the datalogger called "consumer_datalogger_1"
    if world.catalog.dataloggers["consumer_datalogger_1"]._filename != "ConsumerData1":
        print("The file name of the datalogger called consumer_datalogger_1 is not the correct one.")
        exit()

    # period of the datalogger called "consumer_datalogger_1"
    if world.catalog.dataloggers["consumer_datalogger_1"]._period != 2 and world.catalog.dataloggers["consumer_datalogger_1"]._global != False:
        print("The period of the datalogger called consumer_datalogger_1 is not the correct one.")
        exit()

    # type of export of the datalogger called "consumer_datalogger_1"
    if world.catalog.dataloggers["consumer_datalogger_1"]._graph_options.formats != "csv":
        print("The type of export for the output of the datalogger called consumer_datalogger_1 is not the correct one.")
        exit()

    # key "simulation_time"
    if "simulation_time" not in world.catalog.dataloggers["consumer_datalogger_1"]._list:
        print("The key simulation_time has not been added successfully for the output of the datalogger called consumer_datalogger_1.")
        exit()
        
    # graph status of "simulation_time"
    if "simulation_time" not in world.catalog.dataloggers["consumer_datalogger_1"]._x_values:
        print("The key simulation_time is not the X axis for the output of the datalogger called consumer_datalogger_1.")
        exit()

    # key "consumer.LVE.energy_bought"
    if "consumer.LVE.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_1"]._list:
        print("The key consumer.LVE.energy_bought has not been added successfully for the output of the datalogger called consumer_datalogger_1.")
        exit()

    # graph status of "consumer.LVE.energy_bought"
    if "consumer.LVE.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_1"]._y_values:
        print("The key consumer.LVE.energy_bought is not a y series for the output of the datalogger called consumer_datalogger_1.")
        exit()

    # plot on the principal y-axis
    if world.catalog.dataloggers["consumer_datalogger_1"]._y_values["consumer.LVE.energy_bought"]["label"] != 1:
        print("The graph status for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_1.")
        exit()

    # graph style of "consumer.LVE.energy_bought"
    if world.catalog.dataloggers["consumer_datalogger_1"]._y_values["consumer.LVE.energy_bought"]["style"] != "lines":
        print("The graph style for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_1.")
        exit()

    #

    # creation of the datalogger called "consumer_datalogger_2"
    if "consumer_datalogger_2" not in world.catalog.dataloggers:
        print("The datalogger called consumer_datalogger_2 has not been created successfully or does not bear the correct name.")
        exit()

    # file of the datalogger called "consumer_datalogger_2"
    if world.catalog.dataloggers["consumer_datalogger_2"]._filename != "ConsumerData2":
        print("The file name of the datalogger called consumer_datalogger_2 is not the correct one.")
        exit()

    # period of the datalogger called "consumer_datalogger_2"
    if world.catalog.dataloggers["consumer_datalogger_2"]._period != 2 and world.catalog.dataloggers[
        "consumer_datalogger_2"]._global != False:
        print("The period of the datalogger called consumer_datalogger_2 is not the correct one.")
        exit()

    # type of export of the datalogger called "consumer_datalogger_2"
    exported_formats = []
    for fmt in world.catalog.dataloggers["consumer_datalogger_2"]._graph_options.formats:
        exported_formats.append(fmt)

    if exported_formats != ["csv", "LaTeX"]:
        print("The type of export for the output of the datalogger called consumer_datalogger_2 is not the correct one.")
        exit()

    # type of plots for the export of the datalogger called "consumer_datalogger_2"
    if world.catalog.dataloggers["consumer_datalogger_2"]._graph_options.graph_type != "single_series":
        print("The type of export for the output of the datalogger called consumer_datalogger_2 is not the correct one.")
        exit()

    # key "simulation_time"
    if "simulation_time" not in world.catalog.dataloggers["consumer_datalogger_2"]._list:
        print("The key simulation_time has not been added successfully for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # graph status of "simulation_time"
    if "simulation_time" not in world.catalog.dataloggers["consumer_datalogger_2"]._x_values:
        print("The key simulation_time is not the X axis for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # key "consumer.LVE.energy_bought"
    if "consumer.LVE.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_2"]._list:
        print("The key consumer.LVE.energy_bought has not been added successfully for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # graph status of "consumer.LVE.energy_bought"
    if "consumer.LVE.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_2"]._y_values:
        print("The key consumer.LVE.energy_bought is not a y series for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # plot on the principal y-axis
    if world.catalog.dataloggers["consumer_datalogger_2"]._y_values["consumer.LVE.energy_bought"]["label"] != 1:
        print("The graph status for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # graph style of "consumer.LVE.energy_bought"
    if world.catalog.dataloggers["consumer_datalogger_2"]._y_values["consumer.LVE.energy_bought"]["style"] != "lines":
        print("The graph style for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # key "consumer.LTH.energy_bought"
    if "consumer.LTH.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_2"]._list:
        print("The key consumer.LTH.energy_bought has not been added successfully for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # graph status of "consumer.LTH.energy_bought"
    if "consumer.LTH.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_2"]._y_values:
        print("The key consumer.LTH.energy_bought is not a y series for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # plot on the principal y-axis
    if world.catalog.dataloggers["consumer_datalogger_2"]._y_values["consumer.LTH.energy_bought"]["label"] != 1:
        print("The graph status for the key consumer.LTH.energy_bought is not correct for the output of the datalogger called consumer_datalogger_2.")
        exit()

    # graph style of "consumer.LTH.energy_bought"
    if world.catalog.dataloggers["consumer_datalogger_2"]._y_values["consumer.LTH.energy_bought"]["style"] != "lines":
        print("The graph style for the key consumer.LTH.energy_bought is not correct for the output of the datalogger called consumer_datalogger_2.")
        exit()

    #

    # creation of the datalogger called "consumer_datalogger_3"
    if "consumer_datalogger_3" not in world.catalog.dataloggers:
        print("The datalogger called consumer_datalogger_3 has not been created successfully or does not bear the correct name.")
        exit()

    # file of the datalogger called "consumer_datalogger_3"
    if world.catalog.dataloggers["consumer_datalogger_3"]._filename != "ConsumerData3":
        print("The file name of the datalogger called consumer_datalogger_3 is not the correct one.")
        exit()

    # period of the datalogger called "consumer_datalogger_3"
    if world.catalog.dataloggers["consumer_datalogger_3"]._period != 4 and world.catalog.dataloggers[
        "consumer_datalogger_3"]._global != False:
        print("The period of the datalogger called consumer_datalogger_3 is not the correct one.")
        exit()

    # type of export of the datalogger called "consumer_datalogger_3"
    exported_formats = []
    for fmt in world.catalog.dataloggers["consumer_datalogger_3"]._graph_options.formats:
        exported_formats.append(fmt)

    export_format_ok = 0
    for fmt in exported_formats:
        if fmt == "csv":
            export_format_ok += 1
        elif fmt == "LaTeX":
            export_format_ok += 1

    if export_format_ok != 2:
        print("The type of export for the output of the datalogger called consumer_datalogger_3 is not the correct one.")
        exit()

    # type of plots for the export of the datalogger called "consumer_datalogger_3"
    if world.catalog.dataloggers["consumer_datalogger_3"]._graph_options.graph_type != "multiple_series":
        print("The type of export for the output of the datalogger called consumer_datalogger_3 is not the correct one.")
        exit()

    # legends used for the x- and y-axis
    if world.catalog.dataloggers["consumer_datalogger_3"]._graph_labels["xlabel"] != "X-axis":
        print("The legend of the x axis for the export for the output of the datalogger called consumer_datalogger_3 is not the correct one.")
        exit()

    if world.catalog.dataloggers["consumer_datalogger_3"]._graph_labels["ylabel"] != "Y-axis":
        print("The legend of the y axis for the export for the output of the datalogger called consumer_datalogger_3 is not the correct one.")
        exit()

    # key "simulation_time"
    if "simulation_time" not in world.catalog.dataloggers["consumer_datalogger_3"]._list:
        print("The key simulation_time has not been added successfully for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # graph status of "simulation_time"
    if "simulation_time" not in world.catalog.dataloggers["consumer_datalogger_3"]._x_values:
        print("The key simulation_time is not the X axis for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # key "consumer.LVE.energy_bought"
    if "consumer.LVE.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_3"]._list:
        print("The key consumer.LVE.energy_bought has not been added successfully for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # graph status of "consumer.LVE.energy_bought"
    if "consumer.LVE.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_3"]._y_values:
        print("The key consumer.LVE.energy_bought is not a y series for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # plot on the principal y-axis
    if world.catalog.dataloggers["consumer_datalogger_3"]._y_values["consumer.LVE.energy_bought"]["label"] != 1:
        print("The graph status for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # legend of "consumer.LVE.energy_bought"
    tmp = r"$\alpha$"
    if world.catalog.dataloggers["consumer_datalogger_3"]._y_values["consumer.LVE.energy_bought"]["legend"] != tmp:
        print("The legend for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # graph style of "consumer.LVE.energy_bought"
    if world.catalog.dataloggers["consumer_datalogger_3"]._y_values["consumer.LVE.energy_bought"]["style"] != "lines":
        print("The graph style for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # key "consumer.LTH.energy_bought"
    if "consumer.LTH.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_3"]._list:
        print("The key consumer.LTH.energy_bought has not been added successfully for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # graph status of "consumer.LTH.energy_bought"
    if "consumer.LTH.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_3"]._y_values:
        print("The key consumer.LTH.energy_bought is not a y series for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # plot on the principal y-axis
    if world.catalog.dataloggers["consumer_datalogger_3"]._y_values["consumer.LTH.energy_bought"]["label"] != 1:
        print("The graph status for the key consumer.LTH.energy_bought is not correct for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # legend of "consumer.LTH.energy_bought"
    tmp = r"$\beta$"
    if world.catalog.dataloggers["consumer_datalogger_3"]._y_values["consumer.LTH.energy_bought"]["legend"] != tmp:
        print("The legend for the key consumer.LTH.energy_bought is not correct for the output of the datalogger called consumer_datalogger_3.")
        exit()

    # graph style of "consumer.LTH.energy_bought"
    if world.catalog.dataloggers["consumer_datalogger_3"]._y_values["consumer.LTH.energy_bought"]["style"] != "points":
        print("The graph style for the key consumer.LTH.energy_bought is not correct for the output of the datalogger called consumer_datalogger_3.")
        exit()

    #

    # creation of the datalogger called "consumer_datalogger_4"
    if "consumer_datalogger_4" not in world.catalog.dataloggers:
        print("The datalogger called consumer_datalogger_4 has not been created successfully or does not bear the correct name.")
        exit()

    # file of the datalogger called "consumer_datalogger_4"
    if world.catalog.dataloggers["consumer_datalogger_4"]._filename != "ConsumerData4":
        print("The file name of the datalogger called consumer_datalogger_4 is not the correct one.")
        exit()

    # period of the datalogger called "consumer_datalogger_4"
    if world.catalog.dataloggers["consumer_datalogger_4"]._period != 4 and world.catalog.dataloggers["consumer_datalogger_4"]._global != False:
        print("The period of the datalogger called consumer_datalogger_4 is not the correct one.")
        exit()

    # type of export of the datalogger called "consumer_datalogger_4"
    exported_formats = []
    for fmt in world.catalog.dataloggers["consumer_datalogger_4"]._graph_options.formats:
        exported_formats.append(fmt)

    export_format_ok = 0
    for fmt in exported_formats:
        if fmt == "csv":
            export_format_ok += 1
        elif fmt == "matplotlib":
            export_format_ok += 1
        elif fmt == "LaTeX":
            export_format_ok += 1

    if export_format_ok != 3:
        print("The type of export for the output of the datalogger called consumer_datalogger_4 is not the correct one.")
        exit()

    # type of plots for the export of the datalogger called "consumer_datalogger_4"
    if world.catalog.dataloggers["consumer_datalogger_4"]._graph_options.graph_type != "multiple_series":
        print("The type of export for the output of the datalogger called consumer_datalogger_4 is not the correct one.")
        exit()

    # legends used for the x- and y-axis
    if world.catalog.dataloggers["consumer_datalogger_4"]._graph_labels["xlabel"] != "$t \, [\si{\hour}]$":
        print("The legend of the x axis for the export for the output of the datalogger called consumer_datalogger_4 is not the correct one.")
        exit()

    if world.catalog.dataloggers["consumer_datalogger_4"]._graph_labels["ylabel"] != "$\mathcal{P}_{ref.} \, [\si{\watt}]$":
        print("The legend of the y axis for the export for the output of the datalogger called consumer_datalogger_4 is not the correct one.")
        exit()

    # key "simulation_time"
    if "simulation_time" not in world.catalog.dataloggers["consumer_datalogger_4"]._list:
        print("The key simulation_time has not been added successfully for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # graph status of "simulation_time"
    if "simulation_time" not in world.catalog.dataloggers["consumer_datalogger_4"]._x_values:
        print("The key simulation_time is not the X axis for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # key "consumer.LVE.energy_bought"
    if "consumer.LVE.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_4"]._list:
        print("The key consumer.LVE.energy_bought has not been added successfully for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # graph status of "consumer.LVE.energy_bought"
    if "consumer.LVE.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_4"]._y_values:
        print("The key consumer.LVE.energy_bought is not a y series for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # plot on the principal y-axis
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.LVE.energy_bought"]["label"] != 1:
        print("The graph status for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # legend of "consumer.LVE.energy_bought"
    tmp = r"$P_1$"
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.LVE.energy_bought"]["legend"] != tmp:
        print("The legend for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # graph style of "consumer.LVE.energy_bought"
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.LVE.energy_bought"]["style"] != "lines":
        print("The graph style for the key consumer.LVE.energy_bought is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # key "consumer.LTH.energy_bought"
    if "consumer.LTH.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_4"]._list:
        print("The key consumer.LTH.energy_bought has not been added successfully for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # graph status of "consumer.LTH.energy_bought"
    if "consumer.LTH.energy_bought" not in world.catalog.dataloggers["consumer_datalogger_4"]._y_values:
        print("The key consumer.LTH.energy_bought is not a y series for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # plot on the principal y-axis
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.LTH.energy_bought"]["label"] != 1:
        print("The graph status for the key consumer.LTH.energy_bought is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # legend of "consumer.LTH.energy_bought"
    tmp = r"$P_2$"
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.LTH.energy_bought"]["legend"] != tmp:
        print("The legend for the key consumer.LTH.energy_bought is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # graph style of "consumer.LTH.energy_bought"
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.LTH.energy_bought"]["style"] != "lines":
        print("The graph style for the key consumer.LTH.energy_bought is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # key "consumer.money_spent"
    if "consumer.money_spent" not in world.catalog.dataloggers["consumer_datalogger_4"]._list:
        print("The key consumer.money_spent has not been added successfully for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # graph status of "consumer.money_spent"
    if "consumer.money_spent" not in world.catalog.dataloggers["consumer_datalogger_4"]._y_values:
        print("The key consumer.money_spent is not a y series for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # plot on a secondary y-axis
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.money_spent"]["label"] != 2:
        print("The graph status for the key consumer.money_spent is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # legend of "consumer.money_spent"
    tmp = r"$\mathcal{C}$"
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.money_spent"]["legend"] != tmp:
        print("The legend for the key consumer.money_spent is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    # graph style of "consumer.money_spent"
    if world.catalog.dataloggers["consumer_datalogger_4"]._y_values["consumer.money_spent"]["style"] != "points":
        print("The graph style for the key consumer.money_spent is not correct for the output of the datalogger called consumer_datalogger_4.")
        exit()

    print("Congratulations, everything is working well.")
