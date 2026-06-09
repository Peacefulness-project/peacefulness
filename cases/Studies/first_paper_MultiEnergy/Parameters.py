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
    chp_gas_energy_wanted = strategy._catalog.get("combined_heat_power.LPG.energy_wanted")
    chp_elec_energy_wanted = strategy._catalog.get("combined_heat_power.LVE.energy_wanted")
    if len(strategy._catalog.get("electric_microgrid.LVE.energy_wanted")) > 0:
        mainGrid_elec_price = strategy._catalog.get("electric_microgrid.LVE.energy_wanted")[0]['price']
    else:
        mainGrid_elec_price = 0.0
    rigid_elec_consumption = strategy._catalog.get("rigid_electricity_consumption.LVE.energy_wanted")["energy_maximum"]
    rigid_heat_consumption = strategy._catalog.get("space_heating.LTH.energy_wanted")["energy_maximum"]
    pv_production = strategy._catalog.get("PV_field.LVE.energy_wanted")["energy_maximum"]
    wt_production = strategy._catalog.get("WT_field_1.LVE.energy_wanted")["energy_maximum"]
    wt_production += strategy._catalog.get("WT_field_2.LVE.energy_wanted")["energy_maximum"]
    w2h_production = strategy._catalog.get("Waste_to_heat.LTH.energy_wanted")["energy_maximum"]
    tes_storage = strategy._catalog.get("Heat_storage.LTH.energy_wanted")["energy_maximum"]

    if f"low_gas_price" in strategy._catalog.keys:
        strategy._catalog.set(f"low_gas_price", chp_gas_energy_wanted["price"] / chp_elec_energy_wanted["efficiency"] < mainGrid_elec_price)
    else:
        strategy._catalog.add(f"low_gas_price", chp_gas_energy_wanted["price"] / chp_elec_energy_wanted["efficiency"] < mainGrid_elec_price)
    if f"EnR_excess" in strategy._catalog.keys:
        strategy._catalog.set(f"EnR_excess", abs(pv_production + wt_production) >= rigid_elec_consumption)
    else:
        strategy._catalog.add(f"EnR_excess", abs(pv_production + wt_production) >= rigid_elec_consumption)
    if f"w2h_excess" in strategy._catalog.keys:
        strategy._catalog.set(f"w2h_excess", abs(w2h_production) >= rigid_heat_consumption)
    else:
        strategy._catalog.add(f"w2h_excess", abs(w2h_production) >= rigid_heat_consumption)
    if f"TES_full" in strategy._catalog.keys:
        strategy._catalog.set(f"TES_full", abs(tes_storage) <= 10)
    else:
        strategy._catalog.add(f"TES_full", abs(tes_storage) <= 10)

    if abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) < rigid_heat_consumption and chp_gas_energy_wanted["price"] / chp_elec_energy_wanted["efficiency"] >= mainGrid_elec_price:
        consumer_option = ["sellHP", "nothing", "flexible_chargers", "sellGrid"]
        if f"EMG_consumptions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_consumptions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_consumptions_priorities", consumer_option)
        return consumer_option
    elif abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) >= rigid_heat_consumption and chp_gas_energy_wanted["price"] / chp_elec_energy_wanted["efficiency"] >= mainGrid_elec_price:
        consumer_option = ["nothing", "sellHP", "flexible_chargers", "sellGrid"]
        if f"EMG_consumptions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_consumptions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_consumptions_priorities", consumer_option)
        return consumer_option
    elif (abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) >= rigid_heat_consumption and abs(tes_storage) > 10) or (abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) < rigid_heat_consumption):
        consumer_option = ["sellHP", "flexible_chargers", "sellGrid", "nothing"]
        if f"EMG_consumptions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_consumptions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_consumptions_priorities", consumer_option)
        return consumer_option
    elif (abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) >= rigid_heat_consumption and abs(tes_storage) <= 10) or (abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) >= rigid_heat_consumption and chp_gas_energy_wanted["price"] / chp_elec_energy_wanted["efficiency"] < mainGrid_elec_price):
        consumer_option = ["flexible_chargers", "sellGrid", "nothing", "sellHP"]
        if f"EMG_consumptions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_consumptions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_consumptions_priorities", consumer_option)
        return consumer_option
    elif chp_gas_energy_wanted["price"] / chp_elec_energy_wanted["efficiency"] < mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) < rigid_heat_consumption:
        consumer_option = ["flexible_chargers", "sellHP", "sellGrid", "nothing"]
        if f"EMG_consumptions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_consumptions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_consumptions_priorities", consumer_option)
        return consumer_option
    else:
        raise Exception("EMG consumption priorities error !")


