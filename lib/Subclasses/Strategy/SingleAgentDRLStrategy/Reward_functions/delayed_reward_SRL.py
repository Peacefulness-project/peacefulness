from typing import Dict


def SRL_PBRS_final_Rt(reward: float, cumul_dict: Dict):
    """
    Reward function that guides the single RL agent in case of Potential based reward shaping.
    """
    # First formulation : rewarding through OPEX + total green heat
    opex = cumul_dict["OPEX"]
    # HP_green_heat = cumul_dict["total_HP_green_injection"] * cumul_dict["HP_money"]
    # W2h_heat = cumul_dict["incinerator_heat"] * cumul_dict["W2h_money"]

    # Second formulation : direct comparison with RBS
    RBS_OPEX = -12189435.8547157
    RBS_green_injection = 0.817601088191838
    green_injection = cumul_dict["total_green_supply"]

    OPEX_comp = - (abs(opex) - abs(RBS_OPEX)) / abs(RBS_OPEX)
    GREEN_comp = (green_injection - RBS_green_injection) / RBS_green_injection

    return reward + OPEX_comp + GREEN_comp
