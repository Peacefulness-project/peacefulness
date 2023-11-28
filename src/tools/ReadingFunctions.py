from datetime import datetime, timedelta


def get_1_day_per_month(values, catalog, time_offset=0):  # this methods is here to get the temperature when the format is 1 day/month
    physical_time = catalog.get("physical_time") + timedelta(time_offset/24)  # this allows to get previous or next values of the data
    current_hour = physical_time.hour  # the current hour of the day
    current_month = str(physical_time.month)  # the current month in the year

    return values[current_month][current_hour]  # return the appropriate outdoor temperature for the current moment


def get_365_days(values, catalog, time_offset=0):
    physical_time = catalog.get("physical_time") + timedelta(time_offset/24)  # this allows to get previous or next values of the data
    year = physical_time.year
    duration = physical_time - datetime(year=year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    current_hour = duration.days * 24 + duration.seconds // 3600  # conversion of the duration in hours spent since the beginning of the year

    return values[current_hour]


def get_non_periodic_values(values, catalog, time_offset=0):
    physical_time = catalog.get("physical_time") + timedelta(time_offset/24)  # this allows to get previous or next values of the data
    current_datetime = str(physical_time)
    return values[current_datetime]


def get_each_hour_per_month(values, catalog, time_offset=0):  # this methods is here to get the irradiation when the format is 1 day/month
    physical_time = catalog.get("physical_time") + timedelta(time_offset/24)  # this allows to get previous or next values of the data
    month = physical_time.month  # the current month
    day = physical_time.day - 1  # the "- 1" is necessary because python indexation begins at 0 and day at 1
    hour = physical_time.hour
    print("plop")

    return values[str(month)][24 * day + hour]


def get_1_values_per_month(values, catalog, time_offset=0):  # this methods is here to get the temperature when the format is 1 day/month
    physical_time = catalog.get("physical_time") + timedelta(time_offset/24)  # this allows to get previous or next values of the data
    month = physical_time.month  # the current month

    return values[str(month)]


def get_1_day_per_year(values, catalog, time_offset=0):
    physical_time = catalog.get("physical_time") + timedelta(time_offset/24)  # this allows to get previous or next values of the data
    hour = physical_time.hour % 24

    return values[hour]


reading_functions = {
                     "day/month": get_1_day_per_month,  # 1 day in a month
                     "365days": get_365_days,  # every days in a year, hour by hour
                     "non_periodic": get_non_periodic_values,  # each value is associated to a precise datetime, which must match the ones encountered in the simulation
                     "each_hour/month": get_each_hour_per_month,  # every hours in a month
                     "1/month": get_1_values_per_month,  # 1 representative value for each month
                     "1day/year": get_1_day_per_year,  # 1 representative day, hour by hour, for each month
                     }



