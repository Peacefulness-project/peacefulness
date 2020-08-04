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

    with open("../../lib/Subclasses/Daemon/WindDaemon/RandomizedWindProfiles.json", 'w') as outfile:
        dump(generated_wind_daemon, outfile)

#windgenerator("Pau_Alois", 2, 0.5)