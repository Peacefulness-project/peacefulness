### IMPORT
import os
import math as mt # pour la capacité infinie du reseau
'''import Classes
import Supervisor
import EntitiesGenerator
import Utilities'''

exec(open("MainClasses.py").read())
exec(open("Consumers.py").read())
exec(open("Producers.py").read())
#exec(open("Utilities.py").read())
exec(open("Supervisor.py").read())
#exec(open("EntitiesGenerator.py").read())


### INITIALIZATION

# The following variables are lists
CONS = []  # list of different types of consumers
PROD = []  # list of different types of producers
# STOR = []
# TRAN = []
NATURE = []  # list of different natures of energy

# Creation of the environment
maison = World(3)  # Creation of 'world', which serves as a background for our grid

patate = dict()
Entity.create(3, patate, 'patate', 'tartiflette')

# Declaration of consumers
lumiere = dict()
Baseload.create(4, lumiere, 'lumiere', 'LVelec')
chauffage = dict()
Heating.create(1, chauffage, 'chauffage', 'gas')

# Declaration of producers
petits_panneaux = dict()
PV.create(3, petits_panneaux, 'petits_panneaux', 'LVelec')

# Addition of the entities to the world
maison.add(lumiere)
maison.add(chauffage)
maison.add(petits_panneaux)


'''tests pour verifier que tout se passe bien'''
print(CONS)
print(PROD)
print(NATURE)
print(maison.entity_dict)
print(type(maison.entity_dict['lumiere_0']))


### RESOLUTION
''' Here we call the supervisor, which regulates our virtual grid'''
supervisor(maison, strat_test)
