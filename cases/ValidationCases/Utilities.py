# Utilities functions for validation cases


def format_day_per_month_to_year(data):  # to pass 24h/month => 8760h/year
    data = sum([data["1"] for i in range(31)], []) \
         + sum([data["2"] for i in range(28)], []) \
         + sum([data["3"] for i in range(31)], []) \
         + sum([data["4"] for i in range(30)], []) \
         + sum([data["5"] for i in range(31)], []) \
         + sum([data["6"] for i in range(30)], []) \
         + sum([data["7"] for i in range(31)], []) \
         + sum([data["8"] for i in range(31)], []) \
         + sum([data["9"] for i in range(30)], []) \
         + sum([data["10"] for i in range(31)], []) \
         + sum([data["11"] for i in range(30)], []) \
         + sum([data["12"] for i in range(31)], [])

    return data


def format_value_per_month_to_year(data):  # to pass 1 value/month => 8760h/year
    data = [data["1"] for i in range(31*24)] \
         + [data["2"] for i in range(28*24)] \
         + [data["3"] for i in range(31*24)] \
         + [data["4"] for i in range(30*24)] \
         + [data["5"] for i in range(31*24)] \
         + [data["6"] for i in range(30*24)] \
         + [data["7"] for i in range(31*24)] \
         + [data["8"] for i in range(31*24)] \
         + [data["9"] for i in range(30*24)] \
         + [data["10"] for i in range(31*24)] \
         + [data["11"] for i in range(30*24)] \
         + [data["12"] for i in range(31*24)]

    return data


def format_hours_per_month_to_year(data):  # to pass all hours/month => 8760h/year
    data = data["1"] \
         + data["2"]\
         + data["3"] \
         + data["4"] \
         + data["5"] \
         + data["6"] \
         + data["7"] \
         + data["8"] \
         + data["9"] \
         + data["10"] \
         + data["11"]\
         + data["12"]

    return data


