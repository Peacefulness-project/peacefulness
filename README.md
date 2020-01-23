#                                               PEACEFULNESS
           Platform for transverse evaluation of control strategies for multi-energy smart grids
Coordinators: Dr E. Franquet, Dr S. Gibout (erwin.franquet@univ-pau.fr, stephane.gibout@univ-pau.fr)
Contributors (alphabetical order): Dr E. Franquet, Dr S. Gibout, T. Gronier



**To launch a simulation:**
1) Creation of data catalog(s)
2) Creation of environment(s): associated with a data catalog
3) Creation of entities, i.e producers, consumers, etc
4) Association of the entities with environment(s)
5) Creation of data logger(s): write desired results in a file, associated with a data catalog
6) WIP

**Data catalogs**  
Data catalogs are dictionaries associated with an environment.
They gather all data for the current time step.
During the simulation step, decisions will be written there.
During the post-processing step, data exported are extracted from catalogs.

**Data loggers**  
Data loggers are a set of functions in charge of the export of results into files. They need 
to know which data has to be extracted, to which file and with which frequency.

**Entities**  
Entities represent the different systems acting on the grid. It corresponds to consumers, 
producers, storing devices and converters. For each type of entities sub-types can be defined.
Specific rules and behaviors can be associated with each sub-type. For example, photovoltaic 
panels and wind turbines are sub-types of consumers with different attributes : photovoltaic 
panels depend on solar irradation meanwhile wind turbines depend on wind velocity. 

**Environment**  
Environments contain entities, potentially sub-environments, and link them with a data catalog 
and a strategy.

**Supervizor**  
The supervizor is a function which job is to perform the simulation. It updates the data, 
applies the strategy and calls data loggers and daemons for each step.

**Daemons**  
Daemons are functions with a secondary role. They are in charge of irregular operations 
such as ...
