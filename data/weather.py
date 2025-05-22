import pandas as pd

file_path = 'weatherconditions.xlsx'

def generate_weather_set(year):
    """
    Generates the weather set for the project.

    :param year
    :return: K
    """

    if year == 2004:
        weather = pd.read_excel(file_path, nrows=878, usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
    elif year == 2005:
        weather = pd.read_excel(file_path, nrows=8760, skiprows=range(1, 8784),
                                usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
    elif year == 2006:
        weather = pd.read_excel(file_path, nrows=8760, skiprows=range(1, 17544),
                                usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
    elif year == 2007:
        weather = pd.read_excel(file_path, nrows=8760, skiprows=range(1, 26304),
                                usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
    elif year == 2008:
        weather = pd.read_excel(file_path, nrows=8784, skiprows=range(1, 35064),
                                usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
    elif year == 2009:
        weather = pd.read_excel(file_path, nrows=8760, skiprows=range(1, 43848),
                                usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
    elif year == 2010:
        weather = pd.read_excel(file_path, nrows=8760, skiprows=range(1, 52608),
                                usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
    elif year == 2011:
        weather = pd.read_excel(file_path, nrows=8784, skiprows=range(1, 61368),
                                usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])

    return weather

def generate_availability_set(vessels, periods, weather):
    # wind speed and power
    wind = pd.read_excel('windpower.xlsx', usecols=['Wind speed', 'Power'])

    # weather conditions
    hours_available = {}
    for v in V:
        for p in P:
            if p == 1:
                x = sum(W_p.loc[i, 'Wave Height'] < W_v_V)
    return A
