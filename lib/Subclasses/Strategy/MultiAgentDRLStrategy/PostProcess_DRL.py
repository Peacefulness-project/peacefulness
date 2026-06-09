# In this file, a post-process script is executed to do the Excel manipulation to get final results.
# Additionally, it will output also figures, and a text file recapitulating the results.
# Worth noting, is the fact that it is case specific, however many functions can be re-used for different case studies.

# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import re
from lib.Subclasses.Strategy.SingleAgentDRLStrategy.Utilities import who_decided
from scipy.fft import fft, fftfreq


# I - We read the data from PEACEFULNESS '.csv' outputs into dicts #
####################################################################
path_to_csv = "D:/dossier_y23hallo/Thèse/multi-energy/final_results/single_agent/2_dol"  # path to inference results folder

# 1. energy flow values for the devices of the case study
devices_file = "DeviceQuantity_frequency_1"
df = pd.read_csv(path_to_csv + "/" + devices_file + ".csv", sep="\t")
df = df.iloc[:,:-1]  # removing the last column (NaN)
df = df.iloc[:-1]  # removing the last row (due to 2nd reset call ; necessary for export)
devices_data = df.to_dict(orient='list')  # transforming it into dicts.

# 2. energy balance of the aggregators
aggregators_file = "AggregatorsBalances_frequency_1"
df = pd.read_csv(path_to_csv + "/" + aggregators_file + ".csv", sep="\t")
df = df.iloc[:,:-1]  # removing the last column (NaN)
df = df.iloc[:-1]  # removing the last row (due to 2nd reset call ; necessary for export)
aggregators_data = df.to_dict(orient='list')  # transforming it into dicts.

# 3. results/metrics of the case study
metrics_file = "Metrics"
df = pd.read_csv(path_to_csv + "/" + metrics_file + ".csv", sep="\t")
df = df.iloc[:,:-1]  # removing the last column (NaN)
df = df.iloc[:-1]  # removing the last row (due to 2nd reset call ; necessary for export)
metrics_data = df.to_dict(orient='list')  # transforming it into dicts.

# 4. SoC of the TES from the logs
logs_file = "logs"
df = pd.read_csv(path_to_csv + "/" + logs_file + ".csv", sep="\t")
df = df.iloc[:,:-1]  # removing the last column (NaN)
df = df.iloc[:-1]  # removing the last row (due to 2nd reset call ; necessary for export)
logs_data = df.to_dict(orient='list')  # transforming it into dicts.


# 5. the decisions of the RL agents
decisions_file = "Inference_RL_decisions"
df = pd.read_csv(path_to_csv + "/" + decisions_file + ".csv", sep=",")
df_1 = df.iloc[:5304]  # electric microgrid (agent 1)
df_2 = df.iloc[5304:]  # district heating network (agent 2)
df_1 = df_1.drop("Energy_Storage", axis=1)  # the EMG doesn't dispose of energy storage systems
df_1.columns = ['aggregator', 'Energy_Consumption', 'Energy_Production', 'mainGrid', 'heat_pump', 'combined_heat_power']  # renaming columns for clarity
df_2 = df_2.drop("Energy_Conversion_3", axis=1)  # the DHN doesn't exchange heat directly with the superior aggregator
df_2.columns = ['aggregator', 'Energy_Consumption', 'Energy_Production', 'Energy_Storage', 'heat_pump', 'combined_heat_power']  # renaming columns for clarity
agent1_decisions = df_1.to_dict(orient="list")  # transforming it into dicts.
agent2_decisions = df_2.to_dict(orient="list")  # transforming it into dicts.

# 6. energy intervals corresponding to each decision
intervals_file = "Inference_energy_intervals"
df = pd.read_csv(path_to_csv + "/" + intervals_file + ".csv", sep=",")
df_1 = df.iloc[:5304]  # electric microgrid (agent 1)
df_2 = df.iloc[5304:]  # district heating network (agent 2)
df_1 = df_1.reset_index()
df_1 = df_1.drop("level_5", axis=1)
df_1 = df_1.drop("aggregator", axis=1)
df_1.columns = ['aggregator', 'C_min', 'C_max', 'P_min', 'P_max', 'Exch_min', 'Exch_max', 'HP_min', 'HP_max', 'CHP_min', 'CHP_max']
agent1_intervals = df_1.to_dict(orient="list")  # transforming it into dicts.
df_2 = df_2.reset_index()
df_2 = df_2.iloc[:,:-2]
df_2.columns = ['aggregator', 'C_min', 'C_max', 'P_min', 'P_max', 'S_min', 'S_max', 'HP_min', 'HP_max', 'CHP_min', 'CHP_max']
df_2["HP_min"] = 0.0  # correcting the values for the HP
df_2["HP_max"] = -6910.331633  # correcting the values for the HP
agent2_intervals = df_2.to_dict(orient="list")  # transforming it into dicts.


