from typing import Dict


def SRL_PBRS_final_Rt(reward, cumul_dict: Dict):
    """
    Reward function that guides the single RL agent in case of Potential based reward shaping.
    """
    opex = cumul_dict["OPEX"]
    green_injection = cumul_dict["total_green_supply"]

    # Second formulation : direct comparison with RBS
    RBS_OPEX = -8827890.296
    RBS_green_injection = 0.8652762392

    OPEX_comp = - (abs(opex) - abs(RBS_OPEX)) / abs(RBS_OPEX)
    GREEN_comp = (green_injection - RBS_green_injection) / RBS_green_injection

    if not isinstance(reward, dict):  # TODO for single agent RL
        # First formulation : rewarding through OPEX + total green heat
        # HP_green_heat = cumul_dict["total_HP_green_injection"] * cumul_dict["HP_money"]
        # W2h_heat = cumul_dict["incinerator_heat"] * cumul_dict["W2h_money"]

        return_val = reward + OPEX_comp + GREEN_comp

    else:  # TODO for 2-agents RL
        for agent in cumul_dict['priority_hours']:
            reward[agent] += (cumul_dict['priority_hours'][agent] / cumul_dict['time_limit']) * (OPEX_comp + GREEN_comp)
        return_val = reward

    return return_val
