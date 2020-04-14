# This case checks if the daemons simulating meteo work correctly.

# ##############################################################################################
# Importations
from datetime import datetime

from src.common.World import World

from src.tools.SubclassesDictionary import get_subclasses

from cases.ValidationCases.Utilities import *

from json import load


# ##############################################################################################
# Minimum
# the following objects are necessary for the simulation to be performed
# you need exactly one object of each type
# ##############################################################################################


# ##############################################################################################
# Importation of subclasses
# all the subclasses are imported in the following dictionary
subclasses_dictionary = get_subclasses()


# ##############################################################################################
# Creation of the world
# a world contains all the other elements of the model
# a world needs just a name
name_world = "Disc World"
world = World(name_world)  # creation


# ##############################################################################################
# Definition of the path to the files
pathExport = "cases/ValidationCases/Results"
world.set_directory(pathExport)


# ##############################################################################################
# Definition of the random seed
# The default seed is the current time (the value returned by datetime.now())
world.set_random_seed("tournesol")


# ##############################################################################################
# Time parameters
# it needs a start date, the value of an iteration in hours and the total number of iterations
start_date = datetime.now()  # a start date in the datetime format
start_date = start_date.replace(year=2019, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
world.set_time(start_date,  # time management: start date
               1,  # value of a time step (in hours)
               24*365)  # number of time steps simulated

# ##############################################################################################
# Model
# the following objects are the one describing the case studied
# you need at least one local grid and one agent to create a device
# no matter the type, you can create as much objects as you want
# ##############################################################################################

# ##############################################################################################
# Daemon
# this object updates values of the catalog not taken in charge by anyone else

# Indoor temperature
# this daemon is responsible for the value of indoor temperatures in the catalog
# indoor_temperature_daemon = subclasses_dictionary["Daemon"]["IndoorTemperatureDaemon"]()

# Outdoor temperature
# this daemon is responsible for the value of outside temperature in the catalog
outdoor_temperature_daemon = subclasses_dictionary["Daemon"]["OutdoorTemperatureDaemon"]({"location": "Pau"})

# Water temperature
# this daemon is responsible for the value of the water temperature in the catalog
water_temperature_daemon = subclasses_dictionary["Daemon"]["ColdWaterDaemon"]({"location": "Pau"})

# Irradiation
# this daemon is responsible for updating the value of raw solar irradiation
irradiation_daemon = subclasses_dictionary["Daemon"]["IrradiationDaemon"]({"location": "Pau"})

# Wind
# this daemon is responsible for updating the value of raw solar Wind
wind_daemon = subclasses_dictionary["Daemon"]["WindDaemon"]({"location": "Pau"})


# ##############################################################################################
# Daemon of validation
# This daemon evaluates if the simulation value is equal to the reference values
# they take 4 parameters: the description of what is validated, the keys it has to validate, the reference values and the name of the file where data is stored
description = "This daemon validates the values of the meteo-related daemons."

filename = "meteo.txt"

### reference values
# outdoor temperatures
file = open("lib/Subclasses/Daemon/OutdoorTemperatureDaemon/TemperatureProfiles.json", "r")
data = load(file)["Pau"]  # load the JSON format
# current outdoor temperatures
current_outdoor_temperature_values = data["temperatures"]
current_outdoor_temperature_values = format_day_per_month_to_year(current_outdoor_temperature_values)  # modify the list to have 8760h/year
# exergy reference_temperatures
reference_temperature_values = data["exergy_reference_temperatures"]
reference_temperature_values = format_value_per_month_to_year(reference_temperature_values)  # modify the list to have 8760h/year
file.close()

# cold water temperature
file = open("lib/Subclasses/Daemon/ColdWaterDaemon/TemperatureProfiles.json", "r")
data = load(file)["Pau"]  # load the JSON format
cold_water_values = data["temperatures"]
cold_water_values = format_value_per_month_to_year(cold_water_values)  # modify the list to have 8760h/year
file.close()

# irradiation values
file = open("lib/Subclasses/Daemon/IrradiationDaemon/IrradiationProfiles.json", "r")
data = load(file)["Pau"]  # load the JSON format
irradiation_values = data["irradiation"]
irradiation_values = format_hours_per_month_to_year(irradiation_values)  # modify the list to have 8760h/year
file.close()

# wind speed values
file = open("lib/Subclasses/Daemon/WindDaemon/WindProfiles.json", "r")
data = load(file)["Pau"]
file.close()
wind_values = data["wind_speed"]
wind_values = format_day_per_month_to_year(wind_values)

reference_values = {"Pau.current_outdoor_temperature": current_outdoor_temperature_values,
                    "Pau.reference_temperature": reference_temperature_values,
                    "Pau.cold_water_temperature": cold_water_values,
                    "Pau.irradiation_value": irradiation_values,
                    "Pau.wind_value": wind_values}

parameters = {"description": description, "reference_values": reference_values, "filename": filename}

validation_daemon = subclasses_dictionary["Daemon"]["ValidationDaemon"]("meteo_related_daemons", parameters)


# ##############################################################################################
# simulation
world.start()

# ##############################################################################################
# Validation