# II - Processing the results #
###############################
# 1. Electric Microgrid (agent 1) - energy balance.
total_elec_load = (np.array(devices_data['rigid_electricity_consumption.LVE.energy']) +
                   np.array(devices_data['flexible_loads.LVE.energy']) +
                   np.array(devices_data['heat_pump.LVE.energy']))
total_elec_supply = (- np.array(devices_data['PV_field_1.LVE.energy']) -
                     np.array(devices_data['PV_field_2.LVE.energy']) -
                     np.array(devices_data['WT_field_1.LVE.energy']) -
                     np.array(devices_data['WT_field_2.LVE.energy']) -
                     np.array(devices_data['combined_heat_power.LVE.energy']))
elec_imbalance = total_elec_load - total_elec_supply
buy_need = np.where(elec_imbalance >= 0, elec_imbalance, 0)
sell_need = np.where(elec_imbalance < 0, - elec_imbalance, 0)
elec_balance = (np.array(aggregators_data['electric_microgrid.energy_sold_inside']) +
                np.array(aggregators_data['electric_microgrid.energy_sold_outside']) -
                np.array(aggregators_data['electric_microgrid.energy_bought_inside']) -
                np.array(aggregators_data['electric_microgrid.energy_bought_outside']))
diff_buy = np.array(aggregators_data['electric_microgrid.energy_bought_outside']) - buy_need
diff_sell = np.array(aggregators_data['electric_microgrid.energy_sold_outside']) - sell_need
offset_buy = np.where(np.array(aggregators_data['electric_microgrid.energy_bought_outside']) > 7200, np.array(aggregators_data['electric_microgrid.energy_bought_outside']) - 7200, 0)
offset_sell = np.where(np.array(aggregators_data['electric_microgrid.energy_sold_outside']) > 22000, np.array(aggregators_data['electric_microgrid.energy_sold_outside']) - 22000, 0)
total_elec_error = np.abs(diff_buy) + np.abs(diff_sell) + np.abs(offset_buy) + np.abs(offset_sell)
relative_elec_error = np.divide(total_elec_error, np.array(aggregators_data['electric_microgrid.energy_sold_inside']), out=np.zeros_like(total_elec_error, dtype=float), where=np.array(aggregators_data['electric_microgrid.energy_sold_inside'])!=0)

# 2. District Heating Network (agent 2) - energy balance.
TES_charging = np.where(np.array(devices_data['Heat_storage.LTH.energy']) > 0, np.array(devices_data['Heat_storage.LTH.energy']), 0)
TES_discharging = np.where(np.array(devices_data['Heat_storage.LTH.energy']) < 0, - np.array(devices_data['Heat_storage.LTH.energy']), 0)
total_heat_load = (np.array(devices_data['space_heating.LTH.energy']) +
                   # np.array(devices_data['artificial_DHN.LTH.energy']) +
                   np.array(metrics_data['combined_heat_power.heat_by_pass']) +
                   TES_charging)
total_heat_supply = (- np.array(devices_data['heat_pump.LTH.energy']) -
                     np.array(devices_data['combined_heat_power.LTH.energy']) -
                     np.array(devices_data['Waste_to_heat.LTH.energy']) +
                     TES_discharging)
heat_imbalance = np.abs(total_heat_load - total_heat_supply)
heat_balance = np.abs(np.array(aggregators_data['district_heating_network.energy_sold_inside']) +
                np.array(aggregators_data['district_heating_network.energy_sold_outside']) -
                np.array(aggregators_data['district_heating_network.energy_bought_inside']) -
                np.array(aggregators_data['district_heating_network.energy_bought_outside']))
total_heat_error = np.maximum(heat_balance, heat_imbalance)
relative_heat_error = np.divide(total_heat_error, np.array(aggregators_data['district_heating_network.energy_sold_inside']), out=np.zeros_like(total_heat_error, dtype=float), where=np.array(aggregators_data['district_heating_network.energy_sold_inside'])!=0)

