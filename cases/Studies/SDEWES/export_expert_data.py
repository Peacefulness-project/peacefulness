# In this file, some utilities are defined to export results of expert strategy in the same manner as S, A, R
import csv
from copy import deepcopy

normalization_parameters = {"energy_minimum": - 4.0, "energy_maximum": 5.0, "price_minimum": 0.1, "price_maximum": 0.65}

class MyMemory:
    def __init__(self):
        self.my_raw_state = []
        self.my_norm_state = []
        self.my_action = []
        self.my_norm_action = []
        self.my_reward = []

expertMemory = MyMemory()

def export_expert_data(world_export_path: str):
    return_list = []
    for index in range(len(expertMemory.my_raw_state)):
        return_list.append(expertMemory.my_norm_state[index]+expertMemory.my_raw_state[index]+expertMemory.my_action[index]+expertMemory.my_norm_action[index])
        return_list[-1].append(expertMemory.my_reward[index])

    filepath = world_export_path
    myFilename = filepath + "/" + "expertTrajectory.csv"
    with open(myFilename, mode="w", newline="") as myFile:
        writer = csv.writer(myFile)
        writer.writerows(return_list)


def other_strategies_results(world: "World"):
    """
    This function is used to get the rewards for the strategies other than the DRL strategy for the same study-case.
    And it is also used to get the rewards for the DRL strategy when the model is trained.
    """
    results = {}
    # Getting the list of the dataloggers defined for the study_case
    for datalogger in world.catalog.dataloggers.values():
        datalogger_keys = datalogger.get_keys  # retrieving the keys to be exported by the datalogger
        results = {**results, **datalogger.request_keys(datalogger_keys)}

    # Defining the expert data (both in normalized and real spaces)
    expertMemory.my_raw_state.append(define_expert_state(results))
    expertMemory.my_norm_state.append(normalize_state_vector(expertMemory.my_raw_state[-1], world.time_limit))
    expertMemory.my_action.append(get_expert_decision(results))
    expertMemory.my_norm_action.append(normalize_action_vector(expertMemory.my_action[-1], expertMemory.my_raw_state[-1]))
    expertMemory.my_reward.append(calculate_reward(expertMemory.my_action[-1]))


def get_expert_decision(resulting_dict: dict):  # todo attention case specific
    energy_conso = resulting_dict["mirror_third_floor.internal_expert_message"]["quantity"] + resulting_dict["mirror_second_floor.internal_expert_message"]["quantity"] + resulting_dict["mirror_first_floor.internal_expert_message"]["quantity"]
    energy_prod = resulting_dict["mirror_roof_PV.internal_expert_message"]["quantity"] + resulting_dict["mirror_localDieselGenerator.internal_expert_message"]["quantity"]
    energy_storage = resulting_dict["mirror_BESS.internal_expert_message"]["quantity"]
    energy_exchange = []
    for key in resulting_dict:
        if "superior_expert_message" in key:
            energy_exchange.append(- resulting_dict[key][0]["quantity"])
        if "sub_expert_message" in key:
            energy_exchange.append(- resulting_dict[key][0]["quantity"])
    return [energy_conso, energy_prod, energy_storage, *energy_exchange]


def define_expert_state(resulting_dict: dict):  # todo attention case specific
    # initialization
    consumption_dict = {}
    production_dict = {}
    storage_dict = {}

    # getting the correct values from the resulting dict
    consumption_dict["Emin"] = resulting_dict["mirror_third_floor.message"]["energy_maximum"] + resulting_dict["mirror_second_floor.message"]["energy_minimum"] + resulting_dict["mirror_first_floor.message"]["energy_minimum"]
    consumption_dict["Emax"] = resulting_dict["mirror_third_floor.message"]["energy_maximum"] + resulting_dict["mirror_second_floor.message"]["energy_maximum"] + resulting_dict["mirror_first_floor.message"]["energy_maximum"]
    consumption_dict['flexibility'] = 0
    consumption_dict['interruptibility'] = 0
    consumption_dict['coming_volume'] = 0
    production_dict["Emin"] = resulting_dict["mirror_roof_PV.message"]["energy_minimum"] + resulting_dict["mirror_localDieselGenerator.message"]["energy_minimum"]
    production_dict["Emax"] = resulting_dict["mirror_roof_PV.message"]["energy_maximum"] + resulting_dict["mirror_localDieselGenerator.message"]["energy_maximum"]
    production_dict['flexibility'] = 0
    production_dict['interruptibility'] = 0
    production_dict['coming_volume'] = 0
    storage_dict["Emin"] = resulting_dict["mirror_BESS.message"]["energy_minimum"]
    storage_dict["Emax"] = resulting_dict["mirror_BESS.message"]["energy_maximum"]
    storage_dict["state_of_charge"] = resulting_dict["mirror_BESS.message"]['state_of_charge']
    storage_dict["capacity"] = resulting_dict["mirror_BESS.message"]['capacity']
    storage_dict["self_discharge_rate"] = - resulting_dict["mirror_BESS.message"]['self_discharge_rate']
    storage_dict["efficiency"] = resulting_dict["mirror_BESS.message"]['efficiency']['charge'] * resulting_dict["mirror_BESS.message"]['efficiency']['discharge']
    price_list = resulting_dict["Mirror_Aggregator_energy_prices_message"]
    exchange_list = resulting_dict["mirror_home_aggregator.exchange_message"]

    # constructing the state vector in the real space
    return [resulting_dict["simulation_time"], *list(consumption_dict.values()), *list(production_dict.values()), *list(storage_dict.values()), *price_list, *exchange_list]


def normalize_state_vector(state_vector: list, finish_time):
    return_list = deepcopy(state_vector)
    for index in range(len(return_list)):
        if index == 0:
            return_list[index] = return_list[index] / finish_time
        elif index == 17 or index == 18:
            return_list[index] = (return_list[index] - normalization_parameters["price_minimum"]) / (normalization_parameters["price_maximum"] - normalization_parameters["price_minimum"])
        elif index != 13 and index != 15 and index != 16 and index != 21:
            return_list[index] = (return_list[index] - normalization_parameters["energy_minimum"]) / (normalization_parameters["energy_maximum"] - normalization_parameters["energy_minimum"])
    return return_list


def normalize_action_vector(real_action: list, raw_state: list):  # todo case specific
    return_list = deepcopy(real_action)
    if raw_state[1] != raw_state[2]:  # consumption
        return_list[0] = (return_list[0] - raw_state[1]) / (raw_state[2] - raw_state[1])
    else:
        return_list[0] = 0.5
    if raw_state[6] != raw_state[7]:  # production
        return_list[1] = (return_list[1] - raw_state[6]) / (raw_state[7] - raw_state[6])
    else:
        return_list[1] = 0.5
    if raw_state[11] != raw_state[12]:  # storage
        return_list[2] = (return_list[2] - raw_state[11]) / (raw_state[12] - raw_state[11])
    else:
        return_list[2] = 0.5
    if raw_state[19] != raw_state[20]:  # exchange
        return_list[3] = (return_list[3] - raw_state[19]) / (raw_state[20] - raw_state[19])
    else:
        return_list[3] = 0.5
    return return_list

def calculate_reward(expertDecision: list):
    reward_results = expertDecision[-1] - 15 * abs(sum(expertDecision))  # if by chance the Rule-based strategy doesn't respect energy conservation

    return reward_results