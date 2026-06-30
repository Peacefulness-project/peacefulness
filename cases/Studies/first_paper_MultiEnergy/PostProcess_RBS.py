# In this file, a post-process script is executed to do the Excel manipulation to get final results.
# Additionally, it will output also figures, and a text file recapitulating the results.
# Worth noting, is the fact that it is case specific, however many functions can be re-used for different case studies.

# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import ast
import re
from scipy.fft import fft, fftfreq



# I - We read the data from PEACEFULNESS '.csv' outputs into dicts #
####################################################################
path_to_csv = "D:/dossier_y23hallo/Thèse/multi-energy/FINAL-RESULTS/RBS/real_final-min-CHP"  # path to inference results folder

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

# II - Processing the results #
###############################
# 1. Electric Microgrid (agent 1) - energy balance.
total_elec_load = (np.array(devices_data['rigid_electricity_consumption.LVE.energy']) +
                   np.array(devices_data['flexible_loads.LVE.energy']) +
                   np.array(devices_data['heat_pump.LVE.energy']))
total_elec_supply = (- np.array(devices_data['PV_field.LVE.energy']) -
                     np.array(devices_data['WT_field_1.LVE.energy']) -
                     np.array(devices_data['WT_field_2.LVE.energy']) -
                     np.array(devices_data['combined_heat_power.LVE.energy']))
elec_imbalance = total_elec_load - total_elec_supply
buy_need = np.where(elec_imbalance >= 0, elec_imbalance, 0)
sell_need = np.where(elec_imbalance < 0, - elec_imbalance, 0)
elec_balance = abs(np.array(aggregators_data['electric_microgrid.energy_sold_inside']) +
                np.array(aggregators_data['electric_microgrid.energy_sold_outside']) -
                np.array(aggregators_data['electric_microgrid.energy_bought_inside']) -
                np.array(aggregators_data['electric_microgrid.energy_bought_outside']))
diff_buy = np.array(aggregators_data['electric_microgrid.energy_bought_outside']) - buy_need
diff_sell = np.array(aggregators_data['electric_microgrid.energy_sold_outside']) - sell_need
relative_elec_error = np.divide(elec_balance, np.array(aggregators_data['electric_microgrid.energy_sold_inside']), out=np.zeros_like(elec_balance, dtype=float), where=np.array(aggregators_data['electric_microgrid.energy_sold_inside'])!=0)