# 3. Score KPIs - operational objectives.
outside_balance_elec = np.array(metrics_data['electric_microgrid.money_earned_outside']) - np.array(metrics_data['electric_microgrid.money_spent_outside'])
social_cost = np.array(metrics_data['flexible_loads.LVE.energy_erased']) * np.array(metrics_data['flexible_loads.LVE.money'])
gas_cost = np.array(metrics_data['combined_heat_power.LPG.money_spent'])
heat_wasted = np.array(metrics_data['combined_heat_power.heat_by_pass']) * np.array(metrics_data['combined_heat_power.LTH.money'])
green_elec_supply = - np.array(devices_data['PV_field_1.LVE.energy']) - np.array(devices_data['PV_field_2.LVE.energy']) - np.array(devices_data['WT_field_1.LVE.energy']) - np.array(devices_data['WT_field_2.LVE.energy'])
tot_elec_supply = np.array(aggregators_data['electric_microgrid.energy_bought_outside']) + np.array(aggregators_data['electric_microgrid.energy_bought_inside'])
HP_injected = np.array(devices_data['heat_pump.LVE.energy'])
ratio_EnR = HP_injected * np.divide(green_elec_supply, tot_elec_supply, out=np.zeros_like(green_elec_supply, dtype=float), where=tot_elec_supply!=0)
green_HP_injected = np.sum(ratio_EnR) / np.sum(HP_injected)
DHN_heat_consumption = np.array(devices_data['space_heating.LTH.energy']) + TES_charging
green_heat_injected = np.abs(np.array(devices_data['heat_pump.LTH.energy'])) * green_HP_injected + np.abs(np.array(devices_data['Waste_to_heat.LTH.energy']))
total_green_heat_ratio = np.sum(green_heat_injected) / np.sum(DHN_heat_consumption)

# 4. Coordination mechanism. todo specific to MARL
# initial_EMG_controlled_signal = np.where(np.array(metrics_data['artificial_DHN.priority_tau']) > 0, 1, 0)
# initial_DHN_controlled_signal = np.where(np.array(metrics_data['artificial_DHN.priority_tau']) < 0, 1, 0)
# min_control_signal = np.where(np.array(metrics_data['artificial_DHN.priority_tau']) == 0, 1, 0)
# min_HP_elec = np.array(devices_data['heat_pump.LVE.energy']) * min_control_signal
# min_CHP_elec = np.array(devices_data['combined_heat_power.LVE.energy']) * min_control_signal
# min_HP_heat = np.array(devices_data['heat_pump.LTH.energy']) * min_control_signal
# min_CHP_heat = np.array(devices_data['combined_heat_power.LTH.energy']) * min_control_signal
# agent1_HP = np.array(agent1_decisions['heat_pump']) * min_control_signal
# agent1_CHP = np.array(agent1_decisions['combined_heat_power']) * min_control_signal
# agent2_HP = np.array(agent2_decisions['heat_pump']) * min_control_signal
# agent2_CHP = np.array(agent2_decisions['combined_heat_power']) * min_control_signal
# agent1_HP_decided_indices = who_decided(agent1_HP, min_HP_elec, 0.5)
# agent1_CHP_decided_indices = who_decided(agent1_CHP, min_CHP_elec, 0.5)
# agent2_HP_decided_indices = who_decided(agent2_HP, min_HP_heat, 0.5)
# agent2_CHP_decided_indices = who_decided(agent2_CHP, min_CHP_heat, 0.5)
# EMG_controlled_signal = initial_EMG_controlled_signal + agent1_HP_decided_indices + agent1_CHP_decided_indices
# EMG_controlled_signal = (EMG_controlled_signal != 0).astype(int)
# DHN_controlled_signal = initial_DHN_controlled_signal + agent2_HP_decided_indices + agent2_CHP_decided_indices
# DHN_controlled_signal = (DHN_controlled_signal != 0).astype(int)

