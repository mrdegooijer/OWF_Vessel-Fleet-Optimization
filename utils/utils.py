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