def ref_priorities_consumption_2(strategy: "Strategy"):
    heat_consumption = strategy._catalog.get("space_heating.LTH.energy_wanted")["energy_maximum"]
    w2h_heat_production = strategy._catalog.get("Waste_to_heat.LTH.energy_wanted")["energy_maximum"]
    # chp_heat_production = strategy._catalog.get("combined_heat_power.LTH.energy_wanted")["energy_maximum"]
    # hp_heat_production = strategy._catalog.get("heat_pump.LTH.energy_wanted")["energy_maximum"]
    rigid_elec_consumption = strategy._catalog.get("rigid_electricity_consumption.LVE.energy_wanted")["energy_maximum"]
    pv_production = strategy._catalog.get("PV_field.LVE.energy_wanted")["energy_maximum"]
    wt_production = strategy._catalog.get("WT_field_1.LVE.energy_wanted")["energy_maximum"]
    wt_production += strategy._catalog.get("WT_field_2.LVE.energy_wanted")["energy_maximum"]
    tes_storage = strategy._catalog.get("Heat_storage.LTH.energy_wanted")["energy_maximum"]
    chp_elec_efficiency = strategy._catalog.get("combined_heat_power.LVE.energy_wanted")["efficiency"]
    chp_gas_price = strategy._catalog.get("combined_heat_power.LPG.energy_wanted")["price"] / chp_elec_efficiency
    if len(strategy._catalog.get("electric_microgrid.LVE.energy_wanted")) > 0:
        mainGrid_elec_price = strategy._catalog.get("electric_microgrid.LVE.energy_wanted")[0]['price']
    else:
        mainGrid_elec_price = 0.0

    if f"low_gas_price" in strategy._catalog.keys:
        strategy._catalog.set(f"low_gas_price", chp_gas_price < mainGrid_elec_price)
    else:
        strategy._catalog.add(f"low_gas_price", chp_gas_price < mainGrid_elec_price)
    if f"EnR_excess" in strategy._catalog.keys:
        strategy._catalog.set(f"EnR_excess", abs(pv_production + wt_production) >= rigid_elec_consumption)
    else:
        strategy._catalog.add(f"EnR_excess", abs(pv_production + wt_production) >= rigid_elec_consumption)
    if f"w2h_excess" in strategy._catalog.keys:
        strategy._catalog.set(f"w2h_excess", abs(w2h_heat_production) >= heat_consumption)
    else:
        strategy._catalog.add(f"w2h_excess", abs(w2h_heat_production) >= heat_consumption)
    if f"TES_full" in strategy._catalog.keys:
        strategy._catalog.set(f"TES_full", abs(tes_storage) <= 10)
    else:
        strategy._catalog.add(f"TES_full", abs(tes_storage) <= 10)

    if (chp_gas_price >= mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_heat_production) < heat_consumption) or abs(tes_storage) <= 10:
        consumer_option = ["nothing", "storage"]
        if f"DHN_consumptions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_consumptions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_consumptions_priorities", consumer_option)
        return consumer_option
    else:
        consumer_option = ["storage", "nothing"]
        if f"DHN_consumptions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_consumptions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_consumptions_priorities", consumer_option)
        return consumer_option