# 5. Export of brut results (errors, score, etc...)
results_file = "/recap.txt"
with open(path_to_csv + results_file, "a") as myFile:
    myFile.write(f"\n\n******************************************************************************************\n\n")
    myFile.write(f"The total electricity imbalance error is : {np.sum(total_elec_error)} [kWh]\n")
    myFile.write(f"averaging : {np.average(total_elec_error)} [kWh], with a peak of {np.max(total_elec_error)} [kWh]\n")
    myFile.write(f"representing on average {np.average(relative_elec_error) * 100}% relative to electricity consumption in the EMG.\n")
    myFile.write(f"The total heat imbalance error is : {np.sum(total_heat_error)} [kWh]\n")
    myFile.write(f"averaging : {np.average(total_heat_error)} [kWh], with a peak of {np.max(total_heat_error)} [kWh]\n")
    myFile.write(f"representing on average {np.average(relative_heat_error) * 100}% relative to heat consumption in the DHN.\n")
    myFile.write(f"The score obtained is : {np.sum(outside_balance_elec) - np.sum(social_cost) - np.sum(gas_cost) - np.sum(heat_wasted)} €\n")
    myFile.write(f"of which, {np.sum(outside_balance_elec)} [€] is the external balance of the EMG\n")
    myFile.write(f"{np.sum(social_cost)} [€] represents the cost of unserved electricity loads amounting to {np.sum(np.array(metrics_data['flexible_loads.LVE.energy_erased']))} [kWh]\n")
    myFile.write(f"{np.sum(gas_cost)} [€] represents the gas/fuel cost of the combined heat and power\n")
    myFile.write(f"{np.sum(heat_wasted)} [€] represents the heat wasted by the CHP in the DHN which amounts to {np.sum(np.array(metrics_data['combined_heat_power.heat_by_pass']))} [kWh].\n")
    myFile.write(f"Finally, the renewable electricity ratio usage by the HP is : {total_green_heat_ratio * 100} %, corresponding to {sum(green_heat_injected)} [kWh].\n")
    myFile.write(f"and the total renewable heat supplied represents {total_green_heat_ratio * 100} % from total heat consumption, corresponding to {np.sum(green_heat_injected)} [kWh].")
    # myFile.write(f"Initially, the DHN controlled the CHP and HP for {np.sum(initial_DHN_controlled_signal)} hours.\n")
    # myFile.write(f"While, the EMG controlled them during {np.sum(initial_EMG_controlled_signal)} hours.\n")
    # myFile.write(f"And for the remaining {np.sum(min_control_signal)} hours, a minimum rule was applied.")

