
def get_1_day_per_month(values, catalog):  # this methods is here to get the temperature when the format is 1 day/month
    current_hour = catalog.get("physical_time").hour  # the current hour of the day
    current_month = str(catalog.get("physical_time").month)  # the current month in the year

    return values[current_month][current_hour]  # return the appropriate outdoor temperature for the current moment

def get_365_days(values, catalog):
    moment = catalog.get("physical_time")
    year = moment.year
    duration = moment - datetime(year=year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    current_hour = duration.days * 24 + duration.seconds // 3600  # conversion of the duration in hours spent since the beginning of the year

    return values[current_hour]

def get_each_hour_per_month(values, catalog):  # this methods is here to get the irradiation when the format is 1 day/month
    month = catalog.get("physical_time").month  # the month corresponding to the irradiation
    day = catalog.get("physical_time").day - 1  # the "- 1" is necessary because python indexation begins at 0 and day at 1
    hour = catalog.get("physical_time").hour

    return values[str(month)][24 * day + hour]

def get_1_values_per_month(values, catalog):  # this methods is here to get the temperature when the format is 1 day/month
    month = catalog.get("physical_time").month  # the month corresponding to the temperature

    return values[str(month)]

def get_1_day_per_year(values, catalog):
    hour = (catalog.get("physical_time").hour+1) % 24

    return values[hour]