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
GrandTruc= World() # Creation of the world, which serves as a background for our grid

    ### Declaration of consumers
Bidule1= Consumer(0)
Bidule2= Consumer(0)

    ### Declaration of producers
Reseau= Producer(0)


    ### Addition of the entities to the world
'''pas fait directement car on prevoit cluster'''
GrandTruc.add(Reseau)
GrandTruc.add( [Bidule1, Bidule2])

'''test pour verififier que tout se passe bien'''
print(GrandTruc.EntityList[1].Priority,GrandTruc.EntityList[2].Priority)

### RESOLUTION or "moulinette magique"
''' Here we call the supervisor, which regulates our virtual grid'''
exec(open("Supervisor.py").read())

### POST-PROCESSING
'''Here we write files containing the history and the overview of the simulation'''
'''je ne sais pas si on doit vraiment le detacher du superviseur'''
