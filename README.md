# PEACEFULNESS

To launch a simulation:
1) Creation of data catalog(s)
2) Creation of environment(s): associated with a data catalog
3) Creation of entities, i.e producers, consumers, etc
4) Association of the entities with environment(s)
5) Creation of datalogger(s): write desired results in a file, associated with a data catalog
6) WIP

**Data catalogs**  
Data catalogs are dictionaries associated with an environment.
They gather all data for the current time step.
During the simulation step, decisions will be written there.
During the post-processing step, data exported are extracted from catalogs.