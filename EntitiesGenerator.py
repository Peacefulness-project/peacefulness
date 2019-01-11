# Here will be written functions to generate entities associated
# to a unique load behavior thanks to random generation
# in a real case of usage, these functions should be useless

# create_*(N) functions create N diffrents entities with different params
# load_*(entity,timestep) modifies attributes according to the specific params of the function


# Baseload
def create_Baseload(N):
    pass


def load_Baseload(entity,timestep):
    conso = [42, 69, 42]
    entity.energy = conso[timestep]

# Heating
def create_Heating(N):
    pass


def load_Heating(entity,timestep):
    pass


# PV
def create_PV(N):
    pass


def load_PV(entity,timestep):
    prod = [42, 42, 69]
    entity.energy = prod[timestep]


# WindTurbine
def create_WindTurbine(N):
    pass


def load_WindTurbine(entity,timestep):
    pass


# MainGrid
def create_MainGrid(N):
    pass


def load_MainGrid(entity,timestep):
    pass