def ref_priorities_production_1(strategy: "Strategy"):
    rigid_elec_consumption = strategy._catalog.get("rigid_electricity_consumption.LVE.energy_wanted")["energy_maximum"]
    rigid_elec_consumption += strategy._catalog.get("flexible_loads.LVE.energy_wanted")["energy_minimum"]  # added the flexible loads when they become rigid
    pv_production = strategy._catalog.get("PV_field.LVE.energy_wanted")["energy_maximum"]
    wt_production = strategy._catalog.get("WT_field_1.LVE.energy_wanted")["energy_maximum"]
    wt_production += strategy._catalog.get("WT_field_2.LVE.energy_wanted")["energy_maximum"]
    rigid_heat_consumption = strategy._catalog.get("space_heating.LTH.energy_wanted")["energy_maximum"]
    w2h_production = strategy._catalog.get("Waste_to_heat.LTH.energy_wanted")["energy_maximum"]
    tes_storage = strategy._catalog.get("Heat_storage.LTH.energy_wanted")["energy_maximum"]
    chp_elec_efficiency = strategy._catalog.get("combined_heat_power.LVE.energy_wanted")["efficiency"]
    chp_gas_price = strategy._catalog.get("combined_heat_power.LPG.energy_wanted")["price"] / chp_elec_efficiency
    if len(strategy._catalog.get("electric_microgrid.LVE.energy_wanted")) > 0:
        mainGrid_elec_price = strategy._catalog.get("electric_microgrid.LVE.energy_wanted")[0]['price']
    else:
        mainGrid_elec_price = 0.0

    if f"low_gas_price" in strategy._catalog.keys:
        strategy._catalog.set(f"low_gas_price", chp_gas_price < mainGrid_elec_price)
    else:
        strategy._catalog.add(f"low_gas_price", chp_gas_price < mainGrid_elec_price)
    if f"EnR_excess" in strategy._catalog.keys:
        strategy._catalog.set(f"EnR_excess", abs(pv_production + wt_production) >= rigid_elec_consumption)
    else:
        strategy._catalog.add(f"EnR_excess", abs(pv_production + wt_production) >= rigid_elec_consumption)
    if f"w2h_excess" in strategy._catalog.keys:
        strategy._catalog.set(f"w2h_excess", abs(w2h_production) >= rigid_heat_consumption)
    else:
        strategy._catalog.add(f"w2h_excess", abs(w2h_production) >= rigid_heat_consumption)
    if f"TES_full" in strategy._catalog.keys:
        strategy._catalog.set(f"TES_full", abs(tes_storage) <= 10)
    else:
        strategy._catalog.add(f"TES_full", abs(tes_storage) <= 10)

    if chp_gas_price >= mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption:
        consumer_option = ["buyGrid", "buyCHP", "nothing"]
        if f"EMG_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_productions_priorities", consumer_option)
        return consumer_option
    elif (chp_gas_price >= mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) >= rigid_heat_consumption) or (chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) >= rigid_heat_consumption and abs(tes_storage) <= 10):
        consumer_option = ["nothing", "buyCHP", "buyGrid"]
        if f"EMG_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_productions_priorities", consumer_option)
        return consumer_option
    elif (chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) >= rigid_heat_consumption and abs(tes_storage) > 10) or (chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) < rigid_heat_consumption and abs(tes_storage) <= 10):
        consumer_option = ["buyCHP", "nothing", "buyGrid"]
        if f"EMG_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_productions_priorities", consumer_option)
        return consumer_option
    elif (chp_gas_price >= mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) < rigid_heat_consumption) or (chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption) or (chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) < rigid_heat_consumption and abs(tes_storage) > 10):
        consumer_option = ["buyCHP", "buyGrid", "nothing"]
        if f"EMG_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"EMG_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"EMG_productions_priorities", consumer_option)
        return consumer_option
    else:
        raise Exception("EMG production priorities error !")


