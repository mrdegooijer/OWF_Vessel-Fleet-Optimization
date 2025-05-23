import pandas as pd
import numpy as np
import itertools

def load_input_data(file_path):
    """
    Load input data from a file

    :param file_path: Path to the input data file
    :return: DataFrame with input data
    """

    data = pd.read_excel(file_path, sheet_name=None)
    data['task_compatibility'] = pd.read_excel(file_path, sheet_name='task_compatibility', index_col=0)
    # data['tasks'] = pd.read_excel(file_path, sheet_name='tasks', index_col=0)
    return data


def generate_corrective_maintenance_tasks(corr_tasks, periods, turbines, input_tasks):

    daily_failures = pd.DataFrame(index=corr_tasks, columns=periods)
    failures = {}
    for m in corr_tasks:
        for p in periods:
            failures[p] = np.random.uniform(size=turbines)  # uniform distribution of the failures
            daily_failures.loc[m, p] = sum(x < input_tasks.loc[m, 'failure_rate'] / len(periods) for x in failures[p])

    return daily_failures


def generate_task_bundles(tasks):
    bundle_dict = {}
    bundle_id = 1
    for i in range(1, 5):  # bundle sizes 1 to 4
        for combo in itertools.product(tasks, repeat=i):
            bundle_name = f'K{bundle_id}'
            bundle_dict[bundle_name] = combo
            bundle_id += 1
    return bundle_dict


def unpack_sets(sets):
    """
    Unpack the sets dictionary into individual variables
    :param sets: Sets dictionary
    :return: Unpacked variables
    """
    bases = sets['bases']
    vessels = sets['vessels']
    periods = sets['periods']
    charter_dict = sets['charter_dict']
    charter_periods = sets['charter_periods']
    tasks = sets['tasks']
    vessel_task_compatibility = sets['vessel_task_compatibility']
    prev_tasks = sets['prev_tasks']
    corr_tasks = sets['corr_tasks']
    planned_prev_tasks = sets['planned_prev_tasks']
    planned_corr_tasks = sets['planned_corr_tasks']
    bundle_dict = sets['bundle_dict']
    bundles = sets['bundles']
    spare_parts = sets['spare_parts']

    return (bases, vessels, periods, charter_dict, charter_periods, tasks, vessel_task_compatibility,
            prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundle_dict, bundles, spare_parts)

def unpack_parameters(params):
    """
    Unpack the parameters dictionary into individual variables
    :param params: Parameters dictionary
    :return: Unpacked variables
    """
    cost_base_operation = params['cost_base_operation']
    cost_vessel_purchase = params['cost_vessel_purchase']
    cost_vessel_charter = params['cost_vessel_charter']
    cost_vessel_operation = params['cost_vessel_operation']
    cost_technicians = params['cost_technicians']
    cost_downtime = params['cost_downtime']
    penalty_preventive_late = params['penalty_preventive_late']
    penalty_not_performed = params['penalty_not_performed']
    vessel_speed = params['vessel_speed']
    transfer_time = params['transfer_time']
    max_time_offshore = params['max_time_offshore']
    max_vessels_available_charter = params['max_vessels_available_charter']
    distance_base_OWF = params['distance_base_OWF']
    technicians_available = params['technicians_available']
    capacity_base_for_vessels = params['capacity_base_for_vessels']
    capacity_vessel_for_technicians = params['capacity_vessel_for_technicians']
    failure_rate = params['failure_rate']
    time_to_perform_task = params['time_to_perform_task']
    technicians_required_task = params['technicians_required_task']
    latest_period_to_perform_task = params['latest_period_to_perform_task']
    tasks_in_bundles = params['tasks_in_bundles']
    technicians_required_bundle = params['technicians_required_bundle']
    weather_max_time_offshore = params['weather_max_time_offshore']

    return (cost_base_operation, cost_vessel_purchase, cost_vessel_charter,
            cost_vessel_operation, cost_technicians, cost_downtime,
            penalty_preventive_late, penalty_not_performed, vessel_speed,
            transfer_time, max_time_offshore, max_vessels_available_charter,
            distance_base_OWF, technicians_available, capacity_base_for_vessels,
            capacity_vessel_for_technicians, failure_rate, time_to_perform_task,
            technicians_required_task, latest_period_to_perform_task,
            tasks_in_bundles, technicians_required_bundle, weather_max_time_offshore)

def unpack_variables(vars):
    """
    Unpack the variables dictionary into individual variables
    :param vars: Variables dictionary
    :return: Unpacked variables
    """
    base_use = vars['base_use']
    purchased_vessels = vars['purchased_vessels']
    chartered_vessels = vars['chartered_vessels']
    task_performed = vars['task_performed']
    bundle_performed = vars['bundle_performed']
    tasks_late = vars['tasks_late']
    tasks_not_performed = vars['tasks_not_performed']
    periods_late = vars['periods_late']
    hours_spent = vars['hours_spent']

    return (base_use, purchased_vessels, chartered_vessels, task_performed,
            bundle_performed, tasks_late, tasks_not_performed,
            periods_late, hours_spent)

def return_charter_period(p, charter_dict):
    """
    Return the charter period for a given period
    :param p: Period
    :param charter_dict: Charter periods
    :return: Charter period
    """
    for idx, period in enumerate(charter_dict):
        if p in period:
            return idx + 1

def generate_weather_set(year):
    """
    Generates the weather set for the project.

    :param year
    :return: K
    """
    file_path = 'data/weatherconditions.xlsx'

    if year == 2004:
        weather = pd.read_excel(file_path, nrows=8783, usecols=['Year', 'Month', 'Day', 'Hour', 'Wind Speed', 'Wave Height'])
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

def generate_availability_set(vessels, periods, year, data):
    df_weather = generate_weather_set(year)

    weather_max_time_offshore = {}

    for v in vessels:
        for p in periods:
            if p == 1:
                hours_available = sum(df_weather.loc[i, 'Wave Height'] < data['vessels'].loc[v, 'Hslimit'] for i in range(0, 23))
            else:
                hours_available = sum(df_weather.loc[i, 'Wave Height'] < data['vessels'].loc[v, 'Hslimit'] for i in range((24*p-25), (24*p-1)))
            weather_max_time_offshore[v, p] = hours_available

    return weather_max_time_offshore

def generate_downtime_cost(periods, year):
    df_windpower = pd.read_excel('data/windpower.xlsx', usecols=['Wind speed', 'Power'])
    df_weather = generate_weather_set((year))

    cost_downtime = {}
    for p in periods:
        if p == 1:
            cost_downtime[p] = (90/1000) * df_windpower.loc[np.where(df_windpower['Wind speed'] == round(
                sum(df_weather.loc[i, 'Wind Speed'] for i in range(0, 23))/23)), 'Power'].values[0]
        else:
            cost_downtime[p] = (90 / 1000) * df_windpower.loc[np.where(df_windpower['Wind speed'] == round(
                sum(df_weather.loc[i, 'Wind Speed'] for i in range((24*p-25), (24*p-1))) / 24)), 'Power'].values[0]

    return cost_downtime