# III - Analyzing correlations and exporting graphs #
#####################################################
# 1. Coordination mechanism signal against energy imbalance
# fileName = "/CorrelationErrorControl.pdf"
# # a) Electricity MicroGrid
# sum_elec_error = np.sum(total_elec_error)
# EMG_controlled_error_ratio = (np.sum(initial_EMG_controlled_signal * total_elec_error) / sum_elec_error) * 100
# EMG_controlled_average_error = np.average(initial_EMG_controlled_signal * total_elec_error)
# EMG_controlled_peak_error = np.max(initial_EMG_controlled_signal * total_elec_error)
# # b) District Heating Network
# sum_heat_error = np.sum(total_heat_error)
# DHN_controlled_error_ratio = (np.sum(initial_DHN_controlled_signal * total_heat_error) / sum_heat_error) * 100
# DHN_controlled_average_error = np.average(initial_DHN_controlled_signal * total_heat_error)
# DHN_controlled_peak_error = np.max(initial_DHN_controlled_signal * total_heat_error)
# number_of_hours = np.arange(len(relative_heat_error))
# # --- Plotting both in one figure ---
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# fig, axes = plt.subplots(2, 2, figsize=(12, 8))
# # Subplot 1: relative imbalance error for the EMG
# axes[0,0].plot(number_of_hours, relative_elec_error, label="EMG electricity imbalance relative error", color="darkblue", linestyle='--')
# axes[0,0].set_xlabel("Simulation Steps [Hours]")
# axes[0,0].set_ylabel("Electricity Imbalance Relative Error [%]")
# axes[0,0].legend()
# axes[0,0].grid(True)
# # Subplot 2: relative imbalance error for the DHN
# axes[0,1].plot(number_of_hours, relative_heat_error, label="DHN heat imbalance relative error", color="darkred", linestyle='--')
# axes[0,1].set_xlabel("Simulation Steps [Hours]")
# axes[0,1].set_ylabel("Heat Imbalance Relative Error [%]")
# axes[0,1].legend()
# axes[0,1].grid(True)
# # Subplot 3: Electricity MicroGrid
# axes[1,0].plot(total_elec_error, initial_EMG_controlled_signal, label="EMG electricity imbalance vs control signal", color="darkblue", linestyle='', marker='x')
# axes[1,0].set_xlabel("Electricity Imbalance Error [kWh]")
# axes[1,0].set_ylabel("Control Signal")
# axes[1,0].legend()
# axes[1,0].grid(True)
# # Add statistics text box
# axes[1,0].text(
#     0.7, 0.75,
#     f"Share: {EMG_controlled_error_ratio:.3f}\nMean: {EMG_controlled_average_error:.3f}\nMax: {EMG_controlled_peak_error:.3f}",
#     transform=axes[1,0].transAxes,
#     fontsize=11,
#     verticalalignment="top",
#     bbox=dict(boxstyle="round", facecolor="white", alpha=0.7)
# )
# # Subplot 4: District Heating Network
# axes[1,1].plot(total_heat_error, initial_DHN_controlled_signal, label="DHN heat imbalance vs control signal", color="darkred", linestyle='', marker='*')
# axes[1,1].set_xlabel("Heat Imbalance Error [kWh]")
# axes[1,1].set_ylabel("Control Signal")
# axes[1,1].legend()
# axes[1,1].grid(True)
# # Add statistics text box
# axes[1,1].text(
#     0.7, 0.75,
#     f"Share: {DHN_controlled_error_ratio:.3f}\nMean: {DHN_controlled_average_error:.3f}\nMax: {DHN_controlled_peak_error:.3f}",
#     transform=axes[1,1].transAxes,
#     fontsize=11,
#     verticalalignment="top",
#     bbox=dict(boxstyle="round", facecolor="white", alpha=0.7)
# )
# plt.tight_layout()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# # plt.show()
# plt.close()
#
# # 2. HP.LVE against LVE.EnR
# fileName = "/CorrelationHeatPumpEnR.pdf"
# EMG_HP_controlled_signal = agent1_HP_decided_indices + initial_EMG_controlled_signal
# EMG_HP_controlled_signal = (EMG_HP_controlled_signal != 0).astype(int)
# EMG_HP_elec = EMG_HP_controlled_signal * np.array(devices_data['heat_pump.LVE.energy'])
# DHN_HP_controlled_signal = agent2_HP_decided_indices + initial_DHN_controlled_signal
# DHN_HP_controlled_signal = (DHN_HP_controlled_signal != 0).astype(int)
# DHN_HP_elec = DHN_HP_controlled_signal * np.array(devices_data['heat_pump.LVE.energy'])
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(green_elec_supply, EMG_HP_elec, 'bx', label="Controlled by EMG")
# plt.plot(green_elec_supply, DHN_HP_elec, 'r*', label="Controlled by DHN")
# plt.xlabel("Renewable Electricity Supply [kWh]")
# plt.ylabel("HP Electricity Consumption [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
#
# # 3. HP.LTH against CHP.LTH
# fileName = "/CorrelationHP_CHP_heat.pdf"
# EMG_CHP_controlled_signal = agent1_CHP_decided_indices + initial_EMG_controlled_signal
# EMG_CHP_controlled_signal = (EMG_CHP_controlled_signal != 0).astype(int)
# EMG_CHP_heat = EMG_CHP_controlled_signal * np.array(devices_data['combined_heat_power.LTH.energy'])
# DHN_CHP_controlled_signal = agent2_CHP_decided_indices + initial_DHN_controlled_signal
# DHN_CHP_controlled_signal = (DHN_CHP_controlled_signal != 0).astype(int)
# DHN_CHP_heat = DHN_CHP_controlled_signal * np.array(devices_data['combined_heat_power.LTH.energy'])
# EMG_HP_heat = EMG_HP_controlled_signal * np.array(devices_data['heat_pump.LTH.energy'])
# DHN_HP_heat = DHN_HP_controlled_signal * np.array(devices_data['heat_pump.LTH.energy'])
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(EMG_CHP_heat, EMG_HP_heat, 'bx', label="Controlled by EMG")
# plt.plot(DHN_CHP_heat, DHN_HP_heat, 'r*', label="Controlled by DHN")
# plt.xlabel("CHP Heat Supply [kWh]")
# plt.ylabel("HP Heat Supply [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
#
# # 4. HP.LTH against W2H.LTH
# fileName = "/CorrelationHP_Incinerator.pdf"
# W2h_axis = np.array(devices_data['Waste_to_heat.LTH.energy'])
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(W2h_axis, EMG_HP_heat, 'bx', label="Controlled by EMG")
# plt.plot(W2h_axis, DHN_HP_heat, 'r*', label="Controlled by DHN")
# plt.xlabel("Incinerator Heat Supply [kWh]")
# plt.ylabel("HP Heat Supply [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
#
# # 5. HP.LTH against TES
# fileName = "/CorrelationHP_TES.pdf"
# TES_axis = np.array(devices_data['Heat_storage.LTH.energy'])
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(TES_axis, EMG_HP_heat, 'bx', label="Controlled by EMG")
# plt.plot(TES_axis, DHN_HP_heat, 'r*', label="Controlled by DHN")
# plt.xlabel("Thermal Energy Storage Energy Flow [kWh]")
# plt.ylabel("HP Heat Supply [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
#
# # 6. CHP.LTH against W2H.LTH
# fileName = "/CorrelationCHP_Incinerator.pdf"
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(W2h_axis, EMG_CHP_heat, 'bx', label="Controlled by EMG")
# plt.plot(W2h_axis, DHN_CHP_heat, 'r*', label="Controlled by DHN")
# plt.xlabel("Incinerator Heat Supply [kWh]")
# plt.ylabel("CHP Heat Supply [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
#
# # 7. W2H.LTH against heat loads
# fileName = "/CorrelationIncinerator_HeatLoads.pdf"
# heat_loads = np.array(devices_data['space_heating.LTH.energy'])
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(heat_loads, W2h_axis, 'kx', label="Incinerator vs heat loads")
# plt.xlabel("Incinerator Heat Supply [kWh]")
# plt.ylabel("Space Heating Loads [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
#
# # 8. CHP against heat loads
# fileName = "/CorrelationCHP_HeatLoads.pdf"
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(heat_loads, EMG_CHP_heat, 'bx', label="Controlled by EMG")
# plt.plot(heat_loads, DHN_CHP_heat, 'r*', label="Controlled by DHN")
# plt.xlabel("Space Heating Loads [kWh]")
# plt.ylabel("CHP Heat Supply [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
#
# # 9. CHP.LVE against delta(gas_price, elec_price)
# fileName = "/CorrelationCHPPrice_ElectricityPrice.pdf"
# EMG_CHP_elec = EMG_CHP_controlled_signal * np.array(devices_data['combined_heat_power.LVE.energy'])
# DHN_CHP_elec = DHN_CHP_controlled_signal * np.array(devices_data['combined_heat_power.LVE.energy'])
# CHP_efficiencies = []
# CHP_prices_gas = []
# mainGrid_prices = []
# for element in metrics_data["combined_heat_power.LVE.energy_wanted"]:
#     d = ast.literal_eval(element)  # convert string → dict safely
#     CHP_efficiencies.append(d['efficiency'])
# for element in metrics_data["combined_heat_power.LPG.energy_wanted"]:
#     d = ast.literal_eval(element)  # convert string → dict safely
#     CHP_prices_gas.append(d['price'])
# for element in metrics_data["electric_microgrid.LVE.energy_wanted"]:
#     d = ast.literal_eval(element)  # convert string → dict safely
#     mainGrid_prices.append(d[0]['price'])
# CHP_elec_prices = np.divide(np.array(CHP_prices_gas), np.array(CHP_efficiencies), out=np.zeros_like(np.array(CHP_prices_gas), dtype=float), where=np.array(CHP_efficiencies)!=0)
# delta_prices = CHP_elec_prices - np.array(mainGrid_prices)
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(delta_prices, EMG_CHP_elec, 'bx', label="Controlled by EMG")
# plt.plot(delta_prices, DHN_CHP_elec, 'r*', label="Controlled by DHN")
# plt.xlabel("Delta prices gas-electricity [€]")
# plt.ylabel("CHP Electricity Supply [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
#
# # 10. TES energy flow values through the simulation
# fileName = "/TES_charging_discharging.pdf"
# plt.figure()
# plt.rcParams["font.family"] = "Times New Roman"
# plt.rcParams["font.size"] = 12
# plt.plot(number_of_hours, TES_charging, 'b--', label="Charging")
# plt.plot(number_of_hours, TES_discharging, 'r--', label="Discharging")
# plt.xlabel("Simulation Steps [Hours]")
# plt.ylabel("TES Heat Flow [kWh]")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()
