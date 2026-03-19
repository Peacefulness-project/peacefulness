from random import seed
import numpy as np
import itertools


# ######################################################################################################################
# strategies, defined as an ordered list of the available levers
# ######################################################################################################################

consumption_options_1 = ["flexible_chargers", "sellHP", "sellGrid", "nothing"]
consumption_options_2 = ["storage", "nothing"]
production_options_1 = ["buyCHP", "buyGrid", "nothing"]
production_options_2 = ["buyCHP", "buyHP", "buyW2H", "unstorage", "nothing"]
assessed_priorities_consumption_1 = [list(toto) for toto in itertools.permutations(consumption_options_1)]
assessed_priorities_consumption_2 = [list(toto) for toto in itertools.permutations(consumption_options_2)]
assessed_priorities_production_1 = [list(toto) for toto in itertools.permutations(production_options_1)]
assessed_priorities_production_2 = [list(toto) for toto in itertools.permutations(production_options_2)]
assessed_priorities_1 = {"consumption": assessed_priorities_consumption_1, "production": assessed_priorities_production_1}
assessed_priorities_2 = {"consumption": assessed_priorities_consumption_2, "production": assessed_priorities_production_2}


# reference strategies
def ref_priorities_consumption_1(strategy: "Strategy"):
    rigid_consumption = strategy._catalog.get("rigid_electricity_consumption.LVE.energy_wanted")["energy_maximum"]
    flexible_consumption = strategy._catalog.get("flexible_loads.LVE.energy_wanted")["energy_maximum"]
    pv_production = strategy._catalog.get("PV_field_1.LVE.energy_wanted")["energy_maximum"]
    pv_production += strategy._catalog.get("PV_field_2.LVE.energy_wanted")["energy_maximum"]
    wt_production = strategy._catalog.get("WT_field_1.LVE.energy_wanted")["energy_maximum"]
    wt_production += strategy._catalog.get("WT_field_2.LVE.energy_wanted")["energy_maximum"]

    if rigid_consumption + flexible_consumption < abs(pv_production + wt_production):
        return ["flexible_chargers", "sellHP", "sellGrid", "nothing"]
    elif rigid_consumption <= abs(pv_production + wt_production) <= rigid_consumption + flexible_consumption:
        return ["flexible_chargers", "nothing", "sellHP", "sellGrid"]
    else:
        return ["nothing", "flexible_chargers", "sellHP", "sellGrid"]


def ref_priorities_consumption_2(strategy: "Strategy"):
    heat_consumption = strategy._catalog.get("space_heating.LTH.energy_wanted")["energy_maximum"]
    heat_production = strategy._catalog.get("Waste_to_heat.LTH.energy_wanted")["energy_maximum"]
    heat_production += strategy._catalog.get("combined_heat_power.LTH.energy_wanted")["energy_maximum"]
    heat_production += strategy._catalog.get("heat_pump.LTH.energy_wanted")["energy_maximum"]

    if heat_consumption < abs(heat_production):
        return ["storage", "nothing"]
    else:
        return ["nothing", "storage"]


def ref_priorities_production_1(strategy: "Strategy"):
    rigid_consumption = strategy._catalog.get("rigid_electricity_consumption.LVE.energy_wanted")["energy_maximum"]
    flexible_consumption = strategy._catalog.get("flexible_loads.LVE.energy_wanted")["energy_maximum"]
    pv_production = strategy._catalog.get("PV_field_1.LVE.energy_wanted")["energy_maximum"]
    pv_production += strategy._catalog.get("PV_field_2.LVE.energy_wanted")["energy_maximum"]
    wt_production = strategy._catalog.get("WT_field_1.LVE.energy_wanted")["energy_maximum"]
    wt_production += strategy._catalog.get("WT_field_2.LVE.energy_wanted")["energy_maximum"]

    if rigid_consumption + flexible_consumption < abs(pv_production + wt_production):
        return ["nothing", "buyCHP", "buyGrid"]
    elif rigid_consumption <= abs(pv_production + wt_production) <= rigid_consumption + flexible_consumption:
        return ["buyCHP", "nothing", "buyGrid"]
    else:
        return ["buyCHP", "buyGrid", "nothing"]


def ref_priorities_production_2(strategy: "Strategy"):
    heat_consumption = strategy._catalog.get("space_heating.LTH.energy_wanted")["energy_maximum"]

    if heat_consumption > 0:
        return ["buyW2H", "buyCHP", "buyHP", "unstorage", "nothing"]
    else:
        return ["nothing", "buyCHP", "buyHP", "buyW2H", "unstorage"]