# 2. District Heating Network (agent 2) - energy balance.
TES_charging = np.where(np.array(devices_data['Heat_storage.LTH.energy']) > 0, np.array(devices_data['Heat_storage.LTH.energy']), 0)
TES_discharging = np.where(np.array(devices_data['Heat_storage.LTH.energy']) < 0, - np.array(devices_data['Heat_storage.LTH.energy']), 0)
total_heat_load = (np.array(devices_data['space_heating.LTH.energy']) +
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
# social_cost = np.array(metrics_data['flexible_loads.LVE.money_spent'])
gas_cost = np.array(metrics_data['combined_heat_power.LPG.money_spent'])
# heat_dissipated = np.array(metrics_data["Waste_to_heat.heat_dissipated"]) * np.array(metrics_data["Waste_to_heat.LTH.money"])
heat_wasted = np.array(metrics_data['combined_heat_power.heat_by_pass']) * np.array(metrics_data['combined_heat_power.LTH.money'])
green_elec_supply = - np.array(devices_data['PV_field.LVE.energy']) - np.array(devices_data['WT_field_1.LVE.energy']) - np.array(devices_data['WT_field_2.LVE.energy'])
tot_elec_supply = np.array(aggregators_data['electric_microgrid.energy_bought_outside']) + np.array(aggregators_data['electric_microgrid.energy_bought_inside'])
HP_injected = np.array(devices_data['heat_pump.LVE.energy'])
ratio_EnR = HP_injected * np.divide(green_elec_supply, tot_elec_supply, out=np.zeros_like(green_elec_supply, dtype=float), where=tot_elec_supply!=0)
green_HP_injected = np.sum(ratio_EnR) / np.sum(HP_injected)
DHN_heat_consumption = np.array(devices_data['space_heating.LTH.energy'])
green_heat_injected = np.abs(np.array(devices_data['heat_pump.LTH.energy'])) * green_HP_injected + np.abs(np.array(devices_data['Waste_to_heat.LTH.energy']))
total_green_heat_ratio = np.sum(green_heat_injected) / np.sum(DHN_heat_consumption)

# 4. Export of brut results (errors, score, etc...)
results_file = "/recap.txt"
with open(path_to_csv + results_file, "a") as myFile:
    myFile.write(f"\n\n******************************************************************************************\n\n")
    myFile.write(f"The total electricity imbalance error is : {np.sum(elec_balance)} [kWh]\n")
    myFile.write(f"averaging : {np.average(elec_balance)} [kWh], with a peak of {np.max(elec_balance)} [kWh]\n")
    myFile.write(f"representing on average {np.average(relative_elec_error) * 100}% relative to electricity consumption in the EMG.\n")
    myFile.write(f"The total heat imbalance error is : {np.sum(total_heat_error)} [kWh]\n")
    myFile.write(f"averaging : {np.average(total_heat_error)} [kWh], with a peak of {np.max(total_heat_error)} [kWh]\n")
    myFile.write(f"representing on average {np.average(relative_heat_error) * 100}% relative to heat consumption in the DHN.\n")
    myFile.write(f"The score obtained is : {np.sum(outside_balance_elec) - np.sum(gas_cost) - np.sum(heat_wasted)} €\n")
    myFile.write(f"of which, {np.sum(outside_balance_elec)} [€] is the external balance of the EMG\n")
    # myFile.write(f"{np.sum(social_cost)} [€] represents the cost of unserved electricity loads amounting to {np.sum(np.array(metrics_data['flexible_loads.LVE.energy_erased']))} [kWh]\n")
    myFile.write(f"{np.sum(gas_cost)} [€] represents the gas/fuel cost of the combined heat and power\n")
    myFile.write(f"{np.sum(heat_wasted)} [€] represents the heat wasted by the CHP in the DHN which amounts to {np.sum(np.array(metrics_data['combined_heat_power.heat_by_pass']))} [kWh].\n")
    # myFile.write(f"and {np.sum(heat_dissipated)} [€] represents the cost related to the dissipated heat from the incinerator which amounts to {np.sum(metrics_data["Waste_to_heat.heat_dissipated"])} [kWh]\n")
    myFile.write(f"Finally, the renewable electricity ratio usage by the HP is : {green_HP_injected * 100} %, corresponding to {np.sum(ratio_EnR)} [kWh].\n")
    myFile.write(f"and the total renewable heat supplied represents {total_green_heat_ratio * 100} % from total heat consumption, corresponding to {np.sum(green_heat_injected)} [kWh].")


# III - Analyzing correlations and exporting graphs #
#####################################################
# 1. HP.LVE against excess LVE.EnR
fileName = "/CorrelationHeatPumpEnR.pdf"
norm_HP_injected = HP_injected / np.max(HP_injected)
norm_EnR = green_elec_supply - np.array(devices_data['rigid_electricity_consumption.LVE.energy'])
norm_EnR = (norm_EnR - np.min(norm_EnR)) / (np.max(norm_EnR) - np.min(norm_EnR)) * 2 - 1
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(norm_EnR, norm_HP_injected, 'b*')
plt.xlabel("Renewable Electricity Supply Excess [kWh]")
plt.ylabel("HP Electricity Consumption [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 2. HP.LTH against CHP.LTH
fileName = "/CorrelationHP_CHP_heat.pdf"
HP_heat_supply = np.array(devices_data['heat_pump.LTH.energy'])
HP_heat_supply = np.abs(HP_heat_supply)
HP_heat_supply /= np.max(HP_heat_supply)
CHP_heat_supply = np.array(devices_data['combined_heat_power.LTH.energy'])
CHP_heat_supply = np.abs(CHP_heat_supply)
CHP_heat_supply /= np.max(CHP_heat_supply)
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(CHP_heat_supply, HP_heat_supply, 'r*')
plt.xlabel("CHP Heat Supply [kWh]")
plt.ylabel("HP Heat Supply [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 3. HP.LTH against W2H.LTH
fileName = "/CorrelationHP_Incinerator.pdf"
W2h_axis = np.array(devices_data['Waste_to_heat.LTH.energy'])
W2h_axis = np.abs(W2h_axis)
W2h_axis /= np.max(W2h_axis)
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(W2h_axis, HP_heat_supply, 'r*')
plt.xlabel("Incinerator Heat Supply [kWh]")
plt.ylabel("HP Heat Supply [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 4. HP.LTH against heat loads
fileName = "/CorrelationHP_HeatLoads.pdf"
heat_loads = np.array(devices_data['space_heating.LTH.energy'])
heat_loads /= np.max(heat_loads)
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(heat_loads, HP_heat_supply, 'r*')
plt.xlabel("Space Heating Loads [kWh]")
plt.ylabel("HP Heat Supply [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 5. HP.LTH against TES
fileName = "/CorrelationHP_TES.pdf"
TES_axis = np.array(devices_data['Heat_storage.LTH.energy'])
TES_axis = (2 / (np.max(TES_axis) - np.min(TES_axis))) * (TES_axis - np.min(TES_axis)) - 1
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(TES_axis, HP_heat_supply, 'r*')
plt.xlabel("Thermal Energy Storage Energy Flow [kWh]")
plt.ylabel("HP Heat Supply [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 6. CHP.LTH against W2H.LTH
fileName = "/CorrelationCHP_Incinerator.pdf"
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(W2h_axis, CHP_heat_supply, 'r*')
plt.xlabel("Incinerator Heat Supply [kWh]")
plt.ylabel("CHP Heat Supply [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 7. W2H.LTH against heat loads
fileName = "/CorrelationIncinerator_HeatLoads.pdf"
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(heat_loads, W2h_axis, 'r*', label="Incinerator vs heat loads")
plt.xlabel("Space Heating Loads [kWh]")
plt.ylabel("Incinerator Heat Supply [kWh]")
plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 8. CHP against heat loads
fileName = "/CorrelationCHP_HeatLoads.pdf"
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(heat_loads, CHP_heat_supply, 'r*')
plt.xlabel("Space Heating Loads [kWh]")
plt.ylabel("CHP Heat Supply [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 9. CHP against electricity loads
fileName = "/CorrelationCHP_ElecLoads.pdf"
elec_loads = np.array(devices_data['rigid_electricity_consumption.LVE.energy'])
elec_loads /= np.max(elec_loads)
CHP_elec_supply = np.array(devices_data['combined_heat_power.LVE.energy'])
CHP_elec_supply = np.abs(CHP_elec_supply)
CHP_elec_supply /= np.max(CHP_elec_supply)
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(elec_loads, CHP_elec_supply, 'b*')
plt.xlabel("Electricity Rigid Loads [kWh]")
plt.ylabel("CHP Electricity Supply [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 10. CHP.LVE against delta(gas_price, elec_price)
fileName = "/CorrelationCHPPrice_ElectricityPrice.pdf"
CHP_efficiencies = []
CHP_prices_gas = []
mainGrid_prices = []
for element in metrics_data["combined_heat_power.LVE.energy_wanted"]:
    d = ast.literal_eval(element)  # convert string → dict safely
    CHP_efficiencies.append(d['efficiency'])
for element in metrics_data["combined_heat_power.LPG.energy_wanted"]:
    d = ast.literal_eval(element)  # convert string → dict safely
    CHP_prices_gas.append(d['price'])
for element in metrics_data["electric_microgrid.LVE.energy_wanted"]:
    cleaned = re.sub(r'np\.float64\(([^)]+)\)', r'\1', element)
    d = ast.literal_eval(cleaned)  # convert string → dict safely
    if len(d) > 0:
        mainGrid_prices.append(d[0]['price'])
    else:
        mainGrid_prices.append(0.0)
CHP_elec_prices = np.divide(np.array(CHP_prices_gas), np.array(CHP_efficiencies), out=np.zeros_like(np.array(CHP_prices_gas), dtype=float), where=np.array(CHP_efficiencies)!=0)
delta_prices = CHP_elec_prices - np.array(mainGrid_prices)
delta_prices = (2 / (np.max(delta_prices) - np.min(delta_prices))) * (delta_prices - np.min(delta_prices)) - 1
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(delta_prices, CHP_elec_supply, 'b*')
plt.xlabel("Delta Prices Gas-Electricity [€/kWh]")
plt.ylabel("CHP Electricity Supply [kWh]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 11. TES energy flow values through the simulation
fileName = "/TES_charging_discharging.pdf"
number_of_hours = np.arange(len(relative_heat_error))
# TES_charging = np.sort(TES_charging)[::-1]
TES_charging /= np.max(TES_charging)
# TES_discharging = np.sort(TES_discharging)[::-1]
TES_discharging /= np.max(TES_discharging)
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(number_of_hours, TES_charging, 'b--', label="Charging")
plt.plot(number_of_hours, TES_discharging, 'r--', label="Discharging")
plt.xlabel("Simulation Steps [Hours]")
plt.ylabel("TES Heat Flow [kWh]")
plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 12. Exchange with main grid against electric flexible loads
fileName = "/MainGrid_shift.pdf"
shift_loads = np.array(devices_data["flexible_loads.LVE.energy"])
shift_loads /= np.max(shift_loads)
elec_bought_out = np.array(aggregators_data["electric_microgrid.energy_bought_outside"])
elec_bought_out /= np.max(elec_bought_out)
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(shift_loads, elec_bought_out, 'bx', label="Supplied by main grid")
plt.plot(shift_loads, norm_EnR, 'y.', label="Supplied by EnR")
plt.plot(shift_loads, CHP_elec_supply, 'r*', label="Supplied by CHP")
plt.xlabel("Flexible Loads [kWh]")
plt.ylabel("Electricity Supply [kWh]")
plt.legend(loc="upper right")
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 13. TES state of charge against Heat Loads
fileName = "/socTES_HeatLoads.pdf"
SoC = np.array(logs_data["Heat_storage.energy_stored"])
SoC = (SoC - np.min(SoC)) / (np.max(SoC) - np.min(SoC))
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(heat_loads, SoC, 'rx')
plt.xlabel("Heat Loads [kWh]")
plt.ylabel("TES State of Charge [%]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 14. TES state of charge against TES heat flows
fileName = "/socTES_TESflows.pdf"
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(TES_axis, SoC, 'r*')
plt.xlabel("TES Heat Flows [kWh]")
plt.ylabel("TES State of Charge [%]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 15. TES state of charge against EnR
fileName = "/socTES_EnR.pdf"
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(norm_EnR, SoC, 'r*')
plt.xlabel("Renewable Electricity Supply Excess [kWh]")
plt.ylabel("TES State of Charge [%]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 16. TES state of charge against Incinerator heat supply
fileName = "/socTES_Incinerator.pdf"
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(W2h_axis, SoC, 'r*')
plt.xlabel("Incinerator Heat Supply [kWh]")
plt.ylabel("TES State of Charge [%]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 17. TES state of charge against HP heat supply
fileName = "/socTES_HP.pdf"
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(HP_heat_supply, SoC, 'r*')
plt.xlabel("HP Heat Supply [kWh]")
plt.ylabel("TES State of Charge [%]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 18. TES state of charge against CHP heat supply
fileName = "/socTES_CHP.pdf"
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(CHP_heat_supply, SoC, 'r*')
plt.xlabel("CHP Heat Supply [kWh]")
plt.ylabel("TES State of Charge [%]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 19. TES state of charge over time
fileName = "/socTES_time.pdf"
# SoC = np.sort(SoC)[::-1]
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(number_of_hours, SoC, 'k.')
plt.xlabel("Number of Hours [Hours]")
plt.ylabel("TES State of Charge [%]")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()
#
# # 20. FFT analysis cycle of the TES charging/discharging
fileName = "/TES_charging_discharging_fft.pdf"
# SoC -= np.average(SoC)
ySoC = fft(SoC)
xtime = fftfreq(len(number_of_hours), 1)[: len(number_of_hours) // 2]
plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.plot(xtime, 2 / len(number_of_hours) * np.abs(ySoC[0 : len(number_of_hours) // 2]))
plt.xlabel("Frequency [Cycle per Hour]")
plt.ylabel("Magnitude")
# plt.legend()
plt.grid(True)
plt.tight_layout()
# plt.show()
plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
plt.close()


# 3d plot - Correlation CHP vs Heat/Electricity loads & gas prices
# fileName = "/correlation_CHP_Loads_Prices.pdf"
# heat_loads = np.array(devices_data['space_heating.LTH.energy'])
# heat_loads /= np.max(heat_loads)
# elec_loads = np.array(devices_data['rigid_electricity_consumption.LVE.energy'])
# elec_loads /= np.max(elec_loads)
# CHP_supply = np.array(devices_data['combined_heat_power.LPG.energy'])
# CHP_supply /= np.max(CHP_supply)
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
#     cleaned = re.sub(r'np\.float64\(([^)]+)\)', r'\1', element)
#     d = ast.literal_eval(cleaned)  # convert string → dict safely
#     if len(d) > 0:
#         mainGrid_prices.append(d[0]['price'])
#     else:
#         mainGrid_prices.append(0.0)
# CHP_elec_prices = np.divide(np.array(CHP_prices_gas), np.array(CHP_efficiencies), out=np.zeros_like(np.array(CHP_prices_gas), dtype=float), where=np.array(CHP_efficiencies)!=0)
# delta_prices = CHP_elec_prices - np.array(mainGrid_prices)
# low_mask = delta_prices < 0
# high_mask = delta_prices >= 0
# CHP_low_gas_price = CHP_supply[low_mask]
# elec_low_gas_loads = elec_loads[low_mask]
# heat_low_gas_loads = heat_loads[low_mask]
# CHP_high_gas_price = CHP_supply[high_mask]
# elec_high_gas_loads = elec_loads[high_mask]
# heat_high_gas_loads = heat_loads[high_mask]
# fig = plt.figure(figsize=(8,6))
# ax = fig.add_subplot(111, projection='3d')
# plt.plot(heat_loads, TES_axis, 'r*')
# plt.show()

# ax.scatter3D(heat_low_gas_loads, elec_low_gas_loads, CHP_low_gas_price, label='Low Gas Price')
# ax.scatter3D(heat_high_gas_loads, elec_high_gas_loads, CHP_high_gas_price, label='High Gas Price')
# #              # c=delta_prices, cmap='tab10')
# ax.set_title("Correlation_CHP_Prices_Loads")
# ax.legend()
# ax.set_xlabel("Heat Loads")
# ax.set_ylabel("Electricity Loads")
# ax.set_zlabel("CHP Rated Power")
# plt.grid(True)
# plt.tight_layout()
# #
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()

# 3d plot - Correlation HP vs. TES vs. Heat Loads & EnR excess
# fileName = "/correlation_HP_TES_HeatLoads_EnR.pdf"
# heat_loads = np.array(devices_data['space_heating.LTH.energy'])
# heat_loads /= np.max(heat_loads)
# TES_axis = np.array(devices_data['Heat_storage.LTH.energy'])
# TES_axis = (2 / (np.max(TES_axis) - np.min(TES_axis))) * (TES_axis - np.min(TES_axis)) - 1
# HP_heat_supply = - np.array(devices_data['heat_pump.LTH.energy'])
# HP_heat_supply /= np.max(HP_heat_supply)
# norm_EnR = green_elec_supply - np.array(devices_data['rigid_electricity_consumption.LVE.energy'])
# low_mask = norm_EnR >= 0
# high_mask = norm_EnR < 0
# HP_green = HP_heat_supply[low_mask]
# Lth_green = heat_loads[low_mask]
# TES_green = TES_axis[low_mask]
# HP_grey = HP_heat_supply[high_mask]
# Lth_grey = heat_loads[high_mask]
# TES_grey = TES_axis[high_mask]
#
# fig = plt.figure(figsize=(8,6))
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter3D(Lth_green, TES_green, HP_green, label='EnR excess')
# ax.scatter3D(Lth_grey, TES_grey, HP_grey, label='EnR deficit')
# #              # c=delta_prices, cmap='tab10')
# ax.set_title("Correlation_HP_TES_Loads")
# ax.legend()
# ax.set_xlabel("Heat Loads")
# ax.set_ylabel("TES Flows")
# ax.set_zlabel("HP Heat Supply")
# plt.grid(True)
# plt.tight_layout()
# #
# # plt.show()
# plt.savefig(path_to_csv + fileName, format="pdf", bbox_inches="tight")
# plt.close()

