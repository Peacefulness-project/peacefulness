### IMPORT
import os
import numpy as np # pour les tableaux
import math as mt # pour la capacité infinie du reseau


### INSTANTIATION OF CLASSES
exec(open("Classes.py").read())

###PARAMETERS


### CREATION OF THE ENVIRONMENT
'''Here we create the different entitites (producer, consumer, storage, conversion points)... 
... which we want to simulate'''
grand_truc = World() # Creation of the world, which serves as a background for our grid

    ### Declaration of consumers
lumiere = NonSchedulable('LVelec')
chauffage = Heating('LVelec')

    ### Declaration of producers
PV = PV()


    ### Addition of the entities to the world
'''pas fait directement car on prevoit cluster'''
grand_truc.add(PV)
grand_truc.add([lumiere, chauffage])

'''test pour verififier que tout se passe bien'''
print(grand_truc.entity_list[1].priority,grand_truc.entity_list[2].priority)

### RESOLUTION or "moulinette magique"
''' Here we call the supervisor, which regulates our virtual grid'''
exec(open("Supervisor.py").read())

### POST-PROCESSING
'''Here we write files containing the history and the overview of the simulation'''
'''je ne sais pas si on doit vraiment le detacher du superviseur'''
