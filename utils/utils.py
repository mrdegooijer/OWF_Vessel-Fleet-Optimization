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
    bundle = []
    for i in range(4):
        bundle.append(list(itertools.product(tasks, repeat=i + 1)))
    bundles = [j for sub in bundle for j in sub]
    return bundles

def unpack_sets(sets):
    """
    Unpack the sets dictionary into individual variables
    :param sets: Sets dictionary
    :return: Unpacked variables
    """
    bases = sets['bases']
    vessels = sets['vessels']
    periods = sets['periods']
    charter_periods = sets['charter_periods']
    tasks = sets['tasks']
    vessel_task_compatibility = sets['vessel_task_compatibility']
    prev_tasks = sets['prev_tasks']
    corr_tasks = sets['corr_tasks']
    planned_prev_tasks = sets['planned_prev_tasks']
    planned_corr_tasks = sets['planned_corr_tasks']
    bundles = sets['bundles']
    weather_availability_per_vessel = sets['weather_availability_per_vessel']

    return (bases, vessels, periods, charter_periods, tasks, vessel_task_compatibility,
            prev_tasks, corr_tasks, planned_prev_tasks, planned_corr_tasks, bundles,
            weather_availability_per_vessel)

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

    return (cost_base_operation, cost_vessel_purchase, cost_vessel_charter,
            cost_vessel_operation, cost_technicians, cost_downtime,
            penalty_preventive_late, penalty_not_performed, vessel_speed,
            transfer_time, max_time_offshore, max_vessels_available_charter,
            distance_base_OWF, technicians_available, capacity_base_for_vessels,
            capacity_vessel_for_technicians, failure_rate, time_to_perform_task,
            technicians_required_task, latest_period_to_perform_task,
            tasks_in_bundles, technicians_required_bundle)

def unpack_variables(vars):
    """
    Unpack the variables dictionary into individual variables
    :param vars: Variables dictionary
    :return: Unpacked variables
    """
    base_use = vars['base_use']
    purchased_vessels = vars['purchased_vessels']
    chartered_vessels = vars['chartered_vessels']
    task_performance = vars['task_performance']
    bundle_performance = vars['bundle_performance']
    tasks_late = vars['tasks_late']
    tasks_not_performed = vars['tasks_not_performed']
    periods_late = vars['periods_late']
    hours_spent = vars['hours_spent']

    return (base_use, purchased_vessels, chartered_vessels, task_performance,
            bundle_performance, tasks_late, tasks_not_performed,
            periods_late, hours_spent)