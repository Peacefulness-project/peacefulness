from math import sqrt
from numpy.random import normal
from json import load, dump


def windgenerator(location, standard_deviation, correlation_factor):
    file = open("../../lib/Subclasses/Daemon/WindDaemon/WindProfiles.json", "r")
    data = load(file)[location]
    file.close()

    generated_wind_daemon = {}

    randomized_wind_profile = {}
    randomized_wind_profile["height_ref"] = data["height_ref"]
    randomized_wind_profile["format"] = "each_minutes/month"

    wind = {}

    for month in data["wind_speed"]:
        w = []
        hour = 0
        for wind_hour in data["wind_speed"][month]:
            w.append(hour)

            for i in range(59):
                new_w = max(0, correlation_factor * w[i + 60 * hour] + (1 - correlation_factor) * normal(wind_hour,
                                                                                                         standard_deviation * sqrt(
                                                                                                             1 - correlation_factor ** 2)))
                w.append(new_w)

            hour += 1

        wind[month] = w

    randomized_wind_profile["wind_speed"] = wind

    generated_wind_daemon[location] = randomized_wind_profile

    name = "../../lib/Subclasses/Daemon/WindDaemon/WindProfiles_" + str(standard_deviation) + "_" + str(correlation_factor) + ".json"

    with open(name, 'w') as outfile:
        dump(generated_wind_daemon, outfile)

#windgenerator("Pau_Alois", 2, 0.001)



def autoregressiveprofilesgenerator(standard_deviation, correlation_factor, location, daemon, key, key2 = None):
    file = open("../../lib/Subclasses/Daemon/" + str(daemon) + "Daemon/" + str(daemon) + "Profiles.json", "r")
    data = load(file)[location]
    file.close()

    generated_daemon = {}

    randomized_profile = {}

    for ref in data:
        if ref == "format":

            randomized_profile["format"] = "each_minutes/month"

        elif ref == key or ref == key2:
            values = {}
            for month in data[ref]:
                w = []
                hour = 0
                for values_hour in data[ref][month]:
                    w.append(values_hour)
                    for i in range(59):
                        new_w = max(0, correlation_factor * w[i + 60 * hour] + (1 - correlation_factor) * normal(values_hour,
                                                                                                                 standard_deviation * sqrt(
                                                                                                             1 - correlation_factor ** 2)))
                        w.append(new_w)
                    hour += 1
                values[month] = w
            randomized_profile[ref] = values

        else:
            randomized_profile[ref] = data[ref]

    generated_daemon[location] = randomized_profile

    name = "../../lib/Subclasses/Daemon/" + str(daemon) + "Daemon/" + str(daemon) + "Profiles_" + str(standard_deviation) + "_" + str(correlation_factor) + ".json"

    with open(name, 'w') as outfile:
        dump(generated_daemon, outfile)


autoregressiveprofilesgenerator(2, 0.1, "Lyon", "Irradiation", "total_irradiation", "direct_normal_irradiation")