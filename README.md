#                                               PEACEFULNESS
           Platform for transverse evaluation of control strategies for multi-energy smart grids
Coordinators: Dr E. Franquet, Dr S. Gibout (erwin.franquet@univ-pau.fr, stephane.gibout@univ-pau.fr)
Contributors (alphabetical order): Dr E. Franquet, Dr S. Gibout, T. Gronier


## Presentation

PEACEFULNESS is a program designed to perform real-time management of energy grids. Its main principle is its ability to act at the scale of devices, by two means: by delaying the beginning of devices(dishwashers, washing machines,...) or by modulating the power given to them (heating or HVAC). Furthermore, it integrates the notion of contracts: according to the contract they have, consumers and producers are not managed the same way by the supervisor.
It is able to simulate different energies at the same time and to manage interactions between them.


## Main features
PEACEFULNESS is able to simulate **multi-energy grids**, including **several thousands of consumers or producers** each with its **several devices** and its **own contracts**. Moreover, **different strategies of supervision** are available.

![Grid representation](https://user-images.githubusercontent.com/45936732/75159325-38ae4c80-5718-11ea-98f9-b57c86dd9d43.png)

## Code general philosophy
PEACEFULNESS is written in **Python** and is [object-oriented](https://en.wikipedia.org/wiki/Object-oriented_programming): it means that the main entities in relation (devices, consumers/producers, supervisors, etc) are modeled as separated [classes](https://github.com/GAP4HS3/code-one/wiki/Classes), each class being defined by its attributes (its characteristics) and its methods (the actions it performs).

That being said, some classes gather elements whose behaviors are very different: devices, supervisors, daemons, contracts and dataloggers. When it is the case, we create sub-classes: while being identical from the outside, their methods can vary greatly from one subclass to another. The advantage of such an organization is to facilitate the addition of new classes.

Let's take the example of a PV field: like all devices, a PV field has to inform the supervisor of the quantity of energy it produces. Meanwhile, the calculation of this quantity is specific to PV panels.

Then, creating a case consists essentially in creating different elements of the different classes in a predefined-order.

Details of what is happening during the resolution can be found [here](https://github.com/GAP4HS3/code-one/wiki/Progress-of-a-round).