def ref_priorities_production_2(strategy: "Strategy"):
    heat_consumption = strategy._catalog.get("space_heating.LTH.energy_wanted")["energy_maximum"]
    w2h_production = strategy._catalog.get("Waste_to_heat.LTH.energy_wanted")["energy_maximum"]
    rigid_elec_consumption = strategy._catalog.get("rigid_electricity_consumption.LVE.energy_wanted")["energy_maximum"]
    # hp_heat_production = strategy._catalog.get("heat_pump.LTH.energy_wanted")["energy_maximum"]
    pv_production = strategy._catalog.get("PV_field.LVE.energy_wanted")["energy_maximum"]
    wt_production = strategy._catalog.get("WT_field_1.LVE.energy_wanted")["energy_maximum"]
    wt_production += strategy._catalog.get("WT_field_2.LVE.energy_wanted")["energy_maximum"]
    tes_storage = strategy._catalog.get("Heat_storage.LTH.energy_wanted")["energy_maximum"]
    chp_elec_efficiency = strategy._catalog.get("combined_heat_power.LVE.energy_wanted")["efficiency"]
    chp_gas_price = strategy._catalog.get("combined_heat_power.LPG.energy_wanted")["price"] / chp_elec_efficiency
    if len(strategy._catalog.get("electric_microgrid.LVE.energy_wanted")) > 0:
        mainGrid_elec_price = strategy._catalog.get("electric_microgrid.LVE.energy_wanted")[0]['price']
    else:
        mainGrid_elec_price = 0.0

    if f"low_gas_price" in strategy._catalog.keys:
        strategy._catalog.set(f"low_gas_price", chp_gas_price < mainGrid_elec_price)
    else:
        strategy._catalog.add(f"low_gas_price", chp_gas_price < mainGrid_elec_price)
    if f"EnR_excess" in strategy._catalog.keys:
        strategy._catalog.set(f"EnR_excess", abs(pv_production + wt_production) >= rigid_elec_consumption)
    else:
        strategy._catalog.add(f"EnR_excess", abs(pv_production + wt_production) >= rigid_elec_consumption)
    if f"w2h_excess" in strategy._catalog.keys:
        strategy._catalog.set(f"w2h_excess", abs(w2h_production) >= heat_consumption)
    else:
        strategy._catalog.add(f"w2h_excess", abs(w2h_production) >= heat_consumption)
    if f"TES_full" in strategy._catalog.keys:
        strategy._catalog.set(f"TES_full", abs(tes_storage) <= 10)
    else:
        strategy._catalog.add(f"TES_full", abs(tes_storage) <= 10)

    if chp_gas_price >= mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) < heat_consumption:
        consumer_option = ["buyW2H", "unstorage", "buyHP", "buyCHP", "nothing"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    elif (abs(w2h_production) >= heat_consumption and abs(tes_storage) <= 10) or (chp_gas_price >= mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) >= heat_consumption and abs(tes_storage) > 10):
        consumer_option = ["buyW2H", "nothing", "unstorage", "buyHP", "buyCHP"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    elif chp_gas_price >= mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) >= heat_consumption and abs(tes_storage) > 10:
        consumer_option = ["buyW2H", "buyHP", "nothing", "buyCHP", "unstorage"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    elif chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) >= heat_consumption and abs(tes_storage) > 10:
        consumer_option = ["buyW2H", "buyHP", "buyCHP", "nothing", "unstorage"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    elif chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) < heat_consumption:
        consumer_option = ["buyW2H", "buyHP", "buyCHP", "unstorage", "nothing"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    elif chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) < heat_consumption and abs(tes_storage) <= 10:
        consumer_option = ["buyW2H", "buyCHP", "unstorage", "buyHP", "nothing"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    elif chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) >= heat_consumption and abs(tes_storage) > 10:
        consumer_option = ["buyW2H", "buyCHP", "nothing", "unstorage", "buyHP"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    elif chp_gas_price < mainGrid_elec_price and abs(pv_production + wt_production) < rigid_elec_consumption and abs(w2h_production) < heat_consumption and abs(tes_storage) > 10:
        consumer_option = ["buyW2H", "buyCHP", "buyHP", "unstorage", "nothing"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    elif chp_gas_price >= mainGrid_elec_price and abs(pv_production + wt_production) >= rigid_elec_consumption and abs(w2h_production) < heat_consumption:
        consumer_option = ["buyW2H", "buyHP", "unstorage", "buyCHP", "nothing"]
        if f"DHN_productions_priorities" in strategy._catalog.keys:
            strategy._catalog.set(f"DHN_productions_priorities", consumer_option)
        else:
            strategy._catalog.add(f"DHN_productions_priorities", consumer_option)
        return consumer_option
    else:
        raise Exception("DHN production priorities error !")
