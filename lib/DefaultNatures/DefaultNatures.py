from src.common.Nature import Nature


def load_all_default_natures():  # this function creates all the predefined natures, which are used in consumption profiles of devices
    # low voltage electricity
    LVE = load_low_voltage_electricity()

    # high voltage electricity
    HVE = load_high_voltage_electricity()

    # low temperature heat
    LTH = load_low_temperature_heat()

    # medium temperature heat
    MTH = load_medium_temperature_heat()

    # high temperature heat
    HTH = load_high_temperature_heat()

    # low temperature coldness
    LTC = load_low_temperature_coldness()

    # high temperature coldness
    HTC = load_high_temperature_coldness()

    # low pressure gas
    LPG = load_low_pressure_gas()

    # high pressure gas
    HPG = load_high_pressure_gas()

    return [LVE, HVE, LTH, MTH, HTH, LTC, HTC, LPG, HPG]


def load_low_voltage_electricity():  # this function returns the LVE nature
    # electricity for domestic electrical appliances
    nature_name = "LVE"
    nature_description = "Low Voltage Electricity"
    LVE = Nature(nature_name, nature_description)

    return LVE


def load_high_voltage_electricity():  # this function returns the HVE nature
    # electricity for industrial appliances
    nature_name = "HVE"
    nature_description = "High Voltage Electricity"
    HVE = Nature(nature_name, nature_description)

    return HVE


def load_low_temperature_heat():  # this function returns the LTH nature
    # heat energy used to heat residential buildings and for domestic hot water
    nature_name = "LTH"
    nature_description = "Low Temperature Heat"
    LTH = Nature(nature_name, nature_description)

    return LTH


def load_medium_temperature_heat():  # this function returns the MTH nature
    #
    nature_name = "MTH"
    nature_description = "Medium Temperature Heat"
    MTH = Nature(nature_name, nature_description)

    return MTH


def load_high_temperature_heat():  # this function returns the HTH nature
    #
    nature_name = "HTH"
    nature_description = "High Temperature Heat"
    HTH = Nature(nature_name, nature_description)

    return HTH


def load_low_temperature_coldness():  # this function returns the LTC nature
    # coldness used for industrial appliances
    nature_name = "LTC"
    nature_description = "Low Temperature Coldness"
    LTC = Nature(nature_name, nature_description)

    return LTC


def load_high_temperature_coldness():  # this function returns the HTC nature
    # coldness used to refresh residential buildings
    nature_name = "HTC"
    nature_description = "High Temperature Coldness"
    HTC = Nature(nature_name, nature_description)

    return HTC


def load_low_pressure_gas():  # this function returns the LPG nature
    # gas used for domestic usages, such as heating residential buildings and domestic hot water
    nature_name = "LPG"
    nature_description = "Low Pressure Gas"
    LPG = Nature(nature_name, nature_description)

    return LPG


def load_high_pressure_gas():  # this function returns the HPG nature
    # gas used for industrial usages
    nature_name = "HPG"
    nature_description = "High Pressure Gas"
    HPG = Nature(nature_name, nature_description)

    return HPG


