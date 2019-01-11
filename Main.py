### IMPORT
import os
import numpy as np # pour les tableaux
import math as mt # pour la capacité infinie du reseau
'''import Classes
import Supervisor
import EntitiesGenerator
import Utilities'''

exec(open("Classes.py").read())
exec(open("Utilities.py").read())
exec(open("Supervisor.py").read())
exec(open("EntitiesGenerator.py").read())


### CREATION OF THE ENVIRONMENT
'''Here we create the different entitites (producer, consumer, storage, conversion points)... 
... which we want to simulate'''
maison = World(3)  # Creation of the world, which serves as a background for our grid


    ### Declaration of consumers
lumiere = Baseload('Low Voltage electricity')
chauffage = Heating('Low Voltage electricity')


    ### Declaration of producers
PV1 = PV()
Grid = MainGrid('Low Voltage electricity')

    ### Addition of the entities to the world
'''pas fait directement car on prevoit cluster'''
maison.add([PV1, Grid])
maison.add([lumiere, chauffage])


'''test pour verififier que tout se passe bien'''



### RESOLUTION
''' Here we call the supervisor, which regulates our virtual grid'''
supervisor(maison, strat_test)