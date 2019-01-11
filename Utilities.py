# This sheet regroups little things used to simplify the rest of the program


# The following variables are booleans used to test easily the nature of an entity
CONS = [Baseload, Heating]
PROD = [PV, WindTurbine, MainGrid]
# STOR
# TRAN


# List of energy natures
NATURE = ["Low Voltage electricity", "gas"]


# The following functions update the attributes of each entity at the beginning of a timestep
def read_Baseload(entity, timestep):
    load_Baseload(entity, timestep)


def read_Heating(entity, timestep):
    load_Heating(entity, timestep)


def read_MainGrid(entity, timestep):
    load_MainGrid(entity, timestep)


def read_PV(entity, timestep):
    load_PV(entity, timestep)


def read_WindTurbine(entity, timestep):
    load_WindTurbine(entity, timestep)

def read_MainGrid(entity, timestep):
    load_MainGrid(entity, timestep)